import reddit_news_scrap
from requests_html import HTMLSession

def test_ensure_200():
    session = HTMLSession()
    response = session.get("https://microsoft.com")
    assert reddit_news_scrap.is_200(response)


def test_articles_empty():
    articles = []
    try:
        reddit_news_scrap.articles_is_empty(articles)
        assert False
    except SystemExit as e:
        assert True


def test_articles_not_empty():
    articles = ["test"]
    try:
        reddit_news_scrap.articles_is_empty(articles)
        assert True
    except SystemExit as e:
        assert False

class MockArticle:
    
    def __init__(self,absolute_links,text):
        self.text = text
        self.absolute_links = absolute_links

    def __getitem__(self, position):
        return self.absolute_links[position]

def test_article_attributes():
    text = "Posted by\nu/OMS6\n4 hours ago\nFBI catches Air Force senior Officer during underage sex sting operation\nabcnews"
    absolute_links = ["https://www.reddit.com/r/news/comments/01","https://source-url","https://www.reddit.com/user/testuser"]
    articles = []
    a = MockArticle(absolute_links,text)
    articles.append(a)
    
    expected_result = {"url_reddit_internal": "https://www.reddit.com/r/news/comments/01",
                      "url_reddit_user_profile" : "https://www.reddit.com/user/testuser",
                      "url_reddit_external":"https://source-url",
                      "title": "FBI catches Air Force senior Officer during underage sex sting operation" 
                       }

    expected_result = [expected_result]
    result =  reddit_news_scrap.get_article_attributes(articles)
    assert result == expected_result

def test_contains_noise_words():
    comment = "more replies"
    assert reddit_news_scrap.contains_noise_words(comment)