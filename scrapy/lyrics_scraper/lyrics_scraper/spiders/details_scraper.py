import scrapy
import json

class AnimeLyricsSpider(scrapy.Spider):
    name = "details_scraper"
    # Load the anime list from the existing animelist.json
    def start_requests(self):
        with open('animelist.json', 'r', encoding='utf-8') as file:
            anime_list = json.load(file)

        for anime in anime_list:
            # Yield requests to each anime link
            yield scrapy.Request(
                url = f"http://www.animelyrics.com/{anime['anime_link']}",
                callback=self.parse_songs,
                meta={'anime_name': anime['anime_name']}
            )

    # Parse the list of songs from each anime page
    def parse_songs(self, response):
        anime_data = {
            "anime_name": response.meta["anime_name"],
            "song": {}
        }
        # Extract song links and names (Adjust selectors as needed)
        song_links = response.css('#content th a::attr(href)').getall()  # Selector to get song links
        song_names = response.css('#content th a::text').getall()  # Selector to get song names
        # Iterate over each song and yield requests to the song pages
        for link, name in zip(song_links, song_names):
            yield scrapy.Request(
                url=f"http://www.animelyrics.com/{link}",
                callback=self.parse_lyrics,
                meta={
                    "anime_data": anime_data,
                    "song_name" : name
                }
            )
        

    # Parse the lyrics from each song page
    def parse_lyrics(self, response):
        anime_data = response.meta["anime_data"]
        song_name = response.meta["song_name"]
        
        has_table = response.css('#content div.centerbox table').get() is not None
        if has_table: 
            original_lyrics = response.css('#content div.centerbox table td.romaji *::text').getall()
            lyrics = self.clean_lyrics(original_lyrics)
        else: 
            original_lyrics = response.css('#content div.centerbox br + *::text').getall()
            lyrics = self.clean_lyrics(original_lyrics)
        #get the artist/vocalist but the website is too complicated, it keeps changing the word =))))
        #artist = response.xpath("//div[@class='centerbox']//text()[contains(., 'Performed by') or contains(., 'Sung by') or contains(., 'Vocalist') or contains(., 'Singer') or contains(., 'Singers') or contains(., 'Vocals')]").get()
        song_entry = {
            "song_name": song_name,
            "lyrics": lyrics,
        } 
        anime_data["song"] = song_entry
        yield anime_data
        
    def clean_lyrics(self, raw_lyrics):
        # Initialize a list to hold the cleaned lyrics
        cleaned_lyrics = []
        unwanted_keywords = [
            "View Kanji",
            "Lyrics from Animelyrics.com"
        ]
        for line in raw_lyrics:
            # Replace '\xa0' with space and strip whitespace
            line = line.replace('\xa0', ' ').strip()

            # Skip empty lines or lines with unwanted keywords
            if not line or any(keyword in line for keyword in unwanted_keywords):
                continue

            # Skip lines that look like HTML comments
            if line.startswith("<!--") or line.startswith("-->"):
                continue

            # Add the cleaned line to the list
            cleaned_lyrics.append(line)
            lyrics_string = "\r\n".join(cleaned_lyrics)
        return lyrics_string   
