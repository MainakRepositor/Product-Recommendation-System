import scrapy
from scrapy import Selector

class DermSpider(scrapy.Spider):
    name = 'moisturizers'

    def start_requests(self):
        search_url = 'https://www.dermstore.com/skin-care/moisturizers.list?pageNumber=1'
        yield scrapy.Request(url=search_url, callback=self.parse, meta={'page': 1})


    def parse(self, response):
        page_num  = response.meta['page']
        total_pages = int(response.css('a.responsivePaginationButton.responsivePageSelector.responsivePaginationButton--last::text').get().lstrip().strip())
        product_links = []
        for products in response.css('div.productBlock'):
            product_links.append('https://www.dermstore.com'+products.css('a.productBlock_link').attrib['href'])

        for link in product_links:
            yield scrapy.Request(url = link, callback=self.parse_product_data)

        if page_num < total_pages:
            page_num += 1
            next_page = 'https://www.dermstore.com/skin-care/moisturizers.list?pageNumber='+str(page_num)
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse, meta={'page': page_num})
            
    

    def parse_product_data(self, response):
        application = ''
        concerns = ''
        skin_type = ''

        try:
            html_at_glance = ''.join(response.css('#product-description-content- div.productDescription_synopsisContent div.athenaProductPageSynopsisContent').getall()).replace('<div class="athenaProductPageSynopsisContent"><p>', '').replace('</p></div>', '').split('<br>')
            for elem in html_at_glance:
                sel = Selector(text=elem)
                if('Application Area' in ''.join(sel.xpath('//strong//text()').getall())):
                    application = sel.xpath('//a//text()').getall()
                elif('Ideal for these Concerns' in ''.join(sel.xpath('//strong//text()').getall())):
                    concerns = sel.xpath('//a//text()').getall()
                elif('Skin Type' in ''.join(sel.xpath('//strong//text()').getall())):
                    skin_type = sel.xpath('//a//text()').getall()
        except:
            print('At Glance Section Does Not Exist')
        try:
            yield {
                    'name': response.css('h1.productName_title::text').get(),
                    'brand': response.css('ul.productDescription_contentPropertyValue.productDescription_contentPropertyValue_brand li.productDescription_contentPropertyValue_value::text').get(),
                    'link': response.request.url,
                    'product_description': response.css('div.athenaProductPageSynopsisContent p::text').get(),
                    'price': float(str(response.css('p.productPrice_price  ::text').get()).strip().replace('$', '')), 
                    'app_area': application,
                    'concern': concerns,
                    'skin_type': skin_type,
                    'all_ingreds': ''.join(response.css('#product-description-content-7 *::text').getall()).strip()
            }
        except:
            yield {
                    'name': response.css('h1.productName_title::text').get(),
                    'brand': response.css('ul.productDescription_contentPropertyValue.productDescription_contentPropertyValue_brand li.productDescription_contentPropertyValue_value::text').get(),
                    'link': response.request.url,
                    'product_description': response.css('div.athenaProductPageSynopsisContent p::text').get(),
                    'price': float(str(response.css('span.productPrice_fromPrice::text').get()).replace('from','').strip().replace('$','')), 
                    'app_area': application,
                    'concern': concerns,
                    'skin_type': skin_type,
                    'all_ingreds': ''.join(response.css('#product-description-content-7 *::text').getall()).strip()
            }

            
