import os
import lxml
from lxml import html, etree
import requests
import re
import unidecode as ud
from io import StringIO, BytesIO
import textdistance as td

mylist = ["0B", "0C", "0D", "0E","0F", "1A","01", "02","03", "04","05", "06","07", "08","09", "10","11", "12","13", "14","15", "16", "17", "18", "19"]

def browse_xml(list = mylist):

    rif = {}
    for filename in list:
        xml_name = './zax_rif_ita_min_002/{}.xml'.format(filename)
        tree = etree.parse(xml_name)
        root = tree.getroot()
        #reg = re.compile()
        for voce in root:
            #print(voce)
            for i in voce:
                #defin = []
                if i.tag == "lemma" or i.tag =="sottolemma":
                    sottolemma = i.text
                    rif[sottolemma] = []
                elif i.tag == "def":
                    #i.tag != "sottolemma":
                        rif[sottolemma].append(i.text)
                else:
                    pass
                    #rif[sottolemma] = defin


    return rif

lemmas_all = sorted(browse_xml().keys())
lemmas = lemmas_all[0:10]

def get_entry(lemmi = lemmas): #YEEEEE

    '''unc = re.compile(r">+")
    with codecs.open("dorso.txt", "r", encoding='utf-8', errors='ignore') as f:
        text = f.readlines()
    list = []
    for line in text:
        list.append(unc.sub('', line.split()[0]).strip())
    #de_mauro = {}
    #beg = re.compile(r'\n\s*')
    #end = re.compile(r"\s*\'")
    '''
    de_mauro = {}
    for word in lemmi:
        print("Sto cercando la parola '{}'".format(word))

        page = requests.get('https://dizionario.internazionale.it/parola/{}'.format(ud.unidecode(word)))
        print(page)
        tree = html.fromstring(page.content)
        de_mauro[word] = " ".join(tree.xpath('//section[@id="descrizione"]/text()')).strip()
    return de_mauro

rf = {
"deformante":	"che altera l'aspetto, deturpante",
"formante":	"elemento che, aggiunto a un radicale, forma un tema verbale o nominale",
"fuggente":	"che fugge, che trascorre o si dilegua velocemente",
"funzione":	"(biol.) attività propria di una cellula, di un organo o di un insieme di organi, (ling.) ruolo svolto da un elemento linguistico all'interno di una frase, (mat.) rapporto che lega due termini variabili, quando uno varia in seguito alle variazioni dell'altro, (log. mat.) operazione che, applicata a elementi di un insieme (argomenti), dà come risultato un elemento (valore) dello stesso o di un altro insieme, (chim.) insieme delle proprietà chimiche e fisiche caratteristiche dei composti organici nella cui molecola siano presenti gruppi atomici responsabili di tali proprietà",
"indenne":	"nel linguaggio tecnico e scientifico, immune da contagio o da processi infettivi",
"insetto":	"piccolo animale invertebrato con sei zampe, spesso alato, come per es. la formica, la mosca, la farfalla, l'ape, lo scarafaggio, ecc., (entom.) artropode della classe degli Insetti",
"preziosità":	"l'essere prezioso",
"rastremare":	"affinare, rendere più sobrio uno stile letterario",
"gorgo": "punto in cui il letto di un corso d'acqua, abbassandosi, forma cavità di piccole dimensioni",
"casa": "una definizione a caso"
}

def prova():
    l = sorted(rf.keys())
    dm = get_entry(l)
    joint = {}
    for word in dm:
        joint[word] = [td.jaccard(rf[word].split(),dm[word].split()),rf[word],dm[word]]
    return joint