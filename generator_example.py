import requests

def download_image(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        print("downloaded")
        return response.status_code
    else:
        print("not downloaded")
        return None

def image_urls_generator(url_list):
    for url in url_list:
        yield download_image(url)

def main():
    # Replace the following list with the actual image URLs from the website
    image_urls = [
    ]

    image_generator = image_urls_generator(image_urls)

    # Iterate through the generator in a for loop
    for index, image_data in enumerate(image_generator):
        print("\n\n\n")
        print(image_data)
    #handle EndOfMedia

if __name__ == "__main__":
    main()
