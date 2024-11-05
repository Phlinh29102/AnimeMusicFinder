import scrapy
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class ScraperSpider(scrapy.Spider):
    name = 'scraper'
    allowed_domains = ['www.animelyrics.com']
    start_urls = ['http://www.animelyrics.com/anime']

    def parse(self, response):
        anime_links = response.css('#content table td:nth-child(1) td a::attr(href)').getall()  # Extract href attributes
        anime_names = response.css('#content table td:nth-child(1) td a::text').getall()  # Extract text

        # Use a for loop to yield each anime link and name
        for link, name in zip(anime_links, anime_names):
            yield {
                'anime_link': link.strip(),  # Strip whitespace if necessary
                'anime_name': name.strip()    # Strip whitespace if necessary
            }

