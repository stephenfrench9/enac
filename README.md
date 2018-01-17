# enac
An attempt to write code that will be useful for a neural affordance calculus. At the very least, a useful learning experiment for myself.

## n_wiki_parser.py
Printed to the console: Each paragraph from the articles is printed alongside its parse.  
Printed to the console: The affordance distributions are printed at the conclusion of the script.  
Saved to a file: The paragraphs and parses are saved to "n_wiki_pages"  
Saved to a file: The affordance distribution is pickled and saved in "all_affordances.p"  

## build_distributions.py
Extract affordances from a wikidump file: enwiki-latest-pages-articles.xml at the address https://dumps.wikimedia.org/enwiki/latest/

From the command line:
usage: build_distributions.py [-h] [--num_lines N] A

positional arguments:
  A              The address for the dump file

optional arguments:
  -h, --help     show this help message and exit
  --num_lines N  The number of lines to process from the wikidump. A value of
                 -1 means the entire dump will be processed. The default is to
                 process the entire dump.
