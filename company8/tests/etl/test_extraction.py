import feedparser
import pytest

from src.etl.extraction import retrieveLatestRssFeed
from src.orm_models.models import NEWS_SOURCE_2_URL


# Mocking the feedparser object
class MockContent:
    def __init__(self, value):
        self.value = value


class MockEntry:
    def __init__(self, title, link, description, published, author, content):
        self.title = title
        self.link = link
        self.description = description
        self.published = published
        self.author = author
        self.content = content

    def get(self, key, default=None):
        """Simulate the get method of a dictionary."""
        return getattr(self, key, default)


class MockFeed:
    def __init__(self, entries):
        self.entries = entries


@pytest.fixture
def mock_feedparser(mocker):
    """
    Returns a mocked feedparser.parse function
    """
    mock_feed_entries = [
        MockEntry(
            title="Sample Article 1",
            link="http://example.com/article1",
            description="This is a sample article description that is longer than 10 characters.",
            published="2023-01-01",
            author="Author 1",
            content=[MockContent("<p>This is the HTML content of article 1.</p>")],
        ),
        MockEntry(
            title="Sample Article 2",
            link="http://example.com/article2",
            description="Short desc.",  # This should be ignored
            published="2023-01-02",
            author="Author 2",
            content=[MockContent("<p>This is the HTML content of article 2.</p>")],
        ),
    ]
    mock_feed = MockFeed(mock_feed_entries)
    mocker.patch("src.etl.extraction.feedparser.parse", return_value=mock_feed)
    feedparser_parse_mock = mocker.spy(feedparser, "parse")
    return feedparser_parse_mock


def test_retrieve_latest_rss_feed(mock_feedparser) -> None:
    # Define a mock news source
    news_source_name = "test_source"
    NEWS_SOURCE_2_URL[news_source_name] = "http://example.com/rss"
    result = retrieveLatestRssFeed(news_source_name)

    # Assertions to verify the expected output
    assert len(result) == 2
    assert result[0]["title"] == "Sample Article 1"
    assert result[0]["link"] == "http://example.com/article1"
    assert result[0]["description"] == "This is the HTML content of article 1."
    assert result[0]["publication_date"] == "2023-01-01"
    assert result[0]["creator"] == "Author 1"
    assert result[0]["source"] == news_source_name

    # Check that feedparser.parse was called with the correct URL
    mock_feedparser.assert_called_once_with("http://example.com/rss")
