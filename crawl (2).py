from lxml import html
import requests
import re
from assignment1 import tokenise_stem
import codecs
import xml.etree.ElementTree as ET
import beautifulscraper

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
    with codecs.open(xml_file_name, "r", encoding="utf-8", errors="ignore") as f:
        text = f.readlines()
    RIF = {}
    sottolemmi = []
    #reg_sub = re.compile(r"<sottolemma>(\S*)</sottolemma>(.*)</grado>")
    for line in text:
        mj = re.compile(r"<sottolemma>(\S*)</sottolemma>(.*)</grado>")
        #sottolemmi.append(reg_sub.findall(line))
        sottolemma = mj.group(1)
        resto = mj.group(2)
        RIF[sottolemma] = resto

        '''for sottolemma in sottolemmi:
             lemma = sottolemma.find("sottolemma").text
             defin = sottolemma.search("def").text
             RIF[lemma] = defin
            #defin = voce.find("def").text
            #RIF[lemma].append(defin)'''
    return RIF


def simple(xml):
    with codecs.open(xml, "r", encoding="utf-8", errors="ignore") as x:
        entry = re.findall(r"(<sottolemma>\S*</sottolemma>.*</def>", x.read())
    return entry