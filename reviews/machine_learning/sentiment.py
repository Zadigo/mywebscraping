import numpy
import pandas
from django.conf import settings
from textblob import TextBlob

from mywebscraping.utils import create_filename


class CalculateSentiment:
    def __init__(self, documents):
        self.documents = documents
        self.dataframe = pandas.DataFrame({'texts': documents})

    def get_sentiment_as_csv(self, save=False):
        """Returns the calculated sentiments from the dataframe
        as a downloadable csv file for the user"""
        self.calculate_sentiment()
        filename = create_filename()
        if save:
            filepath = settings.MEDIA / filename
            self.dataframe.to_csv(filepath, index=False, encoding='utf-8')
            return filepath
        else:
            return self.dataframe.to_csv(index=False, encoding='utf-8')

    def calculate_sentiment(self):
        """From a set of text documents, calculate 
        the sentiment values where the result scales between
        -1 and 1. -1 represents a global negative sentiment, 
        0 is neutral, and 1 is extremely positif"""
        def calculator(text):
            instance = TextBlob(text)
            return instance.sentiment.polarity
        self.dataframe['sentiment'] = self.dataframe['texts'].apply(calculator)
        return numpy.mean(self.dataframe['sentiment'])
