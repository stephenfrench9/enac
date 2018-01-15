import argparse
import codecs
import time
import locale

default_encoding = locale.getpreferredencoding()
print(default_encoding)
print(type(default_encoding))


# print(str(type(endcoding)))
parser = argparse.ArgumentParser(description='Read and parse a wiki dump')
parser.add_argument('num_lines', metavar='N', type=int, nargs=1,
                    help='The number of lines to process \
                    from the wikidump. A value of -1 means the entire \
                    dump will be processed. The default is to process the \
                    entire dump.')
args = parser.parse_args()

start = time.time()



# f = codecs.open("E:\\enwiki-latest-pages-articles.xml",'r','cp1252') # fail at line 105
# f = codecs.open("E:\\enwiki-latest-pages-articles.xml",'r','latin1') # appears to never fail
# f = codecs.open("E:\\enwiki-latest-pages-articles.xml",'r','utf-8') # appears to never fail
# f = codecs.open("E:\\enwiki-latest-pages-articles.xml",'r',default_encoding) # fail at line 105
# f = codecs.open("E:\\enwiki-latest-pages-articles.xml",'r') # fail at line 103
# f = open("E:\\enwiki-latest-pages-articles.xml", encoding='cp1252') # fail at line 93
# f = open("E:\\enwiki-latest-pages-articles.xml", encoding=default_encoding) # fail at line 93
# f = open("E:\\enwiki-latest-pages-articles.xml", encoding='latin_1') # appears to never fail
f = open("E:\\enwiki-latest-pages-articles.xml", encoding='utf-8') # (never threw an UnicodeDecodeError, on the whole document)

# It looks like the function open() fails before the function codec.open(), even when they are using the same encoding. 


line = True
i = 0
while line:
    # print("about to read line: " + str(i))
    line = f.readline() #.encode('cp1252')
    # print("Just read line: " + str(i))
    # print(line)
    # print(type(line))
    if(i%1000000==0):
        dur = (time.time() - start)/60
        print("Time elapsed: " + str(dur))
        print(str(i))
    i += 1

print("The number of lines read is: " + str(i))
elapsedMin = (time.time() - start)/60
print("The elapsed time is: " + str(elapsedMin))
