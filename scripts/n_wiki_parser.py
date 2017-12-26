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
n = 1 #number of articles

#helper functions

#Preprocess the paragraph - remove all superscripts
def removeSup(soupOb):
    references = soupOb.find_all('sup', recursive = False)
    for refer in references:
        throwOut = soupOb.sup.extract()

#parse paragraph, print to the console, and write to a file.
#Build the affordance distribution
def process_paragraph(txt: str) -> None:
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

        if (token.dep_ == 'dobj' and token.pos_ == 'NOUN' and token.head.pos_ == 'VERB'):
            print('An affordance was added to the dictionary for a sentence structure w/dobj')
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

#download one page, break into paragraphs, parse, print, and save. build affordance distribution.
def one_page():
    url = "https://en.wikipedia.org/wiki/Special:Random"
    # url = "https://en.wikipedia.org/wiki/Polyp" example to deal with special characters that unicode can't represent which sometimes show up in wikipedia
    # url = "https://en.wikipedia.org/wiki/CBC-MAC" example of gibberish from spn tags

    # download the url
    response = requests.get(url)
    html = response.text
    print("The type of the html variable is:" + str(type(html)))
    soup = bs4.BeautifulSoup(html, "html.parser")

    #get the body of the article
    content_div = soup.find(id="mw-content-text").find(class_="mw-parser-output")

    #get all of the paragraph tags
    allPs = content_div.find_all('p',recursive = False)

    #print the article
    print("ARTICLE NUMBER: " + str(i) + "\n")
    f.write("\nARTICLE NUMBER: " + str(i) + "\n")
    paraNum = 0
    for para in allPs:
        # throw out all superscripts
        removeSup(para)
        paraNum += 1
        #Improvement to implement later: Try to throwout all span tags. (To get rid of the math nonsense)

        #process one paragraph
        try:
            texts = para.get_text()
            if(texts != ""):
                print(texts) #print paragraph to console
                f.write(texts) #print paragraph to a file
                print("We are analyzing the " + str(paraNum) + " paragrah")
                process_paragraph(texts) #parse the sentence, build affordance distribution, print parse
        except UnicodeEncodeError:
            print("dog submarine rick mantissa")
        print()
        f.write("\n")

#body
if __name__ == '__main__':
    all_affordances = {} # collection of affordance distributions

    # save each paragraph and its parse to a file.
    with open('..\\output\\n_wiki_pages','w') as f:
        for i in range(0,n):
            one_page() #Download article, parse, print, save, and build distributions.
            time.sleep(2)

    # save the affordances disctionary
    with open('..\\output\\all_affordances.p','wb') as g:
        pickle.dump(all_affordances, g)

    # examine the affordance dictionary
    print("what does my all_afforances dictionary look like?")
    for thing in all_affordances:
        print(thing)
        for affordance in all_affordances[thing]:
            print("\t" + affordance + " : " + str(all_affordances[thing][affordance]))
