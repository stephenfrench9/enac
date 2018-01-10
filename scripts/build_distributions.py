import re
import time
import spacy
import pickle
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES

#global objects
sp = spacy.load('en_core_web_sm')
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
wikiDumpAddress = 'E:\enwiki-latest-pages-articles.xml'
lines_to_process = 10000 #how many lines in the wikiDump should we process?

#dictionary to hold all of the affordances
all_affordances = {}

# modifies "all_affordances"
#input: A string from which affordances will be extracted.
def process_paragraph(txt: str) -> None:
    parse = sp(txt)

    for token in parse:

        if (token.dep_ == 'dobj' and token.pos_ == 'NOUN' and token.head.pos_ == 'VERB'):
            # print('An affordance was added to the dictionary for a sentence structure w/dobj')
            # print(str(token) + ":" + str(token.head))
            addAffordance(str(token), str(token.head))

        if (token.dep_ == 'nsubjpass' and token.pos_ == 'NOUN' and token.head.pos_ == 'VERB'):
            # print('An affordance was added to the dictionary for a passive sentence structure')
            # print(str(token) + ":" + str(token.head))
            addAffordance(str(token), str(token.head))

# modifies "all_affordances"
# input: An affordance pair
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

# input: "thisString" is text to be modified. "options" is
# regular expression to locate text to be replaced.
# Returns: a modified string.
def optionsSub(thisString,options):
    a = options.findall(thisString)
    for option in a:
        # print("The option is: " + option)
        secondThing = re.compile("\|.*?\]")
        m = secondThing.search(option)
        if m:
            # print("the second half of the option is: " + m.group(0)[1:-1])
            thisString = thisString.replace(option, m.group(0)[1:-1])
        else:
            # print("We choose: " + option[2:-2])
            thisString = thisString.replace(option, option[2:-2])
    return thisString

# input: cleans "thisString".
# ouput: returns a cleaned version of "thisString"
def clean(thisString):
    # references
    ref1 = re.compile("&lt;ref&gt;.*?&lt;/ref&gt;")
    thisString = ref1.sub("", thisString)
    ref2 = re.compile("&lt;ref.*?&gt;.*?&lt;/ref&gt;")
    thisString = ref2.sub("",thisString)
    hangingRef = re.compile("&lt;ref&gt;.*$")
    thisString = hangingRef.sub("", thisString)
    hangingRef2 = re.compile("&lt;ref.*?&gt;")
    thisString = hangingRef2.sub("",thisString)

    # everything else
    quotes = re.compile("&....;")
    options = re.compile("\[\[.*?\]\]")
    funky = re.compile("&amp;nbsp;")
    foreign_words = re.compile("{{lang.*?}}") #might not be needed if running python 3
    EMDashes = re.compile("\â\€\”.*?\â\€\”")
    otherEMDashes = re.compile("\â\€\“")
    excessiveCitations = re.compile("{{.*?}}")
    # hangingCurly = re.compile("{{[^\.]*?$")
    # exoticAlphabet = re.compile("{{lang.*?}}")

    # make replacements
    thisString = quotes.sub("\"", thisString, count = 0)
    thisString = optionsSub(thisString,options)
    thisString = funky.sub("",thisString)
    thisString = foreign_words.sub("foreign word",thisString)
    thisString = EMDashes.sub(" ",thisString)
    thisString = otherEMDashes.sub("-",thisString)
    thisString = excessiveCitations.sub("",thisString)
    # thisString = hangingCurly.sub("SCAROFCURLY",thisString)
    # thisString = exoticAlphabet.sub("foreign word",thisString)
    return(thisString)

# Should we clean the line?
def cleanable(line):
    keep = True

    if(len(line) < 200):
        keep = False
    elif(line[0] == ' '):
        keep = False
    elif(line[0] == '&'):
        keep = False
    elif( line[0] == '<' ):
        keep = False
    elif(line[0:2] == '{{'):
        keep = False
    elif(line[0:3] == '==='):
        keep = False
    elif(line[0:6] == '[[File'):
        keep = False
    elif(line[0] == '*'):
        keep = False
    elif(line[0] == '|'):
        keep = False
    elif( 'Ã' in line ):
        keep = False
    elif( '<' in line and '>' in line):
        keep = False
    elif( '|url' in line):
        keep = False
    return(keep)

# Should we keep the cleaned line?
def keep(line):
    like = True
    if('&lt' in line):
        like = False
    elif ( len(line) < 100):
        like = False
    elif( '{' in line):
        like = False
    return like

if __name__ == '__main__':
    f = open(wikiDumpAddress)
    startTime = time.time()
    reg = re.compile('&quot;')

    # READ and Analyze.
    linesProcessed = 0
    line = True
    while line:
        if linesProcessed == lines_to_process:
            break
        try:
            line = f.readline()
            # if linesProcessed < 0:
            #     linesProcessed += 1
            #     continue
            if cleanable(line):
                line = clean(line)
                if keep(line):
                    if(line[0] == ':'):
                        line = line[1:]
                    if(line[0] == ":"):
                        line = line[1:]
                    process_paragraph(line)
        except UnicodeDecodeError: # occurs more often in python 3
            line = True
        linesProcessed += 1


    f.close()
    finishTime = time.time()

    # print("what does my all_afforances dictionary look like?")
    # for thing in all_affordances:
    #     print(thing)
    #     for affordance in all_affordances[thing]:
    #         print("\t" + affordance + " : " + str(all_affordances[thing][affordance]))


    print("Number of things (affordance distributions): " + str(len(all_affordances)))
    print("The program took this long: " + str(finishTime - startTime))
    print("The program processed this many lines: " + str(linesProcessed))
    linesPerSecond = linesProcessed/(finishTime - startTime)
    print("Lines Processed per second is: " + str(linesPerSecond))
    print("Number of lines processed: " + str(linesProcessed))

    with open('..\\..\\all_affordances.p','wb') as g:
        pickle.dump(all_affordances, g)


# NOTES: I have had some trouble reading from the xml file.
# It would work in python2, sometimes printing characters incorrectly.
# It would not work in python 3. It would read and print for while, then throw UnicodeDecodeError.
# The decode error gets thrown when calling a print command. If I catch the error, it will print
# most lines successfully. (All?) Letters with accents are printed incorrectly (no error thrown).

# # SIMPLY READ.
# linesProcessed = 0
# for line in f:
#     if linesProcessed == 1000:
#         break
#     print("FROM THE E:\ DRIVE and  there are " + str(linesProcessed) + " previous lines")
#     print(line)
#     print()
#     linesProcessed += 1
# #WORKS IN PYTHON2 - YES
# #WORKS IN PYTHON3 - NO NO NO

# #SIMPLY READ.
# linesProcessed = 0
# for line in f:
#     if linesProcessed == 1000:
#         break
#     print("FROM THE E:\ DRIVE and  there are " + str(linesProcessed) + " previous lines")
#     print(line.encode('utf-8'))
#     print()
#     linesProcessed += 1
# #WORKS IN PYTHON2 - DONT KNOW OR CARE
# #WORKS IN PYTHON3 - NO NO NO
