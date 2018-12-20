# Example ML project for Azure

The goal of this project is to assess wikipedia article titles and comments.  For this purpose we have built the following components:

* Wikipedia events listener
* active learning (for labeling of data):
* machine learning classification of political lean: 
* data visualization:

## Getting Started And Running The Example Yourself

If you want to do some local development on this project, you simply need to install the necessary requirements.

Note we recommend python 3.6+, this may work on earlier versions, but we make no guarantees.

`python -m pip install -r requirements.txt`

And then scrape some data by running:

`python wikipedia_events_listener.py`

## Run the tests

`pytest tests.py`
