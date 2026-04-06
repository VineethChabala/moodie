import cloudscraper
from bs4 import BeautifulSoup

class Scraper():

    def __init__(self):
        self.baseURL = "https://letterboxd.com/film"
        self.space_replace = "-"
        self.review_class = "body-text"
        self.scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })

    def scrape_review(self, movie_name):
        edited_name = movie_name.lower().replace(" ", self.space_replace).replace("'", "").replace(":", "") 
        url = f"{self.baseURL}/{edited_name}/reviews/"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1', # Do Not Track Request Header
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        response = self.scraper.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            reviews = soup.find_all("div", class_=self.review_class)

            top_reviews = {}
            top_reviews["movie"] = movie_name
            top_reviews["review"] = []

            for i in range(10):
                review = reviews[i].text.strip()
                top_reviews["review"].append(review)
            
            return top_reviews
        else:
            print(f"Error: {response.status_code}")
            return None

if __name__ == "__main__":
    scraper = Scraper()
    print(scraper.scrape_review("The Dark Knight"))
        