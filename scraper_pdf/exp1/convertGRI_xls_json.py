#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 17:23:57 2021

@author: nick
"""
import pandas as pd
import logging,sys
import re
from functools import reduce
import nltk
from nltk.corpus import stopwords

# Set the logging level
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def process(fn):
    
    REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
    GOOD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
    try:
        STOPWORDS = set(stopwords.words('english'))
    except LookupError:
        nltk.download('stopwords')
        STOPWORDS = set(stopwords.words('english'))
    
    def lower(text):
        """
        Transforms given text to lower case.
        Example:
        Input: 'I really like New York city'
        Output: 'i really like new your city'
        """
    
        return text.lower()
    
    def replace_special_characters(text):
        """
        Replaces special characters, such as paranthesis,
        with spacing character
        """
    
        return REPLACE_BY_SPACE_RE.sub(' ', text)
    
    def filter_out_uncommon_symbols(text):
        """
        Removes any special character that is not in the
        good symbols list (check regular expression)
        """
    
        return GOOD_SYMBOLS_RE.sub('', text)
    
    def remove_stopwords(text):
        return ' '.join([x for x in text.split() if x and x not in STOPWORDS])
    
    
    def strip_text(text):
        """
        Removes any left or right spacing (including carriage return) from text.
        Example:
        Input: '  This assignment is cool\n'
        Output: 'This assignment is cool'
        """
    
        return text.strip()
    
    PREPROCESSING_PIPELINE = [
                              lower,
                              replace_special_characters,
                              filter_out_uncommon_symbols,
                              remove_stopwords,
                              strip_text
                              ]
    
    # Anchor method
    
    def text_prepare(text, filter_methods=None):
        """
        Applies a list of pre-processing functions in sequence (reduce).
        Note that the order is important here!
        """
    
        filter_methods = filter_methods if filter_methods is not None else PREPROCESSING_PIPELINE
    
        return reduce(lambda txt, f: f(txt), filter_methods, text)
    
 
     # read excel into pandas datafram
    df = pd.read_excel(fn)
    # Select the right columns   
    new_df = df[df.columns[1:5]]

    new_df = new_df[new_df[new_df.columns[3]] == 'OK']
    new_df['Obs'] = new_df[new_df.columns[3]].apply(lambda txt: text_prepare(txt))
    if new_df.columns[3] != 'Obs':
        new_df = new_df.drop(columns=[new_df.columns[3]])
    
    
#    df['Text'] = df['Text'].apply(lambda txt: text_prepare(txt))
    # return df.to_json(orient='records', lines=True)
    return new_df

if __name__ == '__main__':
    # Inspired in https://realpython.com/python-command-line-arguments/#the-command-line-interface
    if not sys.argv[1:]:
        raise SystemExit(f"Usage: {sys.argv[0]} (-f) <excel filename> (-o) output.jsonl")

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    
    if "-f" in opts:
        filename = args[0] # Only one argument
        logging.debug(f"Filename: {filename}")

    # Do the processing
    final_df = process(filename)
    # End of processing
    if "-o" in opts:
        output_file = args[1]
        logging.debug(f"Output File: {output_file}")
        final_df.to_json(output_file, orient='records', lines=True) 
    else:
        print("ok")
        print(final_df.to_json(orient='records', lines=True))  
        
        
        