import csv
import re
from nltk.corpus import stopwords
import nltk.stem
import pprint

def get_csv_to_array(filename):
    csv_arr = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            csv_arr.append(row)
    # print(csv_arr[0])
    return csv_arr

def sanitize(text):
    text = text.lower() # text to lowercase
    text = re.sub(r'[^\w\s]',' ',text) # remove punctuation
    text = re.sub(r'\n',' ',text) # replace multiple spaces with just one
    text = re.sub('\s\s+',' ',text) # replace multiple spaces with just one
    text_arr = []
    for word in text.split(' '):
        if(len(word) <= 20): text_arr.append(word)
    text_arr = remove_stopwords(text_arr)
    text_arr = do_stemming(text_arr)
    text_arr2 = []
    weird_word_pattern = re.compile(r'([0-9][a-z])|([a-z][0-9])')
    for word in text_arr:
        # print(word, weird_word_pattern.match(word))
        if len(word) > 1 and (not weird_word_pattern.match(word)) : text_arr2.append(word)
    return text_arr2

def remove_stopwords(text_arr):
    stopwords_arr = stopwords.words("english")
    new_text_arr = text_arr[:] # copy first text_arr
    for word in text_arr:
        if word in stopwords_arr:
            new_text_arr.remove(word)
    return new_text_arr

def do_stemming(text_arr):
    stemmer = nltk.stem.SnowballStemmer("english") # english stemmer works better than porter stemmer
    for i in range(len(text_arr)):
        text_arr[i] = stemmer.stem(text_arr[i])
    return text_arr


def prepare_csv(filename):
    csv_arr = get_csv_to_array(filename)
    for i in range(len(csv_arr)):
        # print("------")
        csv_arr[i][2] = sanitize(csv_arr[i][2])
        csv_arr[i][4] = sanitize(csv_arr[i][4])
        # print(csv_arr[i])
    return csv_arr

if __name__ == '__main__':
    csv_output = prepare_csv("csv01.csv")
    pp = pprint.PrettyPrinter()
    pp.pprint(csv_output[0:5])
