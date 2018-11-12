import zan
import textdistance as td

dict = {
"deformante":	"che altera l'aspetto, deturpante",
"formante":	"elemento che, aggiunto a un radicale, forma un tema verbale o nominale",
"fuggente":	"che fugge, che trascorre o si dilegua velocemente",
"funzione":	"(biol.) attività propria di una cellula, di un organo o di un insieme di organi, (ling.) ruolo svolto da un elemento linguistico all'interno di una frase, (mat.) rapporto che lega due termini variabili, quando uno varia in seguito alle variazioni dell'altro, (log. mat.) operazione che, applicata a elementi di un insieme (argomenti), dà come risultato un elemento (valore) dello stesso o di un altro insieme, (chim.) insieme delle proprietà chimiche e fisiche caratteristiche dei composti organici nella cui molecola siano presenti gruppi atomici responsabili di tali proprietà",
"indenne":	"nel linguaggio tecnico e scientifico, immune da contagio o da processi infettivi",
"insetto":	"piccolo animale invertebrato con sei zampe, spesso alato, come per es. la formica, la mosca, la farfalla, l'ape, lo scarafaggio, ecc., (entom.) artropode della classe degli Insetti",
"preziosità":	"l'essere prezioso",
"rastremare":	"affinare, rendere più sobrio uno stile letterario"
}

def prova():
    l = sorted(dict.keys())
    e = zan.get_entry(l)
    return e