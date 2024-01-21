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

class UrlScraper:
    def __init__(self, source_url, ):
        self.source_url = source_url
        self.selenium_wait_timeout = 10
        self.search_parent_element_threshold = 3
        self.search_child_element_threshold = 2
        self.min_text_length = 3
        self.url_indicator_list = ["news", "content", "title", "post", "article", "text", "story"]  # , "headline", "heading"
        self.non_url_indicator_list = ["privacy", "policy", "cookie", "pay"]
        self.non_article_url_endpoints = ["#", "/", "privacy-policy/"]
        self.html_content = self.get_html_with_selenium(url_=self.source_url)
        self.soup_obj = BeautifulSoup(self.html_content, 'html5lib')
        self.anchor_tags = self.soup_obj.find_all('a')
        self.parsed_source_url = self.parse_url(news_url=self.source_url)
        self.extend_non_article_url_endpoints(urls=self.non_article_url_endpoints.copy())
        self.rejected_urls = set()
        self.accepted_urls = set()
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

    def get_html_with_selenium(self, url_):
        try:
            # Specify the path to your ChromeDriver executable
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url_)

            print(self.selenium_wait_timeout)
            WebDriverWait(driver, self.selenium_wait_timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))

        #    driver.switch_to.new_window()
            html_code = driver.page_source
            driver.quit()

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

    # def is_media_url(self, url):
    #     media_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
    #                         'mp4', 'webm', 'avi', 'mkv',
    #                         'mp3', 'wav', 'flac', 'ogg']
    #
    #     pattern = re.compile(r'\.({})$'.format('|'.join(map(re.escape, media_extensions))), flags=re.IGNORECASE)
    #     return bool(pattern.search(url))
    #
    # def find_all_urls(self, base_url):
    #     # Send a GET request to the URL
    #     response = requests.get(base_url)
    #
    #     # Check if the request was successful (status code 200)
    #     if response.status_code == 200:
    #         # Parse the HTML content of the page
    #         soup = BeautifulSoup(response.content, 'html.parser')
    #
    #         # Find all anchor tags (a) that contain href attributes
    #         all_links = soup.find_all('a', href=True)
    #
    #         # Extract and print the absolute URLs using urljoin
    #         for link in all_links:
    #             absolute_url = urljoin(base_url, link['href'])
    #             # print(absolute_url)
    #
    #     else:
    #         print(f"Failed to retrieve the page. Status code: {response.status_code}")

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

    def check_hyperlink_texts(self, hyperlink_tag, ):
        text_of_hyperlink = hyperlink_tag.text.strip()
        pure_text_of_hyperlink = (text_of_hyperlink and self.remove_punctuation(
            text=text_of_hyperlink)) or ''
        # text control if exist
        if pure_text_of_hyperlink:
            if len(pure_text_of_hyperlink.split()) > self.min_text_length: # alternatif olarak url-endpatinde keyword search yap.
                if hyperlink_tag['href'] in self.rejected_urls: self.rejected_urls.remove(hyperlink_tag['href'])
                return True
            else:
                # self.rejected_urls.add(hyperlink_tag)
                if hyperlink_tag['href'] not in self.accepted_urls: self.rejected_urls.add(hyperlink_tag['href'])
                return False
        else:
            if hyperlink_tag['href'] in self.rejected_urls: self.rejected_urls.remove(hyperlink_tag['href'])
            return True

    def url_formatter(self, article_url):
        if 'http' in article_url:
            return article_url
        else:
            http_article_url = 'https://' + self.parsed_source_url['domain'] + article_url
            return http_article_url

    def html_element_attribute_searching(self, html_tag, caller, hyperlink_tag=None):
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
            if self.html_element_attribute_searching(html_tag=hyperlink_tag, caller='hyperlink'):
                hyperlink_tag['href'] not in self.non_article_url_endpoints and self.accepted_urls.add(self.url_formatter(article_url=hyperlink_tag['href']))
                #self.accepted_urls.add(hyperlink_tag['href'])
            if self.check_parent_tags(hyperlink_tag=hyperlink_tag):
                (hyperlink_tag['href'] not in self.non_article_url_endpoints) and (hyperlink_tag['href'] not in self.rejected_urls) and self.accepted_urls.add(self.url_formatter(article_url=hyperlink_tag['href']))
                #(hyperlink_tag['href'] not in self.rejected_urls) and self.accepted_urls.add(hyperlink_tag['href'])
            # else:
            #     print("<a/> tag does not include any 'class' or 'title' or parent attribute.")
        return self.accepted_urls

    def check_parent_tags(self, hyperlink_tag):
        # print("Searching parent elements on selected <a/> tag.")
        html_element = hyperlink_tag
        for i in range(0, self.search_parent_element_threshold):
            html_element = html_element.find_parent()
            if self.html_element_attribute_searching(html_tag=html_element, hyperlink_tag=hyperlink_tag, caller='parent'):
                return True
        return False

    def check_child_tags(self):
        pass

    #TODO: self._url_list_by_article_tag kaldır
    def crawl_article_urls(self):
        article_divs = self.find_articles(html_element="article")
        print(f"Found {len(article_divs)} articles.")
        self._url_list_by_article_tag += list(set(chain(*[self.extract_urls_from_anchor(html_element=article) for article in article_divs]))) #TODO: incele bussinessinsider duplice news-url çekiyor.
   #     self._url_list_by_article_tag.append(chain(*[self.extract_urls_from_anchor(html_element=article) for article in article_divs]))

    def crawler_build(self):
        self.crawl_article_urls()
        self.extract_urls_from_anchor(html_element=self.soup_obj)

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

    url = "https://www.navalnews.com/category/naval-news/page/2/" #done, 19 haber recall+
    # url = "https://www.navalnews.com/"
    # url = "https://www.navytimes.com/" #done recall+
    # url = "https://www.navytimes.com/news/pentagon-congress/" #incele
    # url = "https://www.navy.mil/Press-Office/" #
    # url = "https://www.centcom.mil/MEDIA/NEWS-ARTICLES/" #done recall oriented. +
    # url = "https://www.centcom.mil/" #done recall oriented. +
    # url = "https://www.dailysabah.com/war-on-terror" # sıkıntı, # ve cookies urllerini discard et.
    # url = "https://www.military.com/navy" #done, head çıkarıldı
    #url = "https://www.businessinsider.com/news" #done, 50 +
    #url = "https://indianexpress.com/"#done recall+
    #url = "https://www.voanews.com/a/ships-aircraft-search-for-missing-navy-seals-after-mission-to-seize-iranian-missile-parts/7440990.html" #done recall+
    # url = "https://www.defensenews.com/naval/" #done, recall+
    url = "https://www.defensenews.com/"
    #url = "https://www.navaltoday.com/" #done, 44 recall+





    url_scraper_obj = UrlScraper(source_url=url)
    url_scraper_obj.crawler_build()
    # print(url_scraper_obj._url_list_by_article_tag)
    # print(len(url_scraper_obj._url_list_by_article_tag))
    # print(url_scraper_obj._url_list_a_tag_attributes)
    # print(len(url_scraper_obj._url_list_a_tag_attributes))
    print(url_scraper_obj.rejected_urls)
    print("accepted urls:")
    print(url_scraper_obj.accepted_urls)
    print(len(url_scraper_obj.accepted_urls))



    # Example usage:

    # text = "popular-title-link headline-bold"
    # text = "MetaBox-sc-16mpay8-6 hhBlIv o-articleCard__meta"
    # text = "DNNModuleContent ModArticleCSDashboardC"
    # subwords_list = ["sample", "title", "article"]
    #
    # result = url_scraper_obj.find_matching_words(text, url_scraper_obj.url_indicator_list)
    # print(result)