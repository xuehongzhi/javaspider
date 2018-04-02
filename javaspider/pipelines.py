# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy, os, urllib
from scrapy.pipelines.files import FilesPipeline
class JavaspiderPipeline(FilesPipeline):
    ### Overridable Interface
    def parse(self, response):
        pass

    def file_path(self, request, response=None, info=None):
        url = urllib.parse.urlparse(request.url.rstrip('/'))._replace(query='').geturl()
        print('url=', url)
        media_guid =  os.path.basename(url) # change to request.url after deprecation
        return 'full/%s' % (media_guid)

    def get_media_requests(self, item, info):
        reqs = []
        for x in item.get(self.files_urls_field, []):
            req = urllib.request.Request(x ,headers={'Cookie':'oraclelicense=a'})
            url = urllib.request.urlopen(req).geturl()
            reqs.append(scrapy.http.Request(url))
        return reqs


