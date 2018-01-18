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
from multiprocessing import Pool

# global objects
sp = spacy.load('en_core_web_sm')
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)


def process_paragraph(txt: str, all_affordances: dict):
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
                add_affordance(str(token), str(token.head), all_affordances)

            if (token.dep_ == 'nsubjpass' and token.pos_ == 'NOUN'
               and token.head.pos_ == 'VERB'):
                # print('An affordance was added to the dictionary for a
                # passive sentence structure')
                # print(str(token) + ":" + str(token.head))
                add_affordance(str(token), str(token.head), all_affordances)
    except MemoryError:
        print("There was a memory error while we tried to parse a sentence. \
         Just skipped the one sentence.")


def pool_process_paragraph(txt):
    """Find all the affordances inside a line. Put those affordances in
       a list. First add the "thing", and then add the "affordance"

       positional arguments:
       txt -- text from which affordances will be extracted
    """

    list_of_affs = []
    try:
        parse = sp(txt)
        for token in parse:

            if (token.dep_ == 'dobj' and token.pos_ == 'NOUN'
               and token.head.pos_ == 'VERB'):
                # print('An affordance was added to the dictionary for a
                # sentence structure w/dobj')
                # print(str(token) + ":" + str(token.head))
                list_of_affs.append(str(token))
                list_of_affs.append(str(token.head))

            if (token.dep_ == 'nsubjpass' and token.pos_ == 'NOUN'
               and token.head.pos_ == 'VERB'):
                # print('An affordance was added to the dictionary for a
                # passive sentence structure')
                # print(str(token) + ":" + str(token.head))
                list_of_affs.append(str(token))
                list_of_affs.append(str(token.head))
    except MemoryError:
        print("There was a memory error while we tried to parse a sentence. \
         Just skipped the one sentence.")
    return list_of_affs


def add_affordance(thing, affordance, all_affordances):
    """ Add an affordance pair to the affordance dictionary

        positional arguments:
        thing -- the object in the affordance pair.
        affordance -- the affordance provided by the object.
        all_affordances -- the dictionary with all the affordances
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


def options_sub(this_string, options):
    """ Remove and replace text in a wikicode string

        positional arguments:
        this_string -- wikicode string to be modified
        options -- regex to locate parts of the string
        that look like [[...|...]]

        Return a modified string
    """
    a = options.findall(this_string)
    for option in a:
        # print("The option is: " + option)
        secondThing = re.compile("\|.*?\]")
        m = secondThing.search(option)
        if m:
            # print("the second half of the option is: " + m.group(0)[1:-1])
            this_string = this_string.replace(option, m.group(0)[1:-1])
        else:
            # print("We choose: " + option[2:-2])
            this_string = this_string.replace(option, option[2:-2])
    return this_string


def clean(this_string):
    """Remove all wikimarkup text from a line
       from a wikidump.

       Returns a string that can be read as natural text.

       positional arguments:

       this_string -- line from a wikidump.
    """
    regex_and_replacements = {

        # "&lt;ref&gt;.*?&lt;/ref&gt;" : "", # ref

        "&lt;ref.*?&gt;.*?&lt;/ref&gt;": "",  # same as ref?

        "&lt;ref&gt;.*$": "",  # hangingref

        "&lt;ref.*?&gt;": "",  # hangingref2

        "&amp;nbsp;": "",  # unknown

        "{{.*?}}": "",  # excessive citations

        "&....;": "\"",  # quotes

        # "{{lang.*?}}" : "foreign word", #maybe not needed in python 3 used

        # "\â\€\“" : "-", # other EMdashes

        # "\â\€\”.*?\â\€\”" : " ", # EMdashes

    }

    for regex_template in regex_and_replacements.keys():
        regex = re.compile(regex_template)
        this_string = regex.sub(regex_and_replacements[regex_template],
                               this_string)

    options = re.compile("\[\[.*?\]\]")
    this_string = options_sub(this_string, options)

    return(this_string)


def successfully_cleaned(line):
    """ Decide if the line has been successfully cleaned.

        Return false if the line is not clean.
    """

    cleaned = True
    if('&lt' in line):
        cleaned = False
    elif (len(line) < 150):
        cleaned = False
    elif('{' in line):
        cleaned = False
    return cleaned


def article_text(some_text_from_wikidump):
    """ Analyze a line from a wikidump file and decide if it
        is text from the article body.

        Return True if it is text.
    """

    is_text = True
    first_char = line[0]
    forbidden_first_char = [
        " ",
        "{",
        "}",
        "|",
        "=",
        "[",
        "]",
        "*",
        '<'
    ]
    if len(line) < 10:
        is_text = False
    elif first_char in forbidden_first_char:
        is_text = False
    return(is_text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read and parse a wiki dump')
    parser.add_argument('wikidump_address', metavar='A', type=str, nargs=1,
                        help='The address for the dump file')
    parser.add_argument('--num_lines', metavar='N', type=int, nargs=1,
                        default=[-1], help='The number of lines to process \
                        from the wikidump. A value of -1 means the entire \
                        dump will be processed. The default is to process the \
                        entire dump.')
    args = parser.parse_args()

    # dictionary to hold all of the affordances
    all_affordances = {}

    # decode with a utf-8 scheme. Throws no UnicodeDecodeError. accents
    # are printed correctly.
    f = open(args.wikidump_address[0], encoding='utf-8')
    start_time = time.time()
    prev_time = start_time

    # READ and Analyze.
    lines_processed = 0
    line = True
    many_lines = []
    my_pool = Pool()

    while line:
        if lines_processed == args.num_lines[0]:
            break

        try:
            line = f.readline()
            if line and article_text(line):
                line = clean(line)
                if successfully_cleaned(line):
                    # process_paragraph(line, all_affordances)
                    many_lines.append(line)
                    if len(many_lines) == 2:
                        # for indx, line in enumerate(many_lines):
                        #     print(indx)
                        #     print(line)


                        affordances_from_lines = my_pool.map(pool_process_paragraph, many_lines)


                        # print(affordances_from_lines)
                        # for indx, affs in enumerate(affordances_from_lines):
                        #     print(indx)
                        #     print(affs)


                        for affordances_from_line in affordances_from_lines:
                            while len(affordances_from_line) > 0:
                                an_affordance = affordances_from_line.pop()
                                a_thing = affordances_from_line.pop()
                                # print("thing: " + a_thing)
                                # print("affordance: " + an_affordance)
                                add_affordance(a_thing, an_affordance, all_affordances)
                        many_lines = []
        except UnicodeDecodeError:  # occurs more often in python 3
            print("UNICODE DECODE ERROR")
            line = True

        lines_processed += 1
        if lines_processed % 100000 == 0:
            print(lines_processed)
            print(time.time() - prev_time)
            prev_time = time.time()


    my_pool.close()
    my_pool.join()


    f.close()
    finishTime = time.time()

    print("Number of things (affordance distributions): " +
          str(len(all_affordances)))
    print("The program took this long (seconds): " +
          str(finishTime - start_time))
    print("The program processed this many lines: " + str(lines_processed))
    lines_per_second = lines_processed/(finishTime - start_time)
    print("Lines Processed per second is: " + str(lines_per_second))
    print("Number of lines processed: " + str(lines_processed))

    with open('..\\..\\all_affordances.p', 'wb') as g:
        pickle.dump(all_affordances, g)

# Note: You are handling references incorrectly. Some of them get split across
# lines. It'd take probably an hour to fix it. You currently get rid of lines
# that start mid referece but you keep lines that end mid references. You could
# get rid of both. Or, keep both and let spacy handle some fragments, or, knit
# the lines back together. Up to you.
