# imports
import requests
import bs4
import time
import spacy
import pickle

from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES

#global variables
sp = spacy.load('en_core_web_sm')
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)



#helper functions
def removeSup(soupOb):
    references = soupOb.find_all('sup', recursive = False)
    for refer in references:
        throwOut = soupOb.sup.extract()

def disp_sentence(txt: str) -> None:
    parse = sp(txt)

    for token in parse:

        print('{: >2} {: <12} {: <10} ({})'.format(
            token.i,
            '{}/{}'.format(token.dep_, token.head.i),
            str(token),
            token.pos_))

        f.write("\n")
        f.write('{: >2} {: <12} {: <10} ({})'.format(
                    token.i,
                    '{}/{}'.format(token.dep_, token.head.i),
                    str(token),
                    token.pos_))

        # accumalte counts for parts of speech in the array pos_counts, which has a global scope apparently

        if (token.dep_ == 'dobj' and token.pos_ == 'NOUN' and token.head.pos_ == 'VERB'): # and token.head == 'ROOT' and token.head.pos_ == 'VERB'):
            print(token.pos_)
            print(type(token.pos_))
            print()
            print(token.dep_)
            print(type(token.dep_))
            print()
            print(str(token.head))
            print(type(str(token.head)))
            print()
            print(token.head.pos_)
            print(type(token.head.pos_))
            print('the added will be')
            print(str(token) + ":" + str(token.head))
            addAffordance(str(token), str(token.head))

    print()
    f.write("\n")

def addAffordance(thing, affordance):
    lemmas = lemmatizer(affordance,'VERB')
    affordance = lemmas[0]
    if all_affordances.get(thing):
        if all_affordances.get(thing).get(affordance):
            all_affordances.get(thing)[affordance] += 1
        else:
            all_affordances.get(thing)[affordance] = 1
    else:
        all_affordances[thing] = dict()
        all_affordances[thing][affordance] = 1



#download, break into paragraphs, parse with respect to syntax, and accumulate statistics
def one_page():

    url = "https://en.wikipedia.org/wiki/Special:Random"
    # url = "https://en.wikipedia.org/wiki/Polyp" example to deal with special characters that unicode can't represent which sometimes show up in wikipedia
    # url = "https://en.wikipedia.org/wiki/CBC-MAC" example of gibberish from spn tags

    # download the url
    response = requests.get(url)
    html = response.text
    soup = bs4.BeautifulSoup(html, "html.parser")

    #get the body of the article
    content_div = soup.find(id="mw-content-text").find(class_="mw-parser-output")

    #get all of the paragraph tags
    allPs = content_div.find_all('p',recursive = False)

    #print the article
    print("ARTICLE NUMBER: " + str(i) + "\n")
    f.write("\nARTICLE NUMBER: " + str(i) + "\n") #this function is called in a scope which has a varible 'f'
    for para in allPs:
        # throw out all superscripts
        removeSup(para)

        #Try to throwout all span tags? Get rid of the maths nonsenses

        #print a paragraph
        try:
            texts = para.get_text()
            if(texts != ""):
                print(texts) #print to the console
                f.write(texts) #f exists in the scope of the calling function
                disp_sentence(texts) #parse the sentence (apply dependency labels), count parts of speech, save to a global variable that
                                        #the function has access to.
        except UnicodeEncodeError:
            print("dog submarine rick antissima")
        print()
        f.write("\n")

#body
if __name__ == '__main__':
    #gather and print the data
    all_affordances = {}

    with open('n_wiki_pages','w') as f:
        for i in range(0,100):
            one_page() #This function downloads article, cleans it, prints it, saves to a file. Also, accumaltes statistics about the file,
                        #which are saved in an array called pos_counts
                        #Is this array which is declared in the child scope accessibel to the parent scope?
            time.sleep(2)

    #save that array that was created earlier
    with open('all_affordances.p','wb') as g:
        pickle.dump(all_affordances, g)

    print("what does my all_afforances dictionary look like?")
    for thing in all_affordances:
        print(thing)
        for affordance in all_affordances[thing]:
            print("\t" + affordance + " : " + str(all_affordances[thing][affordance]))
