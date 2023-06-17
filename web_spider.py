import os
import urllib.parse
from bs4 import BeautifulSoup
import scrapy
from scrapy.linkextractors import LinkExtractor
import html2text



class WebsiteSpider(scrapy.Spider):
    name = 'website_spider'
    
    def __init__(self, start_url, domain, *args, **kwargs):
        super(WebsiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.link_extractor = LinkExtractor(allow_domains=[domain])


    link_extractor = LinkExtractor(allow_domains=['docs.lens.xyz'])

    def parse(self, response):
        # Save the current page's content to a text file
        self.save_page(response)

        # Extract all the links from the current page
        links = self.link_extractor.extract_links(response)

        # Follow each link and process the linked pages
        for link in links:
            yield scrapy.Request(link.url, callback=self.parse)


    def save_page(self, response):
    # Create the folder structure based on the URL path
        file_path = self.get_file_path(response.url)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Extract only the text content from the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove all script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Convert the HTML to Markdown
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.inline_links = False
        converter.ignore_images = True
        converter.body_width = 0
        markdown_text = converter.handle(str(soup))

        # Save the Markdown content to a .md file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"URL: {response.url}\n\n")
            file.write(markdown_text)



    def get_file_path(self, url):
    # Return a file path based on the URL
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path.strip('/')
        if not path:
            path = 'index'
        return f"output/{path}.md"

