import scrapy
import re

class TeamSpider(scrapy.Spider):
    name = "team"
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'scrapy_report.json'
    }

    def __init__(self, target_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [target_url] if target_url else []

    def parse(self, response):
        names = response.css('h3::text').getall()
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", response.text)

        yield {
            'url': response.url,
            'names': names,
            'emails': emails
        }
