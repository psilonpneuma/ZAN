#! /usr/bin/env python3

import xml.etree.ElementTree as ET
import string
import re
from stemming.porter2 import stem
from collections import defaultdict
from math import log

# TEXT PREPROCESSING

def read_text(filename):
    '''reads in a text from a file, returns text as string'''
    with open(filename, 'r') as f:
        text = f.read()
    return text

def lower(tokens):
    '''lowercasing, works for both words and list of words'''
    if isinstance(tokens, list):
        return [lower(w) for w in tokens]
    else:
        return tokens.lower()

def tokenise_stem(text):
    '''removes punctuation, lowers all the characters and returns a list of all the stemmed words split at space or newline'''
    punct = re.compile('[%s]' % re.escape(string.punctuation))
    dig = re.compile('\d')
    text_clean1 = punct.sub('', text)
    text_clean = dig.sub('0', text_clean1) #convert all digits to 0 to optimize indexing
    tokens = text_clean.split()
    stemmed_tokens = [stem(token) for token in tokens]
    return lower(stemmed_tokens)

def preprocess_token_list(tokens, stop_infile="stop.txt"):
    '''removes stop words from a list of tokens, given a list of stop words from file (default file= stop.txt)'''
    stop_clean = tokenise_stem(read_text(stop_infile))
    tokens_clean = [token for token in tokens if token not in stop_clean]
    return tokens_clean


# INDEXING

def make_collection_matrix(xml_file_name):
    '''parses specified nodes of an input xml file and returns a collection (list) of all documents in the file.
    Each doc is a list composed as follows [docno, [term1, term2, ..., term_n]]'''
    tree = ET.parse(xml_file_name)
    root = tree.getroot()
    collection = []
    doctuple = []
    for document in root.findall("DOC"):
        docno = document.find("DOCNO").text
        doctuple = preprocess_token_list(tokenise_stem(document.find("HEADLINE").text + " " + document.find("TEXT").text))
        doctuple.insert(0, docno)
        collection.append(doctuple)
    return collection

def get_all_word_types(collection):
    '''returns all the word types of a given collection'''
    wordlist = []
    for doc in collection:
        for word in doc[1:]:
         wordlist.append(word)
    print("Number of tokens = ", len(wordlist))
    N = len(wordlist)
    return sorted(set(wordlist))

def get_index(collection):
    '''builds a positional inverted index (dict) from a document collection, with the following structure:
    index = {"word_a":
                    [[docID, [pos1, pos2, ..., pos_n],
                    [docID, [...]],
            "word_b": ...
            }
    '''
    wordlist = get_all_word_types(collection)
    index = {}
    for word in wordlist:
      index_doc = []
      for document in collection:
        #print(document)
        if word in document[1:]:
            print("Processing : {}".format(word))
            temp_list = [document[0], [i for i, x in enumerate(document[1:]) if x == word]] #probably optimize in here!
            index_doc.append(temp_list)
            index["{}".format(word)] = index_doc
    #print("created index for {}".format(xml_file_name))
    return index

def write_index_to_file(index, filename):
    ''' writes an invered index to file with the following output:
    term:
    docID: pos1, pos2, ....
    docID: pos1, pos2, .... '''
    with open(filename, 'w') as f:
        for word in index:
            f.write('{}:\n'.format(word))
            for document in index[word]:
                #pos = [p + 1 for p in index[word][document]]
                f.write('\t{}'.format(document[0]) + ': ' + '{}'.format(document[1]).replace("[", "").replace("]", ""))
                f.write('\n')
            f.write("\n")


# SEARCHING

'''Search execution module that LOADS the inverted index file, and allows: 
- Boolean search 
- Phrase search 
- Proximity search 
- Ranked IR based on TFIDF'''

def get_index_from_file(infile):
    '''loads an index from text file and returns an index with structure = get_index function's output'''
    with open(infile, 'r') as f:
        text = f.read()
        print("reading file")
        text_chunck = text.split('\n\n')
        index = {}
        for chunck in text_chunck:
            entry = chunck.split(':\n\t')
            print("processing word: {}".format(entry[0]))
            for i in entry[1:]:
                document_list = i.split('\n\t')
                all_docs = []
                for doc in document_list:
                    [h, d] = doc.split(": ")
                    pos = list(map(int, d.split(", ")))
                    all_docs.append([int(h), pos])
                index[entry[0]] = all_docs
    return index

def parse_query(query, stop_infile="stop.txt"):
    query = re.findall(r"[\w']+|[\"]", query)
    key_values = ["AND", "OR", "NOT", "\""] # I did not implement the automatic handing of queries, but this can come in handy
    query_list = []
    for word in query:
        if word not in key_values:
            punct = re.compile('[%s]' % re.escape(string.punctuation))
            word = lower(punct.sub('', word))
        query_list.append(word)
    stop_clean = tokenise_stem(read_text(stop_infile))
    query_clean = [token for token in query_list if token not in stop_clean]
    return query_clean

