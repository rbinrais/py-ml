import json
import sys
from sseclient import SSEClient 
import time
import csv
import os
from datetime import datetime
import pandas as pd
import sys
import azure_helper
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def contains_noise_words(comment):
    """Helper check for noise words in a text.
       Returns True if noise word is present in the comment otherwise returns False
    """
    noise_words = ["Wikipedia:", "User:" ,"Template:" , "Talk:" "User talk:" , "[[" ]
    for word in noise_words:
        if comment.find(word) != -1:
            return True
    return False

def check_text_for_noise_words(text):
    not_empty = text is not None
    return (not_empty) and (not contains_noise_words(text))

def capture_wiki(show_runtime=False, 
                wiki_recent_changes_event_url = "https://stream.wikimedia.org/v2/stream/recentchange",
                timeout=30,
                upload_To_blob=False):
    """Main program listens to wikipedia stream for live changes for the duration set by the timeout (in seconds) parameter.
       Titles and comments are captured from the live stream and then stored in the titles.csv and comments.csv respectively.
       Articles can be in any language but only those in English langauge are parsed for processing. 
    """
    
    print("This program captures the Wikipedia stream comming from "+wiki_recent_changes_event_url+" for the duration of: "+ 
        str(timeout) + " seconds")
    # Keep time to calculate how long it takes to complete this program.
    if show_runtime == True:
        startTime = datetime.now()
        print('Starting time: '+ str(startTime))
    
    # Create directory that stores all comments in csv file.
    directory = "wikipedia"
    if not os.path.exists(directory):
        os.makedirs(directory)

    titles, comments = get_wiki_recent_updates(wiki_recent_changes_event_url,timeout)
    titles_filename = "titles.csv"
    comments_filename = "comments.csv"
    
    save_titles_to_csv(titles,directory,titles_filename)
    save_comments_to_csv(comments,directory,comments_filename)
    
    if upload_to_blob:
        full_path_to_titles_file = directory + "/" + titles_filename
        full_path_to_comments_file = directory + "/" + comments_filename

        upload_To_blob(titles_filename,full_path_to_titles_file)
        upload_To_blob(comments_filename,full_path_to_comments_file)
    
    if show_runtime == True:
        print('Total running time: ' + str (datetime.now() - startTime))

def save_to_csv(dataframe, directory,filename):
    dataframe.to_csv(directory+"/"+filename)

def upload_To_blob(file_name,full_path_to_file):
    account_key= get_env_var('AZURE_STORAGE_KEY')
    account_name = get_env_var('AZURE_STORAGE_ACCOUNT')
    container_name = get_env_var('AZURE_CONTAINER_NAME')

    blob = azure_helper.get_block_service(account_name,account_key)
    azure_helper.upload_file_to_blob(blob,file_name,container_name,full_path_to_file)


def is_timeout(timeout):
    if time.time() > timeout:
        return True
    return False

def get_title_and_comment(data):
    """ Extract title and comment out the data which is a JSON string provided by Wikipedia data feed. 
        Wikipedia data feed response format is explained here: https://wikitech.wikimedia.org/wiki/EventStreams
    """
    json_obj = json.loads(data)
    title = ""
    comment = ""
    if len(json_obj) > 0:
                if(check_conditions(json_obj['title'], json_obj['server_url'], json_obj['type'],json_obj['bot'])):
                    #type is edit | log | categorize 
                    title = json_obj['title']
                    comment =   json_obj['comment']
                    print("Title: "+ title + " --> Comment: " + comment)
    
    return title, comment

def get_wiki_recent_updates(wiki_recent_changes_url, timeout_in_seconds):
    """ Listen to the Wikipedia live event feed comming from wiki_recent_changes_url. 
        The time_out_in_seconds is the time duration after which function will stop reading the feed.
        Returns Wikipedia article titles and comments stored inside the list objects.
    """
    timeout = time.time() + timeout_in_seconds
    messages = SSEClient(wiki_recent_changes_url)
    titles = []
    comments = []
    for msg in messages:
        if is_timeout(timeout):
            return titles , comments
        data = msg.data    
        if len(data.strip()) > 0: 
            title , comment = get_title_and_comment(data)
            if len(title) > 0:
                titles.append(title)
            if len(comment) > 0:
                comments.append(comment)

def check_conditions(text, server_url, article_type, isBot=False):
    # Filter articles based on language (engligh only) with active edits by human (not by bot)
    if (check_text_for_noise_words(text) and server_url == "https://en.wikipedia.org" and  article_type == "edit" and isBot == False ):
          return True 
    return False

def update_existing_csv(dataframe, directory, filename, col_name):
    existing_csv = directory+"/"+filename
    if os.path.exists(existing_csv):
        df = pd.read_csv(existing_csv)
        df = df[col_name]
        df = pd.DataFrame(df)
        dataframe = dataframe.append(df)
        dataframe.index = list(range(len(dataframe)))
    return dataframe 

def save_titles_to_csv(titles, directory, filename):
    dataframe = pd.DataFrame(titles, columns=["titles"])
    dataframe = update_existing_csv(dataframe, directory, 
                                    filename, "titles")
    dataframe.to_csv(directory+"/"+filename, index=False)

def save_comments_to_csv(comments, directory, filename):
    dataframe = pd.DataFrame(comments, columns=["comments"])
    dataframe = update_existing_csv(dataframe, directory, 
                                    filename, "comments")
    dataframe.to_csv(directory+"/"+filename, index=False)

def get_env_var(name):
    try:
       return os.getenv(name)
    except KeyError:
        return None

if __name__ == "__main__":
    
    
    timeout = 30 #value is in seconds
    try:
        timeout = int(get_env_var("TIMEOUT_IN_SEC"))
    except Exception:
        pass
    
    wiki_recent_changes_url = get_env_var("WIKIPEDIA_EVENTS_ENDPOINT")
    if wiki_recent_changes_url is None:
        wiki_recent_changes_url = "https://stream.wikimedia.org/v2/stream/recentchange"
    
    upload_to_blob = get_env_var("UPLOAD_TO_AZURE_BLOB")
    if upload_to_blob is None:
        upload_to_blob = False
    else:
        upload_to_blob = True

    capture_wiki(show_runtime=True,
                 wiki_recent_changes_event_url=wiki_recent_changes_url,
                 timeout= timeout,
                 upload_To_blob=upload_To_blob)
