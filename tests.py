import reddit_news_scrap
from requests_html import HTMLSession

def test_ensure_200():
    session = HTMLSession()
    response = session.get("https://microsoft.com")
    assert reddit_news_scrap.is_200(response)