def preprocess_query(query):
    '''returns query as list, with the same preprocessing as the text applied'''
    query = tokenise_stem(query)
    query = preprocess_token_list(query)
    return(query)

def bool_term_search(index, query):
    '''returns a list of documents where the term occurs'''
    query = preprocess_query(query)
    print("searching : ", query)
    doclist = []
    for term in query:
        #print(term, "yes")
        if term in index:
            #print("yes")
            for docs in index[term]:
                #print(index[term])
                doclist.append(docs[0])
        #else:
            #doclist = []
    return doclist

def bool_term_search_withpos(index, query): # not used right now but useful to simplify the ranking
    '''same as term search but returns documents with their positions'''
    query = preprocess_query(query)
    print("searching : ", query)
    doclist = []
    for term in query:
        #print(term, "yes")
        if term in index:
            #print("yes")
            for docs in index[term]:
                #print(index[term])
                doclist.append(docs)
        #else:
            #doclist = []
    return doclist

def bool_AND_search(index, query):
    '''parses a query with more words and returns documents that contain all terms in the query'''
    query = preprocess_query(query)
    docdict = {}
    for term in query:
        docdict[term] = bool_term_search(index, term)
    doclist = list(docdict.values()) #linear merge
    #print(doclist)
    result = (map(int, doclist[0]))
    for l in range(0, len(doclist)-1):
        result = set(result).intersection(map(int, doclist[l+1]))
    return sorted(list(result))

def bool_OR_search(index, query):
    '''parses a query with more words and returns documents that contain at least a term in the query'''
    query = preprocess_query(query)
    docdict = {}
    for term in query:
        docdict[term] = bool_term_search(index, term)
        #print(term, docdict[term])
    doclist = list(docdict.values()) #linear merge
    result = []
    for l in range(len(doclist)-1):
        result += list(map(int, doclist[l])) + list(map(int, doclist[l+1]))
    return sorted(set(result))

def bool_ANDNOT_search(index, query):
    '''parses a query with more owrds and returns documents that contain first term but not second term in the query'''
    query = preprocess_query(query)
    docdict = {}
    for term in query:
        docdict[term] = bool_term_search(index, term)
    doclist = list(docdict.values()) #linear merge
    result = doclist[0]
    for l in range(0, len(doclist)-1):
        result = [i for i in result if i not in doclist[l+1]]
    return sorted(set(result))

def bool_PROXY_search(index, query, dist=1, phrase=True):
    '''encapsulates both proximity and phrase search:
    - with dist=1 and phrase=True: returns documents that contain first term immediately followed by second term
    - with dist=n and phrase=False: returns documents containing both words within a span of n words
    '''
    query = preprocess_query(query)
    docdict = {}
    for term in query:
        docdict[term] = bool_term_search_withpos(index, term)
    doclist = list(docdict.values()) #linear merge
    #print(doclist[0], '\n', doclist[1], '\n', len(doclist))
    result = []
    for termno in range(0, len(doclist)-1):
        d1 = doclist[termno]
        d2 = doclist[termno+1]
        #print(d1, '\n', d2)
        for doc in d1:
            for doc2 in d2:
                if doc[0] == doc2[0]:
                    if phrase:
                        for pos in doc[1]:
                            if pos + dist in doc2[1]:
                                result.append(doc[0])
                    elif not phrase:
                        for pos in doc[1]:
                            for posit in doc2[1]:#print(pos)
                                if abs(pos-posit) <= dist:
                                    result.append(doc[0])
    return sorted(set(result))

def write_results_to_file(results, filename="index.txt"):
    ''' writes quert results to file with the following output, one line for each docID:
    queryID 0 docID 0 1 0
    '''
    with open(filename, 'w') as f:
        for query in results:
            for document in results[query]:
                if document is not []:
                    f.write('{} 0 {} 0 1 0\n'.format(query, document)) #pos = [p + 1 for p in index[word][document]]
                else:
                    f.write('{} 0 {} 0 1 0\n'.format(query, "No matching document"))

def write_for_checking(results, filename="share.txt"):
    ''' writes query results to file with the following output, one line for each docID:
    queryID 0 docID 0 1 0
    '''
    with open(filename, 'w') as f:
        for query in results:
            f.write("Query {} ***********\n".format(query))
            for document in results[query]:
                if document is not []:
                    f.write('{} | '.format(document)) #pos = [p + 1 for p in index[word][document]]

                else:
                    f.write('{} 0 {} 0 1 0\n'.format(query, "No matching document"))
            f.write("\n")

''' BOOLEAN SEARCH
1 Happiness
2 Edinburgh AND SCOTLAND
3 income AND taxes
4 "income taxes"
5 #20(income, taxes)
6 "middle east" AND peace
7 "islam religion"
8 "Financial times" AND NOT BBC
9 "wall street" AND "dow jones"
10 #15(dow,stocks)
'''


