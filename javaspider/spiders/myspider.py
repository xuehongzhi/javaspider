import scrapy
from scrapy_splash import SplashRequest
from urllib.parse import urljoin, urlsplit, SplitResult
from ..items import JavaspiderItem

scripts = '''
function main(splash)
    splash:init_cookies(splash.args.cookies)
    assert(splash:go(splash.args.url))
    local get_dimensions = splash:jsfunc([[
        function () {
            var elem = document.querySelector(".lic_form > input");
            if(elem !=null) {
               var rect = elem.getClientRects()[0];
               return {"x": rect.left, "y": rect.top}
            }
            return {"x":0, "y":0};
        }
    ]])
    splash:set_viewport_full()
    splash:wait(0.1)
    local dimensions = get_dimensions()
    splash:mouse_click(dimensions.x, dimensions.y)
    -- Wait split second to allow event to propagate.
    splash:wait(0.1)
    return  {
        cookies = splash:get_cookies(),
        html =  splash:html()
    }
end
'''

class IetfSpider(scrapy.Spider):
    name = "ietf"
    allowed_domains = ["ietf.org"]
    start_urls = (
        'http://www.ietf.org/',
        )

    def parse(self, response):
        yield JavaspiderItem(
            file_urls=[
                'http://www.ietf.org/images/ietflogotrans.gif',
                'http://www.ietf.org/rfc/rfc2616.txt',
                'http://www.rfc-editor.org/rfc/rfc2616.ps',
                'http://www.rfc-editor.org/rfc/rfc2616.pdf',
                'http://tools.ietf.org/html/rfc2616.html',
            ]
        )

class JavaSpider(scrapy.Spider):
    name = 'javaspider'

    def __init__(self):
        super().__init__()
        self.urls = []

    def start_requests(self):
        yield scrapy.Request(
            url='http://www.oracle.com/technetwork/java/javase/downloads/index.html',
            callback=self.parse,
       )

    def parseLink(self, response):
        import urllib
        try:
            links = response.css('.downloadBox .download')
            for link in links:
                link = link.xpath('@href').extract()
                if link and not 'void' in link[0] and 'windows' in link[0]:
                    yield JavaspiderItem( file_urls = link[:1])
        except:
            pass


    def parseItem(self, response):
        try:
            print('parseitem', response)
            #if response.status == 302:
                #    yield JavaspiderItem( file_urls= link[:1])
        except:
            pass

    def parse(self, response):
        for next_page in response.css('.dataTable td a'):
            url = next_page.xpath('@href').extract()
            if url:
                url = urljoin(response.url, url[0])
                yield SplashRequest(url, callback = self.parseLink,
                                    endpoint='execute',
                                    args={'wait':0.5, 'lua_source': scripts})
