""" Read through a wikidump xml file and find all of the affordances.
    Add all the affordances to a dictionary.
    write that dictionary to a pickle file.
"""

import re
import time
import spacy
import pickle
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import argparse

# global objects
sp = spacy.load('en_core_web_sm')
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

# dictionary to hold all of the affordances
all_affordances = {}


def process_paragraph(txt: str) -> None:
    """ parse a sentence and add all the affordances found
        in that sentence to a dictionary.

        txt -- A string which will be searched for affordances.
        all_affordances -- a dictionary of all the discovered affordances.
    """

    try:
        parse = sp(txt)
        for token in parse:

            if (token.dep_ == 'dobj' and token.pos_ == 'NOUN'
               and token.head.pos_ == 'VERB'):
                # print('An affordance was added to the dictionary for a
                # sentence structure w/dobj')
                # print(str(token) + ":" + str(token.head))
                addAffordance(str(token), str(token.head))

            if (token.dep_ == 'nsubjpass' and token.pos_ == 'NOUN'
               and token.head.pos_ == 'VERB'):
                # print('An affordance was added to the dictionary for a
                # passive sentence structure')
                # print(str(token) + ":" + str(token.head))
                addAffordance(str(token), str(token.head))
    except MemoryError:
        print("There was a memory error while we tried to parse a sentence. \
         Just skipped the one sentence.")


def addAffordance(thing, affordance):
    """ Add an affordance pair to the affordance dictionary

        positional arguments:
        thing -- the object in the affordance pair.
        affordance -- the affordance provided by the object.
    """

    lemmas = lemmatizer(affordance, 'VERB')
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
def optionsSub(thisString, options):
    """ Remove and replace text in a wikicode string

        positional arguments:
        thisString -- wikicode string to be modified
        options -- regex to locate parts of the string
        that look like [[...|...]]
    """
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
    thisString = ref2.sub("", thisString)
    hangingRef = re.compile("&lt;ref&gt;.*$")
    thisString = hangingRef.sub("", thisString)
    hangingRef2 = re.compile("&lt;ref.*?&gt;")
    thisString = hangingRef2.sub("", thisString)

    # everything else
    quotes = re.compile("&....;")
    options = re.compile("\[\[.*?\]\]")
    funky = re.compile("&amp;nbsp;")
    foreign_words = re.compile("{{lang.*?}}")  # maybe not needed if python 3
    EMDashes = re.compile("\â\€\”.*?\â\€\”")
    otherEMDashes = re.compile("\â\€\“")
    excessiveCitations = re.compile("{{.*?}}")
    # hangingCurly = re.compile("{{[^\.]*?$")
    # exoticAlphabet = re.compile("{{lang.*?}}")

    # make replacements
    thisString = quotes.sub("\"", thisString, count=0)
    thisString = optionsSub(thisString, options)
    thisString = funky.sub("", thisString)
    thisString = foreign_words.sub("foreign word", thisString)
    thisString = EMDashes.sub(" ", thisString)
    thisString = otherEMDashes.sub("-", thisString)
    thisString = excessiveCitations.sub("", thisString)
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
    elif(line[0] == '<'):
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
    elif('Ã' in line):
        keep = False
    elif('<' in line and '>' in line):
        keep = False
    elif('|url' in line):
        keep = False
    return(keep)


# Should we keep the cleaned line?
def keep(line):
    like = True
    if('&lt' in line):
        like = False
    elif (len(line) < 100):
        like = False
    elif('{' in line):
        like = False
    return like


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read and parse a wiki dump')
    parser.add_argument('Wikidump_Address', metavar='A', type=str, nargs=1,
                        help='The address for the dump file')
    parser.add_argument('--num_lines', metavar='N', type=int, nargs=1,
                        default=[-1], help='The number of lines to process \
                        from the wikidump. A value of -1 means the entire \
                        dump will be processed. The default is to process the \
                        entire dump.')
    args = parser.parse_args()

    # decode with a utf-8 scheme. Throws no UnicodeDecodeError. accents
    # are printed correctly.
    f = open(args.Wikidump_Address[0], encoding='utf-8')
    startTime = time.time()
    prevTime = startTime
    reg = re.compile('&quot;')

    # READ and Analyze.
    linesProcessed = 0
    line = True
    while line:
        if linesProcessed == args.num_lines[0]:
            break

        try:
            line = f.readline()

            if cleanable(line):
                line = clean(line)
                if keep(line):
                    if(line[0] == ':'):
                        line = line[1:]
                    if(line[0] == ":"):
                        line = line[1:]
                    print(line)
                    process_paragraph(line)
        except UnicodeDecodeError:  # occurs more often in python 3
            line = True
        linesProcessed += 1

        if linesProcessed % 100000 == 0:
            print(linesProcessed)
            print(time.time() - prevTime)
            prevTime = time.time()

    f.close()
    finishTime = time.time()

    # print("what does my all_afforances dictionary look like?")
    # for thing in all_affordances:
    #     print(thing)
    #     for affordance in all_affordances[thing]:
    #         print("\t" + affordance + " : " +
    #                                str(all_affordances[thing][affordance]))
    print("Number of things (affordance distributions): " +
          str(len(all_affordances)))
    print("The program took this long (seconds): " +
          str(finishTime - startTime))
    print("The program processed this many lines: " + str(linesProcessed))
    linesPerSecond = linesProcessed/(finishTime - startTime)
    print("Lines Processed per second is: " + str(linesPerSecond))
    print("Number of lines processed: " + str(linesProcessed))

    with open('..\\..\\all_affordances.p', 'wb') as g:
        pickle.dump(all_affordances, g)


# NOTES: I have had some trouble reading from the xml file.
# It would work in python2, sometimes printing characters incorrectly.
# It would not work in python 3. It would read and print
# for while, then throw UnicodeDecodeError.
# The decode error gets thrown when calling a print command.
# If I catch the error, it will print
# most lines successfully. (All?) Letters with accents are
# printed incorrectly (no error thrown).

# # SIMPLY READ.
# linesProcessed = 0
# for line in f:
#     if linesProcessed == 1000:
#         break
#     print("FROM THE E:\ DRIVE and  there are " + str(linesProcessed)
#  + " previous lines")
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
#     print("FROM THE E:\ DRIVE and  there are " +
#                                   str(linesProcessed) + " previous lines")
#     print(line.encode('utf-8'))
#     print()
#     linesProcessed += 1
# #WORKS IN PYTHON2 - DONT KNOW OR CARE
#   #WORKS IN PYTHON3 - NO NO NO
