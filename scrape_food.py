# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 11:01:11 2021

@author: pp
"""

# 依赖 ruia == 0.5.5
# 使用协程模型开发爬虫的模板

import aiofiles
from urllib.parse import urljoin
from ruia import AttrField, TextField, Item, Spider, Response


class foodsItem(Item):
    foods_item = TextField(css_select='li.lie>a', many = True)
    foods_url = AttrField(css_select='li.lie>a', attr='href', many = True)

    async def clean_foods_url(self, foods_url):
        """
        加上domain
        """
        domain = 'http://db.foodmate.net/yingyang/'
        return [urljoin(domain, i) for i in foods_url]

class nutriItem(Item):
    nutrition = TextField(css_select = 'div#rightlist>div.list',many = True)

class foodsSpider(Spider):
    start_urls = [f'http://db.foodmate.net/yingyang/type_{index}.html' for index in range(1,22)]
    concurrency = 4

    async def parse(self, response: Response):
        Item = await foodsItem.get_item(html = response.html)
        nutritions = [] 
        async for resp in self.multiple_request(urls = Item.foods_url):
            nutrition = await self.parseNur(response=resp)
            nutritions.append(nutrition)
        foods = Item.foods_item
        await self.process_item(foods, nutritions)
            

    async def parseNur(self, response: Response):
        item = await nutriItem.get_item(html = response.html)
        return item
        # await self.process_item(data, item)
        # print(title, str(item.nutrition))

    async def process_item(self, itemA, itemB):
        """Ruia build-in method"""
        async with aiofiles.open('./foods_list.txt', 'a') as f:
            for i, value in enumerate(itemB):
                await f.write(str(itemA[i]) + '\t' + str(value)+'\n')


if __name__ == '__main__':
    foodsSpider.start(middleware=None)