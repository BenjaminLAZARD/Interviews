import feedparser
from scrapy import Selector

from src.orm_models.models import NEWS_SOURCE_2_URL


def extract_html_from_body(body: str) -> str:
    return Selector(text=body).xpath("string(.)").get()


def retrieveLatestRssFeed(news_source_name: str):
    feed = feedparser.parse(NEWS_SOURCE_2_URL[news_source_name])
    feed = [
        {
            "_id": str(hash(article.description)),
            "title": article.get("title", ""),
            "link": article.get("link", ""),
            "description": extract_html_from_body(article.content[0].value),
            "publication_date": article.get("published", ""),
            "creator": article.get("credit", ""),
            "source": news_source_name,
        }
        for article in feed.entries
        # if article has no description ditch it
        if article.description and len(article.description) > 10
    ]
    return feed
