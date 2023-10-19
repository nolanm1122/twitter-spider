# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Tweet(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    text = scrapy.Field()
    date = scrapy.Field()
    user_handle = scrapy.Field()
    favorites = scrapy.Field()
    replies = scrapy.Field()
    retweets = scrapy.Field()
