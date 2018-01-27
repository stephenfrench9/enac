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


def pool_process_paragraph(q,t1,label,file_location,total_groups,lock,group_size,process_num):
    """Find all the affordances inside a line. Put those affordances in
       a list. First add the "thing", and then add the "affordance"

       positional arguments:
       txt -- text from which affordances will be extracted
    """
    print_log(label, " ..... Execute the first line at " + str(round(time.time()-t1,4)), lock)
    f = open(file_location, 'r',encoding='utf-8')


    print_log(label, " ...... about to start reading and parsing lins", lock)
    print_log(label, " ...... the total number of groups is: " + str(total_groups), lock)
    line = f.readline()
    group_num = 0
    line_num = 0
    while line:

        if group_num == total_groups:
            break
        if line_num == process_num:
            try:
                parse = sp(line)
                print_log(label, " ...... parsed a sentence", lock)
                print_log(label, " ...... line_num is: " + str(line_num),lock)
                print_log(label, " ...... group_num is: " + str(group_num),lock)
                print_log(label, line, lock)
                # print_log(label, " ...... line_num is: " + str(line_num), lock)
                # print_log(label, " ...... group_num is: " + str(group_num), lock)
                for token in parse:

                    if (token.dep_ == 'dobj' and token.pos_ == 'NOUN'
                       and token.head.pos_ == 'VERB'):
                        toopull = (str(token),str(token.head))
                        # print_log(label, " ...... about to place a tuple.", lock)
                        q.put(toopull)
                        # print_log(label, "....... just placed a tuple.", lock)
                    # if (token.dep_ == 'nsubjpass' and token.pos_ == 'NOUN'
                    #    and token.head.pos_ == 'VERB'):
                    #     toopull = (token,token.head)
                    #     q.put(toopull)
            except MemoryError:
                print("There was a memory error while we tried to parse a sentence. \
                 Just skipped the one sentence.")

        if line_num == (group_size - 1):
            group_num += 1
            line_num = 0
            line = f.readline()
        else:
            line_num += 1
            line = f.readline()


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

    parser = argparse.ArgumentParser(description='Read and parse txt doc \
                                     generated by generate_intermediate_text.\
                                     py. Identify affordances with in the text \
                                     and read them into a dictionary. Print \
                                     that dictionary.\
                                     ')
    parser.add_argument('intermediate_text_address', metavar='A', type=str,
                        nargs=1, help='The address for the file with text to \
                        search for affordances. This file is generated by \
                        generate_intermediate_text.py')
    parser.add_argument('--num_lines', metavar='N', type=int, nargs=1,
                        default=[-1], help='The number of lines to process \
                        from the intermediate_text. A value of -1 means the \
                        entire dump will be processed. The default is to \
                        process the entire dump.')
    parser.add_argument('--num_processes', metavar='P', type=int, nargs=1,
                        default=[1], help='The number of process objects the\
                        script will use.')
    args = parser.parse_args()

    print("intermediate_text_address argument has the value: " + args.intermediate_text_address[0])
    print("--num_lines argument has the value: " + str(args.num_lines[0]))
    print("--num_processes argument has the value: " + str(args.num_processes[0]))



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

    total_lines = args.num_lines[0]
    num_processes = args.num_processes[0]
    group_size = num_processes
    total_lines = args.num_lines[0]
    total_groups = total_lines//group_size
    #
    # process = []
    #
    # for i in range(0,num_processes):
    #     process.append(Process(target = pool_process_paragraph, args =
    #                    (process_queues[i],t1,process_labels[i],
    #                     i*lines_per_process,lines_per_process,lock,)))
    #     first thing to do is delete this unused process list below. it is deprecated. replaced!
    process = [
        Process(target = pool_process_paragraph, args =
                (process_queues[0],t1,process_labels[0], args.intermediate_text_address[0], total_groups, lock, num_processes, 0,)),
        Process(target = pool_process_paragraph, args =
                (process_queues[1],t1,process_labels[1], args.intermediate_text_address[0], total_groups, lock, num_processes, 1,)),
        Process(target = pool_process_paragraph, args =
                (process_queues[2],t1,process_labels[2], args.intermediate_text_address[0], total_groups, lock, num_processes, 2,))
    ]

    print(process_labels[0] + "created at time " + str(round(time.time()-t1,4)))
    print(process_labels[1] + "created at time " + str(round(time.time()-t1,4)))
    print(process_labels[2] + "created at time " + str(round(time.time()-t1,4)))




    process[0].start()
    print(process_labels[0] + "started at time " + str(round(time.time()-t1,4)))
    time.sleep(.5)

    process[1].start()
    print(process_labels[1] + "started at time " + str(round(time.time()-t1,4)))
    time.sleep(.5)

    process[2].start()
    print(process_labels[2] + "started at time " + str(round(time.time()-t1,4)))
    time.sleep(6)
    # Read into your process from another process.

    target_dict = [all_affordances, all_affordances, all_affordances]
    num_done = 0
    while True:
        for proc_num in range(0,3):
            try:
                # print_log(process_labels[proc_num], "about to read from the queue.", lock)
                aff_tuple = process_queues[proc_num].get(True, timeout = 1) # procure an affordance tuple
                print_log(process_labels[proc_num], "got a tuple", lock)
                print_log(process_labels[proc_num], str(aff_tuple), lock)
                if aff_tuple == "END111END222end3755639":
                    num_done += 1
                    print(num_done)
                else:
                    add_affordance(aff_tuple[0],aff_tuple[1], target_dict[proc_num])
            except queue.Empty:
                a = 1
                # print_log(process_labels[proc_num], "no tuples found.", lock)

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
