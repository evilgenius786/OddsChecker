import glob
import time
from collections import OrderedDict
from datetime import datetime

from scrapy import Spider, Selector
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager


class OddsCheckerScraper(Spider):
    name = 'oddschecker'
    quotes_url = 'https://quotes.toscrape.com/'
    start_urls = [quotes_url]

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': f'output/{datetime.now().strftime("%d-%m-%Y %H-%M")}.csv',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_url = self.get_search_link_from_file()
        self.driver = self.get_driver()

    def get_driver(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        return Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

    def parse(self, response, **kwargs):
        self.driver.get(self.search_url)
        time.sleep(10)
        sel = Selector(text=self.driver.page_source)

        for element in sel.css('ul._2zQ8KU'):
            _date = element.css('._1svvs0 ::text').get()

            for sub_element in element.css('ul li'):
                teams = sub_element.css('a ._2tehgH ::text').getall()
                item = OrderedDict()
                item['Date'] = _date
                item['Time'] = sub_element.css('li + ._73153N ::text').get()
                item['Team 1'] = ''.join(teams[:1]).strip()
                item['Team 2'] = ''.join(teams[1:2]).replace('@', '').strip()
                item['Spread 1'] = sub_element.css('a + div .VCz_0X button ::text').get()
                item['Spread 2'] = sub_element.css('a + div .VCz_0X button + button ::text').get()

                yield item

    def get_search_link_from_file(self):
        file_name = glob.glob('input/*.txt')[0].replace('\\', '/')
        with open(file=file_name, mode='r') as link_file:
            return link_file.readline().strip()

    def close(spider, reason):
        spider.driver.quit()
