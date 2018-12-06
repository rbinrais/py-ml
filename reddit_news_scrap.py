import requests
import lxml.html
import code
import time
import csv
import base64
import os
from requests_html import HTMLSession
from datetime import datetime

class Article(object):
    """ Represents meta-data associated with the Reddit article.
    """

    url_reddit_external = ""
    url_reddit_internal = ""
    url_reddit_user_profile = ""
    title = ""

def save_articles_to_csv(articles):
    """Helper to save list of articles to a csv file.
       CSV file namming format is reddit-news-{day-month-year}.csv
    """
    filename = 'reddit-news-%s.csv' % datetime.today().strftime('%d-%b-%Y')
    with open(filename, 'w') as myfile:
        for a in articles:
            myfile.write(a.title+","+a.url_reddit_internal+","+a.url_reddit_external+","+a.url_reddit_user_profile + "\n")

def contains_noise_words(comment):
    """Helper check for noise words in a reddit comment.
       Returns True if noise word is present in the comment otherwise returns False
    """
    noise_words = ["more replies", "more reply" ]
    for word in noise_words:
        if comment.find(word) != -1:
            return True
    return False

# Keep time to calculate how long it takes to complete this program.
startTime = datetime.now()
print('Starting time --> '+ str(startTime))

session = HTMLSession()
url_reddit_news = "https://www.reddit.com/r/news/"
url_reddit_user_profile = "https://www.reddit.com/user"
response = session.get(url_reddit_news)

#TODO: Check for status code 200 and empty response 
#TODO: Check for empty list
#TODO: Exception handling

articles = response.html.find("article")
article_list = []

# Get the external,internal and user profile links for each article along with its title.
for article in articles:
    a = Article()
    a.title = article.text.splitlines()[-2]
    for link in article.absolute_links:
        if link.find(url_reddit_news) != -1:
            a.url_reddit_internal = link
        elif link.find(url_reddit_user_profile) != -1:
            a.url_reddit_user_profile = link
        else:
            a.url_reddit_external = link
    article_list.append(a)

# Save articles meta data in a csv file
save_articles_to_csv(article_list)

# Create directory that stores all comments in csv file.
directory = "comments"
if not os.path.exists(directory):
    os.makedirs(directory)

# Iterate over articles and get all the comments (till date)
# Each article corresponds to a separate csv file that stores all the comments posted on that article.
# Each comment is seperated by newline '/n' from other comments.
# CSV file name is based on the full url to the reddit article that is base64 encoded.

for article in article_list:
    print ("Fetching article --> " + article.url_reddit_internal)
    response = session.get(article.url_reddit_internal)
    #TODO: Check for status code 200 and empty response 
    #TODO: Exception handling

    r = response.html.find("p")
    if r is not None:
        # base64 encode the article internal url and use it as a filename. 
        filename = '%s.csv' % base64.b64encode(article.url_reddit_internal.encode())
        with open( directory+"/"+filename, 'w') as myfile:
            for comments in r:
                if comments.full_text is not None and contains_noise_words(comments.full_text) == False:
                    myfile.write(comments.full_text+ "\n")


print('Total running time --> ' + str (datetime.now() - startTime))
