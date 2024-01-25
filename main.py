import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from urllib.parse import urlparse
from itertools import chain
import string
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from xml.etree import ElementTree as ET

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
        self.search_parent_element_threshold = 3
        self.search_child_element_threshold = 3
        self.min_text_length = 3
        self.url_indicator_list = ["news", "content", "title", "post", "article", "story"]  # , "headline", "heading", "text"
        self.non_url_indicator_list = ["privacy", "policy", "cookie", "pay", "ad", "advertise"]
        self.redundant_html_parts = ["header", "footer", "head", "img", "figure"]
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
        self.non_article_url_endpoints = ["#", "/", "privacy-policy/"]
        self.parsed_source_url = self.parse_url(news_url=source_url)
        self.extend_non_article_url_endpoints(urls=self.non_article_url_endpoints.copy())
        self._url_list_by_article_tag = []
        self._url_list_a_tag_attributes = []


        #TODO: remove '#' and '/' and url-domain, başına jhttp ve https versiyonlarınıda ekle
        #TODO: keyword configurable yap.
        #TODO: Selenium new tabte çalıştır.

    def extend_non_article_url_endpoints(self, urls):
        for endpoint in urls:
            print(len(urls))
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
        # chrome_options.add_argument('--headless')
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
            # print(f"Error: Unable to fetch content. Status code: {response.status_code}")
            html_content = self.get_html_with_selenium(url_=url_)
            return html_content


    def find_matching_words(self, text, subwords):
        pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, subwords)) + r')\w*\b|\w*(?:' + '|'.join(map(re.escape, subwords)) + r')\w*', flags=re.IGNORECASE)
        matches = pattern.findall(text)
        return matches

    def find_articles(self, class_name=None, html_element='article'):
        # Parse the HTML content

        # Find <div> elements with the specified class}
        if class_name:
            article_elements = self.soup_obj.find_all(html_element, class_=class_name)
        else:
            article_elements = self.soup_obj.find_all(html_element)

        return article_elements

    def remove_punctuation(self, text):
        translator = str.maketrans('', '', string.punctuation)
        text_without_punctuation = text.translate(translator)
        return text_without_punctuation

    def extract_urls_from_anchor(self, html_element):
        # print("Finding anchor tags")
        extracted_tag = [a_tag for a_tag in html_element.find_all('a')]

        urls = self.find_hyperlinks_url_by_attribute(extracted_tag)
        # print(urls)

        return urls

    #TODO: punc disable edildi kontrol et. farklarına bak not et
    def check_hyperlink_texts(self, hyperlink_tag):
        a_tag_text = ''.join(hyperlink_tag.find_all(string=True, recursive=False))
        text_of_hyperlink = a_tag_text.strip()
        # pure_text_of_hyperlink = (text_of_hyperlink and self.remove_punctuation(
        #     text=text_of_hyperlink)) or ''
        pure_text_of_hyperlink = text_of_hyperlink
        # text control if exist
        # if hyperlink_tag['href'] == "https://www.aa.com.tr/en/world/uk-us-announce-sanctions-to-disrupt-financial-networks-of-hamas/3115721":
        #     print("aaaa")
        if pure_text_of_hyperlink:
            if len(pure_text_of_hyperlink.split()) > self.min_text_length: # alternatif olarak url-endpatinde keyword search yap.
                if hyperlink_tag['href'] in self.rejected_urls: self.rejected_urls.remove(hyperlink_tag['href'])
                return True

            # self.rejected_urls.add(hyperlink_tag)
        #    if hyperlink_tag['href'] not in self.accepted_urls: self.rejected_urls.add(hyperlink_tag['href'])

            # if hyperlink_tag['href'] in self.accepted_urls: self.accepted_urls.remove(hyperlink_tag['href'])
            self.rejected_urls.add(hyperlink_tag['href'])
            return False
        else:
            #if hyperlink_tag['href'] in self.rejected_urls: self.rejected_urls.remove(hyperlink_tag['href'])
            if hyperlink_tag['href'] == "https://www.instagram.com/p/C2XvKEtMtHp/":
                print("heeeeeee")
            if self.check_child_tags(hyperlink_tag=hyperlink_tag):
                return True
            return False
            # Child textine bak.
            ##return False #TODO: kaldır.

    def check_child_tags(self, hyperlink_tag):
        immediate_children = hyperlink_tag
        for i in range(0, self.search_child_element_threshold):
            try:
                immediate_childrens = immediate_children.find_all(recursive=False)
            except AttributeError as e:
                return False
            if not immediate_childrens: return False
            for immediate_children in immediate_childrens:
                text_of_child = immediate_children.text.strip()
                if text_of_child and (len(text_of_child.split()) > self.min_text_length):
                    return True
                # return False
        return False

    def url_formatter(self, article_url):
        if 'http' in article_url:
            return article_url
        else:
            http_article_url = 'https://' + self.parsed_source_url['domain'] + article_url
            return http_article_url

    def html_element_attribute_searching(self, html_tag, hyperlink_tag=None):
        hyperlink_tag = (hyperlink_tag and hyperlink_tag) or html_tag
        if html_tag.attrs:
            for attr_key, attr_value in html_tag.attrs.items():
                # if hyperlink_tag['href'] == "/a/trump-becomes-indignant-in-deposition-video-of-civil-fraud-lawsuit-/7448757.html":
                #     print("found url")
                if attr_key == 'href': continue

                # article-url detection based on tag-attributes
                if bool(self.find_matching_words(text=" ".join(attr_value), subwords=self.url_indicator_list)):
                    # non-article-url elimination
                    if not bool(self.find_matching_words(text=" ".join(attr_value), subwords=self.non_url_indicator_list)):
                        # if self.check_hyperlink_texts(hyperlink_tag=hyperlink_tag):
                        #     if hyperlink_tag['href'] in self.rejected_urls: self.rejected_urls.remove(hyperlink_tag['href'])
                        #     return True
                        # else:
                        #     if hyperlink_tag['href'] not in self.accepted_urls: self.rejected_urls.add(hyperlink_tag['href'])
                        #     return False

                        if hyperlink_tag['href'] in self.rejected_urls: self.rejected_urls.remove(hyperlink_tag['href'])
                        return True
                    else:
                        # print("detected non-article-url indicator in html-element-attributes")
                        # self.rejected_urls.add(hyperlink_tag)
                        if hyperlink_tag['href'] not in self.accepted_urls: self.rejected_urls.add(hyperlink_tag['href'])
                        return False
                else:
                    # print("does not detect any articl-url indicator html-attribute in html-element")
                    continue
                # return False
        else:
            # print("html-element does not have any html-attribute")
            return False

    def get_unique_hyperlink_tags(self, hyperlik_tags):
        print(len(hyperlik_tags))
        valid_anchor_tags = set()
        for hyperlink_tag in hyperlik_tags:
            if 'href' in hyperlink_tag.attrs: #and (hyperlink_tag['href'] not in valid_anchor_urls)
                valid_anchor_tags.add(hyperlink_tag)
        return valid_anchor_tags

    def find_hyperlinks_url_by_attribute(self, hyperlink_tags):
        unique_hyperlink_tags = self.get_unique_hyperlink_tags(hyperlik_tags=hyperlink_tags)
        print(len(unique_hyperlink_tags))

        for hyperlink_tag in unique_hyperlink_tags:
            # hyperlink element attribute searching

            if hyperlink_tag['href'] == "https://www.aa.com.tr/en/energy":
                print("found url")
            if self.html_element_attribute_searching(html_tag=hyperlink_tag):
                hyperlink_tag['href'] not in self.non_article_url_endpoints and self.accepted_urls.add(self.url_formatter(article_url=hyperlink_tag['href']))
                #self.accepted_urls.add(hyperlink_tag['href'])
            if self.check_parent_tags(hyperlink_tag=hyperlink_tag):
                (hyperlink_tag['href'] not in self.non_article_url_endpoints) and (hyperlink_tag['href'] not in self.rejected_urls) and self.accepted_urls.add(self.url_formatter(article_url=hyperlink_tag['href']))
                #(hyperlink_tag['href'] not in self.rejected_urls) and self.accepted_urls.add(hyperlink_tag['href'])
            if self.check_hyperlink_texts(hyperlink_tag=hyperlink_tag):
                (hyperlink_tag['href'] not in self.non_article_url_endpoints) and (hyperlink_tag['href'] not in self.rejected_urls) and self.accepted_urls.add(self.url_formatter(article_url=hyperlink_tag['href']))

            # else:
            #     print("<a/> tag does not include any 'class' or 'title' or parent attribute.")
        return self.accepted_urls

    def check_parent_tags(self, hyperlink_tag):
        # print("Searching parent elements on selected <a/> tag.")
        immediate_parent = hyperlink_tag
        for i in range(0, self.search_parent_element_threshold):
            immediate_parent = immediate_parent.find_parent()
            if self.html_element_attribute_searching(html_tag=immediate_parent, hyperlink_tag=hyperlink_tag):
                return True
        return False

    #TODO: self._url_list_by_article_tag kaldır
    def crawl_article_urls(self):
        article_divs = self.find_articles(html_element="article")
        print(f"Found {len(article_divs)} articles.")
        self._url_list_by_article_tag += list(set(chain(*[self.extract_urls_from_anchor(html_element=article) for article in article_divs]))) #TODO: incele bussinessinsider duplice news-url çekiyor.
   #     self._url_list_by_article_tag.append(chain(*[self.extract_urls_from_anchor(html_element=article) for article in article_divs]))

    def crawler_build(self):
        self.crawl_article_urls()
        self.extract_urls_from_anchor(html_element=self.soup_obj)

    def get_sitemap_urls(self, sitemap_url):
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            return [url.text for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        else:
            print(f"Failed to fetch sitemap from {sitemap_url}")
            return []

    #TODO: media url'lerini sil.
    def html_structural_pattern_search(self):

        html_structural_patterns = []


        parent_dive_threshold = 3

        extracted_tags = [a_tag for a_tag in self.soup_obj.find_all('a')]
        unique_hyperlink_tags = self.get_unique_hyperlink_tags(hyperlik_tags=extracted_tags)
        print(len(unique_hyperlink_tags))


        for hyper_link_tag in unique_hyperlink_tags:
            if hyper_link_tag['href'] == "/news/your-military/2024/01/23/pentagon-can-boost-pay-for-separated-families-to-400-but-hasnt/":
                print("sssss")
            article_html_structure = {
                "vote": 1,
                "element_order": [],
                "hyperlink_tags": [],
                "urls": []
            }
            element_order = []
            html_element = hyper_link_tag
            for i in range(0, 3):
                element_order.append(self.html_name_class_mapper(html_element.name))
                html_element = html_element.find_parent()
            article_html_structure['element_order'] = element_order
            article_html_structure['hyperlink_tags'].append(hyper_link_tag)
            article_html_structure['urls'].append(hyper_link_tag['href'])

            # controll hyperlink texts
            self.check_hyperlink_texts(hyperlink_tag=hyper_link_tag) and self.process_dicts(html_structural_patterns=html_structural_patterns, new_pattern=article_html_structure)

        # print(html_structural_patterns)
        print("\n**********************\n")
        max_voted_dict = max(html_structural_patterns, key=lambda x: x["vote"])
        # print(list(set(max_voted_dict['urls'])))
        # print(len(list(set(max_voted_dict['urls']))))
        # print((max_voted_dict['element_order']))
        print("\n************\n")
        for i in html_structural_patterns:
            print(i['vote'])
            print(i['element_order'])
            print(set(i['urls']))
            print(len(set(i['urls'])))
            print("\n*****\n")


    aaa = {
        "vote": 0,
        "element_order": [],
        "hyperlink_tags": [],
        "urls": []
    }

    def process_dicts(self, html_structural_patterns, new_pattern):
        for html_pattern in html_structural_patterns:
            if html_pattern["element_order"] == new_pattern["element_order"]: # and new_pattern["element_order"] != ["link", "list", "list"]
                html_pattern["vote"] += 1
                html_pattern["hyperlink_tags"].append(new_pattern['hyperlink_tags'][0])
                html_pattern["urls"].append(new_pattern['urls'][0])
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

    def unknown_main(self, source_url):
        self.__build_html(source_url=source_url)
        self.html_structural_pattern_search()





#
#1) *Find <article/>*
# <article> exist:
#   scrape <a/> tags in <article/> tags
#2)
#   scrape all <a/> tags
#   remove media urls by search .jpg or .png .svg endings etc. (regex)
#   valid_url_list_1 = check <a/> tags which contains 'title' attribute then find_pattern_subwords()
#   valid_url_list_2 = check <a/> tags which contains 'class' attribute then find_pattern_subwords()
#   valid_url_list_3 = check <a/> tags parents element (depth can be 2 or 3) then check their 'class' attribute then find_pattern_subwords()
#   valid_url_list_4 = check <a/> tags child elements then check their 'class' attribute then find_pattern_subwords() and try find text in childs.
#   check url with regex
#   check text inside a tag
#   valid_url_list_5 = set(valid_url_lists)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    url = "https://www.navalnews.com/category/naval-news/page/2/" #done, 19 haber recall++
    url = "https://www.navalnews.com/" #done 20 ++
    url = "https://www.navytimes.com/" #done 68 ++
    url = "https://www.navytimes.com/news/pentagon-congress/" #incele
    # url = "https://www.navy.mil/Press-Office/" #
    url = "https://www.navy.mil/Press-Office/Press-Releases/display-pressreleases/Article/3652564/secnav-del-toro-meets-with-key-leaders-during-travel-through-europe/"
    url = "https://www.centcom.mil/MEDIA/NEWS-ARTICLES/" #done +
    url = "https://www.centcom.mil/" #done recall oriented. +
    url = "https://www.dailysabah.com/war-on-terror" # sıkıntı, # ve cookies urllerini discard et.
    url2 = "https://www.military.com/navy" #done, head çıkarıldı #35
    #url = "https://www.businessinsider.com/news" #done, 65 ++
    # url = "https://indianexpress.com/"#done recall+
    #url = "https://www.voanews.com/a/ships-aircraft-search-for-missing-navy-seals-after-mission-to-seize-iranian-missile-parts/7440990.html" #done recall+
    # url = "https://www.defensenews.com/naval/" #done, recall+
    # url = "https://www.defensenews.com/"
    # url = "https://www.navaltoday.com/" #done, 44 recall+
    # url = "https://www.miragenews.com/" #54 Select Top 3 Vote +++

    # url = "https://www.al-monitor.com/" # 31 stv3++
    # url = "https://www.shephardmedia.com/news/naval-warfare/turkish-navy-looks-to-advance-maritime-power-with-2024-fleet-expansion/" #6 news 18 found ++
    # url = "https://www.shephardmedia.com/" #3 news 9 found ++

    #url = "https://www.defenseone.com/"
    # url = "https://www.alhurra.com/" # st3v +++

    # tr news
    # url = "https://www.hurriyetdailynews.com/"  # 69 + st3v +++
    # url = "https://www.aa.com.tr/en/turkiye/turkiye-hosting-eastern-mediterranean-2023-invitation-naval-exercise/3058764"  # news url-indicator dan çıkarıldı

    # gr news
    # url = "https://www.naftikachronika.gr/" #st3v +++
    # url = "https://e-nautilia.gr/" #st3v +++
    # url = "https://www.naftikachronika.gr/latest/" #stv3 +++
    # url = "https://www.naftemporiki.gr/maritime/" #st3v +++
    # url = "https://www.isalos.net/" #st3v +++
    # url = "https://www.capital.gr/tag/nautilia/" #st3v +++
    # url = "https://www.maritimes.gr/el/"
    # url = "https://www.pno.gr/"
    # url = "https://tralaw.gr/category/nautika-nea/"
    # url = "https://www.tanea.gr/tag/%CE%BD%CE%B1%CF%85%CF%84%CE%B9%CE%BA%CE%BF%CE%AF/"
    # url = "https://www.alithia.gr/eidiseis" #st3v +++
    url = "https://hellenicnavy.gr/" #st3v +++ 1+2=35 no-punc ++
    # url = "https://www.onalert.gr/" #st3v +++ no-punc ++

#TODO ***:
# url filter ( #, /, etc.) or privacy-policy
# add domain prefix
# en çok olanı al
# 2 ve 3. en çok vote alana class search uygula geçenleri al.
# discard vote < 3
# url kontrolü yap
# parent element check yaparak elementin attributelarını kontrol et ve cookie ve privacy policy elemesi yap (cookie, privacy policy, privacy-policy)



    url_scraper_obj = UrlScraper()
    # url_scraper_obj.crawler_build()
    url_scraper_obj.unknown_main(source_url=url)
    # url_scraper_obj.unknown_main(source_url=url2)
    # print(url_scraper_obj._url_list_by_article_tag)
    # print(len(url_scraper_obj._url_list_by_article_tag))
    # print(url_scraper_obj._url_list_a_tag_attributes)
    # print(len(url_scraper_obj._url_list_a_tag_attributes))
    # sitemap_url = "https://www.eurasiantimes.com/sitemap.xml"
    # urls = url_scraper_obj.get_sitemap_urls(sitemap_url)
    # print(urls)





    # Example usage:

    # text = "popular-title-link headline-bold"
    # text = "MetaBox-sc-16mpay8-6 hhBlIv o-articleCard__meta"
    # text = "DNNModuleContent ModArticleCSDashboardC"
    # subwords_list = ["sample", "title", "article"]
    #
    # result = url_scraper_obj.find_matching_words(text, url_scraper_obj.url_indicator_list)
    # print(result)