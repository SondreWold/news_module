
import logging
import pymysql
import ftfy
from keys import CONNECTION_DETAILS
import re
import nltk
from nltk.util import ngrams
import string
from collections import Counter
import operator
import matplotlib.pyplot as plt

def remove_html_tags(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def get_articles(id_site, interval_start, interval_stop):
    query = "SELECT id_article, xmltext FROM Article WHERE id_site = {} AND stimestamp between (1<<31)-unix_timestamp()+3600*24*{} AND (1<<31)-unix_timestamp()+3600*24*{}".format(id_site, interval_stop, interval_start)
    connection = pymysql.connect(host=CONNECTION_DETAILS["host"],port=CONNECTION_DETAILS["port"], user=CONNECTION_DETAILS["user"],passwd=CONNECTION_DETAILS["passwd"],db=CONNECTION_DETAILS["db"],charset=CONNECTION_DETAILS["charset"])
    cur = connection.cursor(pymysql.cursors.DictCursor)
    cur.execute(query)
    list_of_articles = []
    for line in cur.fetchall():
        text = ftfy.fix_encoding(line["xmltext"])
        plain_text = remove_html_tags(text)
        out = plain_text.translate(str.maketrans("","", string.punctuation))
        list_of_articles.append(out)
    return list_of_articles

if __name__ == "__main__":
    #logging
    format = '%(asctime)s - %(levelname)s - %(message)s'
    logging_filename = "news_fetcher"
    logging_location = "../logs/"
    logging.basicConfig(filename=logging_location + logging_filename +
                    ".log",format=format, level=logging.INFO)
    logging.info("Starting news fetcher")
    list_of_articles = get_articles(34,28,14)
    words_per_article = [nltk.word_tokenize(article) for article in list_of_articles]
    flat_list = [item for sublist in words_per_article for item in sublist]
    fd = nltk.FreqDist(flat_list)
    bigrams = nltk.FreqDist(ngrams(flat_list, 2))
    bigrams_great = nltk.FreqDist({k:v for (k,v) in bigrams.items() if v > 50})
    fd_great = nltk.FreqDist({k:v for (k,v) in fd.items() if len(k) >10})
    most_common_words = dict(sorted(fd_great.items(), key=operator.itemgetter(1),reverse=True)[:5])
    most_common_bigrams = dict(sorted(bigrams_great.items(), key=operator.itemgetter(1),reverse=True)[:5])
    
    
    plt.bar(range(len(most_common_words)), list(most_common_words.values()), align='center')
    plt.xticks(range(len(most_common_words)), list(most_common_words.keys()))
    plt.show()

    plt.bar(range(len(most_common_bigrams)), list(most_common_bigrams.values()), align='center')
    plt.xticks(range(len(most_common_bigrams)), list(most_common_bigrams.keys()))
    plt.show()
