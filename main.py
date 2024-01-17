import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from urllib.parse import urlparse
from itertools import chain

class UrlScraper:
    def __init__(self, source_url, ):
        self.source_url = source_url
        self.domain_url = self.parse_url_domain()
        self.html_content = self.get_html_with_selenium(url_=self.source_url)
        self.soup_obj = BeautifulSoup(self.html_content, 'html5lib')
        self.anchor_tags = self.soup_obj.find_all('a')
        self.url_clue_list = ["news", "content", "title", "post", "article", "text"]
        self.url_list_by_article_tag = []
        self.url_list_a_tag_css = []
        self.search_parent_element_threshold = 2
        self.search_child_element_threshold = 2

        #TODO: remove '#' and 'domain-url'
        #TODO: class içerisinde cookie var mı bak varsa alma parent divinede bak.

    def parse_url_domain(self):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain

    def get_html_with_selenium(self, url_):
        try:
            # Specify the path to your ChromeDriver executable
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url_)
            time.sleep(10)
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
            print(f"Error: Unable to fetch content. Status code: {response.status_code}")
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

    def is_media_url(self, url):
        media_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
                            'mp4', 'webm', 'avi', 'mkv',
                            'mp3', 'wav', 'flac', 'ogg']

        pattern = re.compile(r'\.({})$'.format('|'.join(map(re.escape, media_extensions))), flags=re.IGNORECASE)
        return bool(pattern.search(url))

    def find_all_urls(self, base_url):
        # Send a GET request to the URL
        response = requests.get(base_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all anchor tags (a) that contain href attributes
            all_links = soup.find_all('a', href=True)

            # Extract and print the absolute URLs using urljoin
            for link in all_links:
                absolute_url = urljoin(base_url, link['href'])
                print(absolute_url)

        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")

    def extract_urls_from_anchor(self, html_element):
        print("Finding anchor tags")
        extracted_tag = [a_tag for a_tag in html_element.find_all('a')]
        urls = self.find_urls_by_attribute(extracted_tag)
        print(urls)

        return urls

    def find_urls_by_attribute(self, a_tags, word_threshold=3):
        # a_tags = html_content.find_all('a')
        valid_anchor_tags = []
        for a_tag in a_tags:
            print("\n\n")
            # if 'title' in a_tag.attrs:
            #     print("Found 'title' in <a/> tag")
            #     print(a_tag)
            #     print(a_tag['title'])
            #     if "href" in a_tag.attrs:
            #         valid_anchor_tags.append(a_tag['href'])
            if 'class' in a_tag.attrs:
                print("Found 'class' in <a/> tag")
                print(a_tag)
                print(a_tag['class'])
                if bool(self.find_matching_words(text=" ".join(a_tag['class']), subwords=self.url_clue_list)):
                    if "href" in a_tag.attrs:
                        valid_anchor_tags.append(a_tag['href'])
            elif self.check_parent_tags(a_tag):
                if "href" in a_tag.attrs:
                    valid_anchor_tags.append(a_tag['href'])
            else:
                print("<a/> tag does not include any 'class' or 'title' or parent attribute.")

        return valid_anchor_tags

    def check_parent_tags(self, html_element):
        print("Searching parent elements on selected <a/> tag.")
        for i in range(0, self.search_parent_element_threshold):
            print(i)
            html_element = html_element.find_parent()
            if "class" in html_element.attrs and bool(self.find_matching_words(text=" ".join(html_element['class']), subwords=self.url_clue_list)):
                return True
        return False



    def check_child_tags(self):
        pass

    def crawl_article_urls(self):
        article_divs = self.find_articles(html_element="article")
        print(f"Found {len(article_divs)} articles.")
        return list(set(chain(*[self.extract_urls_from_anchor(html_element=article) for article in article_divs])))

    def crawler_build(self):
        extracted_urls = self.crawl_article_urls()
        if extracted_urls:
            return extracted_urls
        else:
            extracted_urls = self.extract_urls_from_anchor(html_element=self.soup_obj)
            return extracted_urls
#
# *Find <article/>*
# if <article> exist:
#   scrape <a/> tags in <article/> tags
# else:
#   scrape all <a/> tags
#   remove media urls by search .jpg or .png .svg endings etc. (regex)
#   valid_url_list_1 = check <a/> tags which contains 'title' attribute then find_pattern_subwords()
#   valid_url_list_2 = check <a/> tags which contains 'class' attribute then find_pattern_subwords()
#   valid_url_list_3 = check <a/> tags parents element (depth can be 2 or 3) then check their 'class' attribute then find_pattern_subwords()
#   valid_url_list_4 = check <a/> tags child elements then check their 'class' attribute then find_pattern_subwords() and try find text in childs.
#   valid_url_list_5 = set(valid_url_lists)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # url = "https://www.navalnews.com/category/naval-news/page/2/" #done, 10 haber
    #url = "https://www.navytimes.com/" #done, 51 haber
    # url = "https://www.navy.mil/Press-Office/" #text-threshold dene
    # url = "https://www.centcom.mil/MEDIA/NEWS-ARTICLES/" #done
    # url = "https://www.dailysabah.com/war-on-terror" # sıkıntı, # ve cookies urllerini discard et.
    # url = "https://www.military.com/navy" #done, head çıkarıldı
    url = "https://www.businessinsider.com/news" #done, 51
    url_scraper_obj = UrlScraper(source_url=url)
    # urls = url_scraper_obj.crawler_build()
    # print(len(urls))
    # print(urls)


    # Example usage:

    text = "popular-title-link headline-bold"
    subwords_list = ["sample", "title", "article"]

    result = url_scraper_obj.find_matching_words(text, url_scraper_obj.url_clue_list)
    print(result)