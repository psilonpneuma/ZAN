from lxml import html
import requests
import re
from assignment1 import tokenise_stem
import codecs
import xml.etree.ElementTree as ET
#import beautifulsoup4

def preprocess(string):
    re1 = re.compile(r'(\\n\s+) | (\s){2,}')
    return re1.sub('', string)

def get_entry():
    #list = ["casa", "albero", "aquilone", "booooh", "fiocco", "corteccia", "telefonino", "tastiera", "corteccia", "telefonino", "tastiera", "albero", "aquilone", "booooh", "fiocco", "corteccia", "telefonino", "tastiera", "corteccia", "telefonino", "tastiera"]
    unc = re.compile(r">+")
    with codecs.open("dorso.txt", "r", encoding='utf-8', errors='ignore') as f:
        text = f.readlines()
    list = []
    for line in text:
        list.append(unc.sub('', line.split()[0]).strip())
    #de_mauro = {}
    #beg = re.compile(r'\n\s*')
    #end = re.compile(r"\s*\'")

    de_mauro = {}
    for word in list:
        page = requests.get('https://dizionario.internazionale.it/parola/{}'.format(word))
        tree = html.fromstring(page.content)
        de_mauro[word] = " ".join(tree.xpath('//section[@id="descrizione"]/text()')).strip()
    return de_mauro


def make_collection_matrix(xml_file_name):
    '''parses specified nodes of an input xml file and returns a collection (list) of all documents in the file.
    Each doc is a list composed as follows [docno, [term1, term2, ..., term_n]]'''
    tree = ET.parse(xml_file_name)
    root = tree.getroot()
    RIF = {}
    reg_sub = re.compile("<sottolemma>.+</grado>")
    for voce in root.findall("voce"):
        reg_sub = re.compile(r"<sottolemma>.+</grado>")
        sottolemmi = reg_sub.findall("voce")
        for sottolemma in sottolemmi:
             lemma = sottolemma.find("sottolemma").text
             defin = sottolemma.search("def").text
             RIF[lemma] = defin
            #defin = voce.find("def").text
            #RIF[lemma].append(defin)
    return RIF