import re
import time
import spacy
import pickle
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import argparse
from multiprocessing import Pool, Process, Queue, Pipe, Lock, Manager
import queue
import multiprocessing
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


def print_log(label,mssg,lock):
    lock.acquire()
    print(label + mssg)
    lock.release()


def pool_process_paragraph(q,t1,label,start_line,num_lines,lock):
    """Find all the affordances inside a line. Put those affordances in
       a list. First add the "thing", and then add the "affordance"

       positional arguments:
       txt -- text from which affordances will be extracted
    """
    print_log(label, " ..... Execute the first line at " + str(round(time.time()-t1,4)), lock)
    f = open("..\\..\\lines_to_process.txt", 'r',encoding='utf-8')

    for i in range(0,start_line):
        line = f.readline()

    print_log(label, " ...... skipped many lines", lock)
    print_log(label, " ...... about to start reading and parsing lins", lock)
    for _ in range(0,num_lines):
        line = f.readline()
        if len(line) > 1:
            # print(label + line)

            try:
                # print("BEFORE: " + str(time.time()))
                # print(line)
                parse = sp(line)
                print_log(label, " ...... parsed a sentence", lock)
                # print("AFTER: " +str(time.time()))
                for token in parse:

                    if (token.dep_ == 'dobj' and token.pos_ == 'NOUN'
                       and token.head.pos_ == 'VERB'):
                        # print('An affordance was added to the dictionary for a
                        # sentence structure w/dobj')
                        # print(str(token) + ":" + str(token.head))
                        # lock.acquire()
                        toopull = (str(token),str(token.head))
                        print_log(label, " ...... about to place a tuple.", lock)
                        # print(toopull)
                        q.put(toopull)
                        print_log(label, "....... just placed a tuple.", lock)
                        # lock.release()
                    # if (token.dep_ == 'nsubjpass' and token.pos_ == 'NOUN'
                    #    and token.head.pos_ == 'VERB'):
                    #     # print('An affordance was added to the dictionary for a
                    #     # passive sentence structure')
                    #     # print(str(token) + ":" + str(token.head))
                    #     # lock.acquire()
                    #     toopull = (token,token.head)
                    #     q.put(toopull)
                    #     # lock.release()
            except MemoryError:
                print("There was a memory error while we tried to parse a sentence. \
                 Just skipped the one sentence.")
        # elif len(line) == 1:
        #     # print(label + "DEADLINE")
        # elif len(line) == 0:
        #     # print(label + "ZEROLINE")
    q.put("END111END222end3755639")
    print_log(label, " ..... pool_process_paragraph is done at " + str(round(time.time()-t1,4)), lock)


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


def read_q_into_affordances(q,all_affordances):
    while not q.empty():
        a_thing = q.get()
        an_affordance = q.get()
        # print("thing: " + a_thing)
        # print("affordance: " + an_affordance)
        # print(a_thing)
        add_affordance(a_thing, an_affordance, all_affordances)


if __name__=='__main__':

    all_affordances = {}
    check_affordances = {}
    t1 = time.time()

    process_labels = [
        "process_  0  : ",
        "process_  1  : ",
        "process_  2  : "
    ]

    the_man = Manager()
    process_queues = [
        the_man.Queue(),
        the_man.Queue(),
        the_man.Queue()
    ]

    lock = Lock()

    process = [
        Process(target = pool_process_paragraph, args =
                (process_queues[0],t1,process_labels[0],0,50,lock,)),
        Process(target = pool_process_paragraph, args =
                (process_queues[1],t1,process_labels[1],50,50,lock,)),
        Process(target = pool_process_paragraph, args =
                (process_queues[2],t1,process_labels[2],0,100,lock))
    ]

    print(process_labels[0] + "created at time " + str(round(time.time()-t1,4)))
    print(process_labels[1] + "created at time " + str(round(time.time()-t1,4)))
    print(process_labels[2] + "created at time " + str(round(time.time()-t1,4)))




    process[0].start()
    print(process_labels[0] + "started at time " + str(round(time.time()-t1,4)))
    process[1].start()
    print(process_labels[1] + "started at time " + str(round(time.time()-t1,4)))
    process[2].start()
    print(process_labels[2] + "started at time " + str(round(time.time()-t1,4)))
    time.sleep(10)
    # Read into your process from another process.

    target_dict = [all_affordances, all_affordances, check_affordances]
    num_done = 0
    while True:

        for proc_num in range(0,3):
            try:
                print_log(process_labels[proc_num], "about to read from the queue.", lock)
                aff_tuple = process_queues[proc_num].get(True, timeout = .001) # procure an affordance tuple
                print_log(process_labels[proc_num], "got a tuple", lock)
                print_log(process_labels[proc_num], str(aff_tuple), lock)
                if aff_tuple == "END111END222end3755639":
                    num_done += 1
                else:
                    add_affordance(aff_tuple[0],aff_tuple[1], target_dict[proc_num])
            except queue.Empty:
                print_log(process_labels[proc_num], "no tuples found.", lock)

        if num_done == 3:
            break


    proc_num = 0
    process[proc_num].join()
    print(process_labels[proc_num] + "joined at time " + str(round(time.time()-t1,4)))
    # read_q_into_affordances(process_queues[proc_num],all_affordances)

    proc_num = 1
    process[proc_num].join()
    print(process_labels[proc_num] + "joined at time " + str(round(time.time()-t1,4)))
    # read_q_into_affordances(process_queues[proc_num],all_affordances)

    proc_num = 2
    print(process_labels[proc_num] + "joined at time " + str(round(time.time()-t1,4)))
    # read_q_into_affordances(process_queues[proc_num],check_affordances)
    # process[proc_num].join()



    print()
    print()
    print()
    print(all_affordances)
    print()
    print("CHECK AGAINGST SINGLE PROCESS: ")
    print(check_affordances)
