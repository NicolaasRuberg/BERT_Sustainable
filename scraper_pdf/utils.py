import fitz
import textract
import operator
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Inspired in https://github.com/LouisdeBruijn/Medium/commit/3d9523d9bd5e4bd898a22df1bab9078ddea465b8
def fonts(doc, granularity=False):
    """Extracts fonts and their usage in PDF documents.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param granularity: also use 'font', 'flags' and 'color' to discriminate text
    :type granularity: bool
    :rtype: [(font_size, count), (font_size, count}], dict
    :return: most used fonts sorted by count, font style information
    """
    styles = {}
    font_counts = {}

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if granularity:
                            identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                            styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                  'color': s['color']}
                        else:
                            identifier = float("{0}".format(s['size']))
                            styles[identifier] = {'size': s['size'], 'font': s['font']}
                            
                        rounded_id = round (identifier)
                        font_counts[rounded_id] = font_counts.get(rounded_id, 0) + 1  # count the fonts usage

    font_counts = sorted(font_counts.items(), key=operator.itemgetter(1), reverse=True)
    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")

    return font_counts, styles

def font_tags(font_counts, styles):
    """Returns dictionary with font sizes as keys and tags as value.
    :param font_counts: (font_size, count) for all fonts occuring in document
    :type font_counts: list
    :param styles: all styles found in the document
    :type styles: dict
    :rtype: dict
    :return: all element tags based on font-sizes
    """
    p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
    p_size = p_style['size']  # get the paragraph's size

    # sorting the font sizes high to low, so that we can append the right integer to each tag 
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == p_size:
            idx = 0
            size_tag[size] = '<p>'
        if size > p_size:
            size_tag[size] = '<h{0}>'.format(idx)
        elif size < p_size:
            size_tag[size] = '<s{0}>'.format(idx)

    return size_tag

def headers_para(doc, size_tag):
    """Scrapes headers & paragraphs from PDF and return texts with element tags.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param size_tag: textual element tags for each size
    :type size_tag: dict
    :rtype: list
    :return: pandas dataframe
    """    
    header_para = []  # list with headers and paragraphs
    for page in doc:
        first = True  # boolean operator for first header
        blocks = page.getText("dict")["blocks"]
        block_string = ""  # text found in block
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # this block contains text
                next_s = round(b["lines"][0]["spans"][0]["size"])
                if first:
                    s = next_s
                if block_string != "" :
                    if ((s != next_s) or first or (block_string[-1] in {".","?","!",})):
                        header_para.append([str(s), block_string])
                        block_string =""
                        first = False
                # REMEMBER: multiple sizes are possible IN one block. We are ignoring it..
                for l in b["lines"]:  # iterate through the text lines                
                    for sp in l["spans"]:  # iterate through the text spans
                        if block_string == "":
                            block_string = sp['text'].strip()
                        else:
                            block_string += " " + sp['text'].strip()
                s = next_s
        if block_string != "": 
            header_para.append([s, block_string])
            block_string = ""       

    return header_para

