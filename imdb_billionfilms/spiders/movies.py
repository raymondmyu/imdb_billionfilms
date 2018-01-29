# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import MovieImages, ActorImages
from bs4 import BeautifulSoup

class MoviesSpider(scrapy.Spider):
    name = 'movies'
    allowed_domains = ['imdb.com']
    start_urls = ['http://www.imdb.com/imdbpicks/32-billion-dollar-grossing-movies/ls063095038/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=3486279762&pf_rd_r=1XX46PWMX2PSJRKZZZ9D&pf_rd_s=center-2&pf_rd_t=15061&pf_rd_i=homepage&ref_=hm_pks_bfc_sm']

    def parse_title(self, response):
        summary = response.css('.summary_text::text').extract_first()
        directors = response.css('span[itemprop="director"] span::text').extract()
        writers = response.css('span[itemprop="creator"] span::text').extract()
        actors = response.css('span[itemprop="actors"] span::text').extract()

        actors_links = [response.urljoin(x) for x in response.css('span[itemprop="actors"] a::attr(href)').extract()]

        # Parse actors
        for actor, actor_link in zip(actors, actors_links):
            yield scrapy.Request(actor_link, callback=self.parse_actor, meta={'actor': actor, 'title': response.meta['title']})

        yield {
            'type': 'titlesummary',
            'title': response.meta['title'],
            'summary': summary,
            'directors': directors,
            'writers': writers,
            'actors': actors
        }

    def parse_actor(self, response):
        fullbio_link = response.css('span[class="see-more inline nobr-only"] a::attr(href)').extract_first()
        actor_imgsrc = response.css('img#name-poster::attr(src)').extract_first()
        yield ActorImages(type='actorimage', actor=response.meta['actor'], image_urls=[actor_imgsrc], image_name='a-'+response.meta['actor'])
        yield scrapy.Request(response.urljoin(fullbio_link), callback=self.parse_fullbio, meta=response.meta)

    def parse_fullbio(self, response):
        title = response.meta['title']
        actor = response.meta['actor']

        overview = response.css('table#overviewTable')
        birthdate = overview.css('time::attr(datetime)').extract_first()
        birthplace = overview.css('td.label:contains("Born")+td>a::text').extract_first()
        birthname = overview.css('td.label:contains("Birth Name")+td::text').extract_first()
        height = overview.css('td.label:contains("Height")+td::text').extract_first()

        minibio = response.css('h4:contains("Mini Bio")+div')
        bio = BeautifulSoup(minibio.css('p').extract_first(), 'lxml').text

        quotes = response.css('a[name="quotes"]+h4~div').extract()
        quotes = [BeautifulSoup(x,'lxml').text.strip() for x in quotes]

        yield {
            'type': 'bio',
            'title': title,
            'actor': actor,
            'birthdate': birthdate,
            'birthplace': birthplace,
            'birthname': birthname,
            'height': height,
            'bio': bio,
            'quotes': quotes
        }

    def parse(self, response):

        def to_num(text):
            # Extract the digits with .
            num_text = re.search('([\d.]+)', text.replace(',','')).group()
            # Extract words
            words = re.search('([a-zA-Z]+)',text)
            to_multiply = 1
            if words:
                if words.group() in ('million','millions'):
                    to_multiply = 1e6

            if '.' in num_text:
                return float(num_text)*to_multiply
            else:
                return int(num_text)*to_multiply

        for movie in response.css('.image-list-item'):
            description = movie.css('.image-list-item-description')

            ranking = to_num(description.css('b:first-child::text').extract_first())
            title = description.css('a:first-child::text').extract_first().strip()
            year = re.findall('\((\d*)\)',description.css("b").extract_first())[0]
            gross = to_num(description.css("p::text").extract()[1])
            opening = to_num(description.css("p::text").extract()[2])
            # actors = description.css('a:not(a:first-child)::text').extract()

            # Get Links
            title_link = response.urljoin(description.css('a:first-child::attr(href)').extract_first())
            # actor_links = [response.urljoin(x) for x in description.css('a:not(a:first-child)::attr(href)').extract()]

            # Get title summary
            yield scrapy.Request(title_link, callback=self.parse_title, meta={'title': title})

            img_src = movie.css('img::attr(src)').extract_first()
            image_name = str(int(ranking))+'- '+title
            if img_src:
                yield MovieImages(type='billionfilm', ranking=ranking, title=title, year=year, gross=gross, opening=opening, image_urls=[img_src], image_name=image_name)