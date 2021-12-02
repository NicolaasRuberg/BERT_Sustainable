#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 17:23:57 2021

@author: nick
"""
import fitz
from  utils import *
import pandas as pd
import logging,sys

# Set the logging level
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def process(fn):
    pdfReader = fitz.open(fn)
    font_counts, styles = fonts(pdfReader, granularity=False)
    size_tags = font_tags(font_counts, styles)
    header_para = headers_para(pdfReader, size_tags)
    df = pd.DataFrame(header_para, columns=['Size', 'Text'])
    return df
#    print(df.to_json(orient='records', lines=True)) 
#    print(header_para)

if __name__ == '__main__':
    # Inspired in https://realpython.com/python-command-line-arguments/#the-command-line-interface
    if not sys.argv[1:]:
        raise SystemExit(f"Usage: {sys.argv[0]} (-f) <pdf filename> (-o) output.jsonl")

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    
    if "-f" in opts:
        filename = args[0] # Only one argument
 #       process(filename[0])
        logging.debug(f"Filename: {filename}")
    # Do the processing
    final_df = process(filename)
    # End of processing
    if "-o" in opts:
        output_file = args[1]
        logging.debug(f"Output File: {output_file}")
        final_df.to_json(output_file, orient='records', lines=True) 
    else:
        print(final_df.to_json(orient='records', lines=True))          
        