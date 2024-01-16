import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def find_matching_words(text, subwords):
    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, subwords)) + r')\w*\b|\w*(?:' + '|'.join(map(re.escape, subwords)) + r')\w*', flags=re.IGNORECASE)
    matches = pattern.findall(text)
    return matches

def is_media_url(url):
    media_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
                        'mp4', 'webm', 'avi', 'mkv',
                        'mp3', 'wav', 'flac', 'ogg']

    pattern = re.compile(r'\.({})$'.format('|'.join(map(re.escape, media_extensions))), flags=re.IGNORECASE)
    return bool(pattern.search(url))

def find_all_urls(base_url):
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
    # Example usage:
    text = "This is a sample text containing some .subwords. like example, text, and .subword."
    subwords_list = ["sample", "text", "word"]

    result = find_matching_words(text, subwords_list)

    url = "https://example.com.jpg/image"
    print(is_media_url(url))
    print(result)

    url_to_scrape = 'https://www.defensenews.com/naval/'
    find_all_urls(url_to_scrape)
