#!/usr/bin/python

import os
import sys
import getopt
import logging
import logging.config
import re
import csv

sys.path.append(os.getcwd() + "/..")
from CollabFilt import Filt



def usage():
    print ("Usage: %s [-h] [-i file]")
    print ("Options and arguments:")
    print ("-h          : help")
    print ("-i file     : load topic data from named file")


#def main():
# Process comand args
global input, out, url, appkey, username, password
input = "../data/test.dat"
try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:")
except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(2)

for o, a in opts:
    if o in ("-h"):
        usage()
        sys.exit()
    elif o in ("-i"):
        input = a
    else:
        usage()
        sys.exit(2)

if not input:
    print ("Input file not specified.")
    usage()
    sys.exit(2)

# Load data from input file
filt = Filt(missingaszero=False)
with open(input, 'rb') as f:
    # DictReader expects first row to define fieldnames
    reader = csv.DictReader(f, delimiter=';', quotechar='"')
    for line in reader:
        #print("Adding user rating: %s (%s)" % (line['Book-Rating'], type(line['Book-Rating'])))
        filt.addUserRatings(line['User-ID'], {line['ISBN']: line['Book-Rating']})


#try
print filt.getUserCount()
print filt.getItemCount()

#simUsers = filt.similarUsers({'042505313X':10, '0155061224':10}, n=10, sim='euclid')
#print (simUsers)
print filt.predictRatings({'042505313X':5, '0553073273':5}, n=100, m=5)

#except Exception, exception:
#        logger.error("Error retrieving topic query terms: %s" % (exception))
#        raise exception



#if __name__ == '__main__': 
#    logging.config.fileConfig("logging.conf")
#    logger = logging.getLogger(__name__)
#    main() 
