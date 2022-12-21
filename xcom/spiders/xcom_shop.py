import scrapy
import re
import random
from urllib.parse import urljoin
from xcom import items
from scrapy import Spider, Request

class QuotesSpider(scrapy.Spider):
    page_count = 1
    name = 'xcom_shop'
    allowed_domains = ['xcom-shop.ru']
    base_url_xcom_shop_ru = "https://www.xcom-shop.ru"
    download_delay = random.uniform(2, 5)
    proxy = {'proxy':'https://?.?.?.?:?'}
    product_details_table_dict = {}
    
#    def start_requests(self):
#        url = 'https://www.xcom-shop.ru/zalman_zm-ve350_723995.html'
#        yield scrapy.Request(url, meta=self.proxy, callback=self.get_details)
    

    def start_requests(self):
        url = 'https://www.xcom-shop.ru'
        yield scrapy.Request(url, meta=self.proxy, callback=self.get_url)
    def get_url(self, response, **kwargs):
        print(f"\nSTART def get_url_to_pages_with_products\n\n in url -- {response.url}\n")
        urls = response.css(".header_catalog_tiles__inner a::attr(href)").extract()
        print(f'{urls=}')
        for url in urls:
            print(f"url = {url}")
            joinurl = urljoin(self.base_url_xcom_shop_ru, url)
            print(f"{joinurl=}")
            try:
                yield scrapy.Request(joinurl, meta={"proxy": 'https://?.?.?.?:?'}, callback=self.get_url__with_products)
            except Exception as e:
                print(f"Exception get_subcategories_2 {e}")

    def get_url__with_products(self, response):
        print(f'{response.url=}')
        try:
            page_count = int(response.css('.content .content__catalog_center .gray span:last-of-type::text').extract()[0])//24+1
            print(f'{page_count=} \n {response.url=}')
        except Exception as e:
            print("one page")
        for page in range(page_count):
            url = urljoin(response.url, f'?list_page={page+1}')
#            url = 'https://www.xcom-shop.ru/catalog/televizory_i_proektory/?list_page=1'
            print(f'{url=}')
            yield scrapy.Request(url, meta=self.proxy, callback=self.get_url_to_product_page)

    def get_url_to_product_page(self, response):
        print(f'{response.url=} \n {response.status=} \n {response}')
        url_to_product = response.css(".catalog_items .catalog_item__name::attr(href)").extract()
        print(f'{url_to_product=}')
        for url_short in url_to_product:
            print(f'{url_short=}')
            url_long = urljoin(self.base_url_xcom_shop_ru, url_short)
            print(f'{url_long=}\n')

            yield scrapy.Request(url_long, meta=self.proxy, callback=self.get_details)
    def get_details(self, response):
        print(f'{response.url=}')
        title_description_descript_short = response.css(".product-block-description__block h2::text").extract() #  title_description=['Основные характеристики', 'Характеристики Xerox VersaLink C405DN']
        description_preambula = response.css(".product-block-description__block p::text").extract()  # ['МФУ подойдет для\xa0предприятий малого и\xa0среднего бизнеса.]удалитьлишнее

        full_description_column = response.css(".product-block-description__item").extract()
        count = 0
        for item in full_description_column:
            count+=1
            try:
                first_elem = re.findall('first-elem">(.*?)<', item.replace('\n', ''))[0].strip()
            except Exception as e:
                pass
            try:
                second_elem = re.findall('second-elem"(.*?)<', item.replace('\n', ''))[0][1:].strip()
            except Exception as e:
                pass
            if len(second_elem) == 0:
                try:
                    second_elem = re.findall('blank">(.*?)</a>', item.replace('\n', ''))[0]
                except Exception as e:
                    pass
            self.product_details_table_dict[first_elem] = second_elem
#            print(f'{first_elem} : {second_elem}')
        try:
            price = response.css(".card-bundle-basket__price--orange::text").extract()
            price = re.sub('\D', '', price[0])
            self.product_details_table_dict["price"] = price
            print(price)
        except:
            print(f"{response.url=} price  mistake ")
        try:
            self.product_details_table_dict[title_description_descript_short[0]] = description_preambula[0].replace('\xa0', ' ')
        except:
            pass

        print(f'{self.product_details_table_dict=}')
#        yield self.product_details_table_dict

    def clear_list(self, l:list):
        clear_list = []
        for item in l:
            clear_list.append(item.replace('  ', '').replace("\n", ""))
        return [value for value in clear_list if value]