def tfidf(index, query, N=5000):
    '''index = {'term': [docno, [pos1, pos2, ...]]}
    N = number of documents in collection
    query = string with one or more terms > for relevance, query is intended of the type "OR" (retrieves docs that contain all the terms)
    returns a score for the query given '''
    #N = len(make_collection_matrix(xml_file_name))
    query_list = preprocess_query(query)
    search_result_list = bool_OR_search(index, query)
    query_weights = {}
    search_result_scores = defaultdict(lambda: 0)
    for term in query_list:
        if term in index:
            doc_list = []
            dft = len(index[term])
            for doc in index[term]:
                doc_id = doc[0]
                tf = len(doc[1])
                wtd = (1+ log(tf, 10))*(log((N/dft), 10))
                doc_tuple = (doc_id, wtd)
                doc_list.append(doc_tuple)
            query_weights[term] = doc_list
    #print(query_weights)
    #print(doc_list)
    for document in search_result_list:
        doc_score = 0
        for term in query_weights:
            #print(term)
            for tuple in query_weights[term]:
                if document == tuple[0]:
                    doc_score += tuple[1]
        search_result_scores[document] = doc_score
    sorted_dict = [(k, search_result_scores[k]) for k in sorted(search_result_scores, key=search_result_scores.get, reverse=True)]
    return sorted_dict

def write_ranked_results_to_file(tfidf_scores_dict, filename="index.txt"):
    '''writes a line onto file for each query, with the following output:
    queryID 0 docID 0 score 0
    '''
    with open(filename, 'w') as f:
        for query in tfidf_scores_dict:
            for document in tfidf_scores_dict[query]:
                if not document:
                    f.write('{} {}\n'.format(query, "No matching document"))
                else:
                    f.write('{} 0 {} 0 {} 0\n'.format(query, document[0], document[1])) #pos = [p + 1 for p in index[word][document]]



def main():
    print("Hi! this program will automatically build an index from an xml file and will perform several queries, oututting files for easy reference.")
    myindex = get_index_from_file("index.txt")
    results_boolean = {}
    results_boolean[1] = bool_term_search(myindex, "Happiness")
    results_boolean[2] = bool_AND_search(myindex, "Edinburgh AND SCOTLAND")
    results_boolean[3] = bool_AND_search(myindex, "income AND taxes")
    results_boolean[4] = bool_PROXY_search(myindex, "income taxes")
    results_boolean[5] = bool_PROXY_search(myindex, "income taxes", 20, phrase=False)
    mideast = bool_PROXY_search(myindex, "middle east")
    peace = bool_term_search(myindex, "peace")
    results_boolean[6] = [doc for doc in mideast if doc in peace]
    results_boolean[7] = bool_PROXY_search(myindex, "islam religion")
    fintime = bool_PROXY_search(myindex, "Financial times")
    bbc = bool_term_search(myindex, "BBC")
    results_boolean[8] = [doc for doc in fintime if doc not in bbc]
    wall = bool_PROXY_search(myindex, "wall street")
    dow = bool_PROXY_search(myindex, "dow jones")
    results_boolean[9] = [doc for doc in wall if doc in dow]
    results_boolean[10] = bool_PROXY_search(myindex, "dow stocks", dist=15, phrase=False)

    ''' BOOLEAN QUERY SEARCHES
    1 Happiness
    2 Edinburgh AND SCOTLAND
    3 income AND taxes
    4 "income taxes"
    5 #20(income, taxes)
    6 "middle east" AND peace
    7 "islam religion"
    8 "Financial times" AND NOT BBC
    9 "wall street" AND "dow jones"
    10 #15(dow,stocks)
    '''

    write_results_to_file(results_boolean, "results.boolean.txt")

    results_ranking = {}
    results_ranking[1] = tfidf(myindex, "income tax reduction")
    results_ranking[2] = tfidf(myindex, "stock market in Japan")
    results_ranking[3] = tfidf(myindex, "health industry")
    results_ranking[4] = tfidf(myindex, "the Robotics industries")
    results_ranking[5] = tfidf(myindex, "the peace process in the middle east")
    results_ranking[6] = tfidf(myindex, "information retrieval")
    results_ranking[7] = tfidf(myindex, "Dow Jones industrial average stocks")
    results_ranking[8] = tfidf(myindex, "will be there a reduction in the income taxes?")
    results_ranking[9] = tfidf(myindex, "the gold prices versus the dollar price")
    results_ranking[10] = tfidf(myindex, "FT article on the BBC and BSkyB deal")

    write_ranked_results_to_file(results_ranking, "results.ranked.txt")

    ''' RANKED SEARCH
    1 income tax reduction
    2 stock market in Japan
    3 health industry
    4 the Robotics industries
    5 the peace process in the middle east
    6 information retrieval
    7 Dow Jones industrial average stocks
    8 will be there a reduction in the income taxes?
    9 the gold prices versus the dollar price
    10 FT article on the BBC and BSkyB deal
    '''
    print("\nWe are finished! Go to your directory to check the results")

if __name__ == '__main__':
    main()