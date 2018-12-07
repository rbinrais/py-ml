import requests
import lxml.html
import code
import time
import csv
import base64
import os
from requests_html import HTMLSession
from datetime import datetime
import pandas as pd
import sys

def save_articles_to_csv(articles):
    """
    Helper to save list of articles to a csv file.
    CSV file namming format is reddit-news-{day-month-year}.csv
    """
    filename = 'reddit-news-%s.csv' % datetime.today().strftime('%d-%b-%Y')
    df = pd.DataFrame()
    for article in articles:
        df = df.append(article, ignore_index=True)
    df.to_csv(filename)

def contains_noise_words(comment):
    """Helper check for noise words in a reddit comment.
       Returns True if noise word is present in the comment otherwise returns False
    """
    noise_words = ["more replies", "more reply" ]
    for word in noise_words:
        if comment.find(word) != -1:
            return True
    return False

def is_200(response):
    return response.status_code == 200

def exit_needed(response_received):
    if not response_received:
        print("returned status_code", response.status_code, "200 was expected")
        sys.exit(0)

def articles_is_empty(articles):
    #TODO: Exception handling
    if articles == []:
        print("no articles found, try editting your query or url")
        sys.exit(0)

def get_articles():
    session = HTMLSession()
    url_reddit_news = "https://www.reddit.com/r/news/"
    response = session.get(url_reddit_news)
    status = is_200(response)
    exit_needed(status)
    articles = response.html.find("article")
    articles_is_empty(articles)
    return articles

def get_article_attributes(articles):
    """
    Get the external,internal and user profile links 
    for each article along with its title.
    """
    url_reddit_news_comments = "https://www.reddit.com/r/news/comments"
    url_reddit_user_profile = "https://www.reddit.com/user"
    article_list = []
    for article in articles:
        article_dict = {}
        article_dict["title"] = article.text.splitlines()[-2]
        for link in article.absolute_links:
            if link.find(url_reddit_news_comments) != -1:
                article_dict["url_reddit_internal"] = link
            elif link.find(url_reddit_user_profile) != -1:
                article_dict["url_reddit_user_profile"] = link
            else:
                article_dict["url_reddit_external"] = link
        article_list.append(article_dict)
    return article_list

def save_comments_to_csv(article_list,directory):
    """
    Iterate over articles and get all the comments (till date)
    Each article corresponds to a separate csv file that stores all the comments posted on that article.
    Each comment is seperated by newline '/n' from other comments.
    CSV file name is based on the full url to the reddit article that is base64 encoded.
    """
    session = HTMLSession()
    for article in article_list:
        print ("Fetching article --> " + article["url_reddit_internal"])
        try:
            response = session.get(article["url_reddit_internal"])
            status = is_200(response)
            exit_needed(status)
            r = response.html.find("p")
            if r is not None:
                # base64 encode the article internal url and use it as a filename. 
                filename = '%s.csv' % base64.b64encode(article["url_reddit_internal"].encode())
                try:
                    with open( directory+"/"+filename, 'w') as myfile:
                        for comments in r:
                            if comments.full_text is not None and contains_noise_words(comments.full_text) == False:
                                myfile.write(comments.full_text+ "\n")
                except Exception as e:
                        print ("Error occurred while saving comments for the article --> ",article["url_reddit_internal"])
                        print(e)

        except Exception as e:
                print ("Error occurred while fetching --> ",article["url_reddit_internal"])
                print(e)

def run_scraper(show_runtime=False):
    # Keep time to calculate how long it takes to complete this program.
    if show_runtime == True:
        startTime = datetime.now()
        print('Starting time --> '+ str(startTime))
    articles = get_articles()

    article_list = get_article_attributes(articles)
    # Save articles meta data in a csv file
    save_articles_to_csv(article_list)

    # Create directory that stores all comments in csv file.
    directory = "comments"
    if not os.path.exists(directory):
        os.makedirs(directory)

    save_comments_to_csv(article_list,directory)

    if show_runtime == True:
        print('Total running time --> ' + str (datetime.now() - startTime))

if __name__ == '__main__':
    run_scraper(show_runtime=True)