"""
    def start_requests(self):
        url = 'https://www.xcom-shop.ru'
        yield scrapy.Request(url, meta=self.proxy, callback=self.get_url)

    def get_url(self, response, **kwargs):
        print(f"\nSTART def get_url_to_pages_with_products\n\n in url -- {response.url}\n")
        urls = response.css(".header_catalog_tiles__inner a::attr(href)").extract()
        print(f'{urls=}')
        for url in urls:
            print(f"url = {url}")
            joinurl = urljoin(self.base_url_xcom_shop_ru, url)
            print(f"{joinurl=}")
            try:
                yield scrapy.Request(joinurl, meta={"proxy": 'https://?.?.?.?:?'}, callback=self.get_url__with_products)
            except Exception as e:
                print(f"Exception get_subcategories_2 {e}")

    def get_url__with_products(self, response):
        print(f'{response.url=}')
        try:
            page_count = int(response.css('.content .content__catalog_center .gray span:last-of-type::text').extract()[0])//24+1
            print(f'{page_count=} \n {response.url=}')
        except Exception as e:
            print("one page")
        for page in range(page_count):
            url = urljoin(response.url, f'?list_page={page+1}')
#            url = 'https://www.xcom-shop.ru/catalog/televizory_i_proektory/?list_page=1'
            print(f'{url=}')
            yield scrapy.Request(url, meta=self.proxy, callback=self.get_url_to_product_page)

    def get_url_to_product_page(self, response):
        print(f'{response.url=} \n {response.status=} \n {response}')
        url_to_product = response.css(".catalog_items .catalog_item__name::attr(href)").extract()
        print(f'{url_to_product=}')
        for url_short in url_to_product:
            print(f'{url_short=}')
            url_long = urljoin(self.base_url_xcom_shop_ru, url_short)
            print(f'{url_long=}\n')
            """

'''
    def start_requests(self):
        url = 'https://www.xcom-shop.ru/catalog/televizory_i_proektory'
        yield scrapy.Request(url, meta=self.proxy, callback=self.get_url__with_products)
'''



'''
022-11-04 18:23:59 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/televizory_i_proektory/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/televizory_i_proektory/'
2022-11-04 18:24:00 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/klimaticheskoe_oborydovanie/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/klimaticheskoe_oborydovanie/'
2022-11-04 18:24:01 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/apple/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/apple/'
2022-11-04 18:24:02 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/instryment_izmeritelnoe_oborydovanie_i_tehnika/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/instryment_izmeritelnoe_oborydovanie_i_tehnika/'
2022-11-04 18:24:03 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/telefoniya/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/telefoniya/'
2022-11-04 18:24:05 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/torgovoe_oborydovanie/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/torgovoe_oborydovanie/'
2022-11-04 18:24:06 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/elektrika_i_sistemy_elektropitaniya/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/elektrika_i_sistemy_elektropitaniya/'
2022-11-04 18:24:09 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/igry_i_servisy/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/igry_i_servisy/'
2022-11-04 18:24:11 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/sks/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/sks/'
2022-11-04 18:24:11 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/programmnoe_obespechenie/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/programmnoe_obespechenie/'
2022-11-04 18:24:12 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/sistemy_bezopasnosti/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/sistemy_bezopasnosti/'
2022-11-04 18:24:13 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/setevoe_oborydovanie/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/setevoe_oborydovanie/'
2022-11-04 18:24:13 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/rashodnye_materialy/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/rashodnye_materialy/'
2022-11-04 18:24:14 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/ibp/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/ibp/'
2022-11-04 18:24:16 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/orgtehnika/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/orgtehnika/'
2022-11-04 18:24:17 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/periferiya/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/periferiya/'
2022-11-04 18:24:18 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/portativnaya_tehnika/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/portativnaya_tehnika/'
2022-11-04 18:24:19 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/servery_i_shd/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/servery_i_shd/'
2022-11-04 18:24:21 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/kompyuternye_komplektyyuschie/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/kompyuternye_komplektyyuschie/'
2022-11-04 18:24:22 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.xcom-shop.ru/catalog/kompyutery_i_noytbyki/> (referer: https://www.xcom-shop.ru)
response.url='https://www.xcom-shop.ru/catalog/kompyutery_i_noytbyki/'

'''
