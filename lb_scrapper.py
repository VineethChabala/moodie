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
        response = self.scraper.get(url)
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
        