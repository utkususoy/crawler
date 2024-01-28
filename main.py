import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse
import string
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class UrlScraper:
    def __init__(self):
        #self.source_url = source_url
        self.driver = None
        self.html_body = None
        self.html_content = None
        self.parsed_source_url = None
        self.soup_obj = None
        self.anchor_tags = None
        self.non_article_url_endpoints = None
        self.selenium_wait_timeout = 10
        self.searchable_parent_level = 3
        self.searchable_child_depth = 3
        self.min_text_length = 2 #TODO: 3 yap
        self.selected_pattern_boundary = 3
        self.url_indicator_list = ["news", "content", "title", "post", "article", "story"]  # , "headline", "heading", "text"
        self.non_url_indicator_list = ["privacy", "policy", "cookie", "advertise"]
        self.redundant_html_parts = ["header", "footer", "head"] #TODO: ekle dene, "img", "figure", nav ekle
        self.rejected_urls = set()
        self.accepted_urls = set()
        self._url_list_by_article_tag = []
        self._url_list_a_tag_attributes = []
        self.__build()

    def __build(self):
        self.driver = self.__build_driver()

    def __build_html(self, source_url):
        self.html_content = self.get_html_with_selenium(source_url=source_url)  # dependent on self.driver
        self.soup_obj = self.purify_redundant_html_parts()  # self.html_content
        self.anchor_tags = self.soup_obj.find_all('a')  # independent
        self.non_article_url_endpoints = ["#", "/", "privacy-policy/", "javascript:void(0);"]
        self.parsed_source_url = self.parse_url(news_url=source_url)
        self.extend_non_article_url_endpoints(urls=self.non_article_url_endpoints.copy())
        self._url_list_by_article_tag = []
        self._url_list_a_tag_attributes = []


        #TODO: remove '#' and '/' and url-domain, başına jhttp ve https versiyonlarınıda ekle
        #TODO: keyword configurable yap.

    def extend_non_article_url_endpoints(self, urls):
        for endpoint in urls:
            if endpoint[-1] == '/':
                domain_non_endpoint = self.parsed_source_url['domain'] + endpoint
            else:
                domain_non_endpoint = self.parsed_source_url['domain'] + '/' + endpoint
            self.non_article_url_endpoints.append(domain_non_endpoint)

    def parse_url(self, news_url):
        parsed_url = urlparse(news_url)
        domain = parsed_url.netloc
        endpoint = parsed_url.path
        domain and self.non_article_url_endpoints.append(domain)
        return {"domain": domain, "endpoint": endpoint}

    def __build_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def get_html_with_selenium(self, source_url):
        try:

            #driver.get("https://stackoverflow.com/questions/28431765/open-web-in-new-tab-selenium-python")

            # print(self.selenium_wait_timeout)
            # driver.switch_to.new_window() #new-tab options
            self.driver.get(source_url) #new-tab options
            WebDriverWait(self.driver, self.selenium_wait_timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
            # driver.window_handles[1]
            # driver.close() #new-tab options
            # time.sleep(3) #new-tab options
            html_code = self.driver.page_source
            #driver.quit()

            return html_code
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_html(self, url_, timeout=10, max_retries=3):
        retries = 0
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",

            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.google.com/",
            # Referer header to make it look like you came from a search engine
        }
        response = requests.get(url_, headers=headers, timeout=timeout)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Error: Unable to fetch content. Status code: {response.status_code}")
            html_content = self.get_html_with_selenium(url_=url_)
            return html_content


    def find_matching_words(self, text, subwords):
        pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, subwords)) + r')\w*\b|\w*(?:' + '|'.join(map(re.escape, subwords)) + r')\w*', flags=re.IGNORECASE)
        matches = pattern.findall(text)
        return matches

    def remove_punctuation(self, text):
        translator = str.maketrans('', '', string.punctuation)
        text_without_punctuation = text.translate(translator)
        return text_without_punctuation

    #TODO: punc disable edildi kontrol et. farklarına bak not et
    def check_hyperlink_texts(self, hyperlink_tag):
        a_tag_text = ''.join(hyperlink_tag.find_all(string=True, recursive=False))
        text_of_hyperlink = a_tag_text.strip()
        if text_of_hyperlink:
            if len(text_of_hyperlink.split()) > self.min_text_length: # alternatif olarak url-endpatinde keyword search yap.
                if hyperlink_tag['href'] in self.rejected_urls: self.rejected_urls.remove(hyperlink_tag['href'])
                return True
        elif 'title' in hyperlink_tag.attrs:
            text_of_hyperlink = hyperlink_tag['title'].strip()
            if len(text_of_hyperlink.split()) > self.min_text_length:
                return True
        else:
            if self.check_child_tags(hyperlink_tag=hyperlink_tag):
                return True
        self.rejected_urls.add(hyperlink_tag['href'])
        return False

    def check_child_tags(self, hyperlink_tag):
        immediate_children = hyperlink_tag
        for i in range(0, self.searchable_child_depth):
            try:
                immediate_childrens = immediate_children.find_all(recursive=False)
            except AttributeError as e:
                self.rejected_urls.add(hyperlink_tag['href'])
                return False
            if not immediate_childrens: return False
            for immediate_children in immediate_childrens:
                text_of_child = immediate_children.text.strip()
                if text_of_child and (len(text_of_child.split()) > self.min_text_length):
                    return True
                # return False
        self.rejected_urls.add(hyperlink_tag['href'])
        return False

    def url_formatter(self, article_url):
        if 'http' in article_url:
            return article_url
        else:
            http_article_url = 'https://' + self.parsed_source_url['domain'] + article_url
            return http_article_url

    def get_unique_hyperlink_tags(self, hyperlik_tags):
        valid_anchor_tags = set()
        for hyperlink_tag in hyperlik_tags:
            if 'href' in hyperlink_tag.attrs: #and (hyperlink_tag['href'] not in valid_anchor_urls)
                valid_anchor_tags.add(hyperlink_tag)
        return valid_anchor_tags

    def check_parent_tags(self, hyperlink_tag):
        immediate_parent = hyperlink_tag
        if not self.html_element_attribute_searching(html_tag=hyperlink_tag):
            self.rejected_urls.add(hyperlink_tag['href'])
            return False
        for i in range(0, self.searchable_parent_level):
            immediate_parent = immediate_parent.find_parent()
            if not self.html_element_attribute_searching(html_tag=immediate_parent):
                self.rejected_urls.add(hyperlink_tag['href'])
                return False
        return True

    def html_element_attribute_searching(self, html_tag):
        if html_tag.attrs:
            for attr_key, attr_value in html_tag.attrs.items():
                if attr_key == 'href' or attr_key == 'title':
                    continue
                # non-article-url elimination based on html-tag attributes
                if bool(self.find_matching_words(text=" ".join(attr_value), subwords=self.non_url_indicator_list)):
                    return False
        return True

    #TODO: media url'lerini sil.
    def html_structural_pattern_search(self):
        html_structural_patterns = []

        extracted_tags = [a_tag for a_tag in self.soup_obj.find_all('a')]
        print(f"Found {len(extracted_tags)} Urls.")
        unique_hyperlink_tags = self.get_unique_hyperlink_tags(hyperlik_tags=extracted_tags)
        print(f"Found {len(unique_hyperlink_tags)} Unique Urls.")

        for hyper_link_tag in unique_hyperlink_tags:
            article_html_structure = {
                "vote": 1,
                "element_order": None,
                "hyperlink_tags": [],
                "urls": set()
            }
            element_order = []
            html_element = hyper_link_tag
            for i in range(0, 3):
                element_order.append(self.html_name_class_mapper(html_element.name))
                html_element = html_element.find_parent()
            article_html_structure['element_order'] = element_order
            article_html_structure['hyperlink_tags'].append(hyper_link_tag)
            article_html_structure['urls'].add(hyper_link_tag['href'])

            if self.check_hyperlink_texts(hyperlink_tag=hyper_link_tag) and \
                    self.check_parent_tags(hyperlink_tag=hyper_link_tag) and \
                    (hyper_link_tag['href'] not in self.non_article_url_endpoints):
                self.process_dicts(html_structural_patterns=html_structural_patterns,
                                   new_pattern=article_html_structure)

        return html_structural_patterns

    def process_dicts(self, html_structural_patterns, new_pattern):
        for html_pattern in html_structural_patterns:
            if html_pattern["element_order"] == new_pattern["element_order"]: # and new_pattern["element_order"] != ["link", "list", "list"]
                html_pattern["vote"] += 1
                html_pattern["hyperlink_tags"].append(new_pattern['hyperlink_tags'][0])
                html_pattern["urls"].update(new_pattern['urls'])
                return
        html_structural_patterns.append(new_pattern)

    def html_name_class_mapper(self, html_element_name):
        html_classes = {
            "heading": ["h1", "h2", "h3", "h4", "h5", "h6"],
            "text": ["p", "br", "hr", "span", "b"],
            "list": ["ul", "ol", "li", "dl", "dt", "dd"],
            "link": ["a", "link"],
            "meta": ["head", "meta"],
            "table": ["table", "tr", "td"],
            "media": ["img", "audio", "video"],
            "form": ["form", "input", "button", "label", "select", "textarea"],
            "container": ["div", "header", "footer", "nav", "main", "article", "section", "aside", "figure",
                          "figcaption"]
        }
        for html_class, elements in html_classes.items():
            if html_element_name in elements: return html_class
        return "unknown"

    #TODO: img ve figurelerde find_all yaparak hepsini sil.
    def purify_redundant_html_parts(self):
        soup = BeautifulSoup(self.html_content, 'html5lib')
        for redundant_section in self.redundant_html_parts:
            found_html_section = soup.find(redundant_section)
            if found_html_section:
                found_html_section.extract()

        self.html_body = soup.find('body')
        # print(self.html_body.prettify())
        return soup

    def __to_print(self, pattern_list):
        print("\n---Printing All Found Patterns---\n")
        for i in pattern_list:
            print("Vote: ", i['vote'])
            print("HTML Element Order: ", i['element_order'])
            print("# of Urls: ", len(set(i['urls'])))
            print("Urls: ", set(i['urls']))
            print("\n\n")

    def unknown_main(self, source_url, print_eliminated=False, print_all=False):
        self.__build_html(source_url=source_url)
        article_url_patterns = self.html_structural_pattern_search()
        if print_all:
            self.__to_print(pattern_list=article_url_patterns)
        if print_eliminated:
            print(f"{len(self.rejected_urls)} Eliminated urls: \n", self.rejected_urls)
        return self.get_comprehensive_top_patterns(list_of_article_patterns=article_url_patterns)

    def get_comprehensive_top_patterns(self, list_of_article_patterns):
        list_of_article_patterns = [article_pattern for article_pattern in list_of_article_patterns if article_pattern['vote'] > 3]
        list_of_article_patterns = sorted(list_of_article_patterns, key=lambda pattern: pattern['vote'], reverse=True)

        if len(list_of_article_patterns) > 3:
            list_of_article_patterns = list_of_article_patterns[:self.selected_pattern_boundary]
        comprehensive_results = set().union(*[article_pattern['urls'] for article_pattern in list_of_article_patterns])

        return list(comprehensive_results)

#TODO ***:
# url içerisinde /news/ path i geçiyorsa al. pattern'de farklı bir yere yada set()'e ekle en son most-voted-pattern ile birleştir. (diğer diller içinde ekleme yap.)
# driver'ı dışarden verebil
# add domain prefix

# if __name__ == '__main__':

    # text = "popular-title-link headline-bold"
    # text = "MetaBox-sc-16mpay8-6 hhBlIv o-articleCard__meta"
    # text = "DNNModuleContent ModArticleCSDashboardC"
    # subwords_list = ["sample", "title", "article"]
    #
    # result = url_scraper_obj.find_matching_words(text, url_scraper_obj.url_indicator_list)
    # print(result)