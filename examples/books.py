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

def mapISBN (ratings):
    for (isbn, rating) in ratings:
        print ("%s: %s %s" % (isbn, rating, books[isbn]))


# Process comand args
input = "../data/BX-Book-Ratings.csv"
bookinput = "../data/BX-Books.csv"
books = {}
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


# Load titles
with open(bookinput, 'rb') as f:
    # DictReader expects first row to define fieldnames
    reader = csv.DictReader(f, delimiter=';', quotechar='"')
    for line in reader:
        books[line['ISBN']] = line['Book-Title'], line['Book-Author']

# Load ratings from input file
filt = Filt(missingaszero=False)
with open(input, 'rb') as f:
    # DictReader expects first row to define fieldnames
    reader = csv.DictReader(f, delimiter=';', quotechar='"')
    for line in reader:
        filt.addUserRatings(line['User-ID'], {line['ISBN']: line['Book-Rating']})


print ("User count: %d" %filt.getUserCount())
print ("Item count: %d" % filt.getItemCount())

# "042505313X";"Dune";"Frank Herbert"
# "083760463X";"The Martian Way and Other Stories";"Isaac Asimov"
# "0425042367";"Podkayne of Mars";"Robert A. Heinlein"
# "0425043770";"Stranger Strg Lnd";"Robert A. Heinlein"
# "0425043797";"Dune Messiah";"Frank Herbert"
# "0446354872";"Batman: The Novelization"
user1 = {'042505313X':10, '083760463X':7, "0425042367":8, "0425043770":6, "0425043797":10, '0446354872': 7.0}
print ("\nUser\n====")
mapISBN ([(isbn, rating) for (isbn, rating) in user1.items()])

topnitems = 10
print ("\nEuclid\n======")
print ("Top estimated ratings for user:")
predicted = filt.predictRatings(user1, m=topnitems, sim='euclid')
mapISBN(predicted)
print ("\nSimilar to users:")
print filt.similarUsers(user1, sim='euclid')

print ("\nPearson\n=======")
print ("Top estimated ratings for user:")
predicted = filt.predictRatings(user1, m=topnitems, sim='pearson')
mapISBN(predicted)
print ("\nSimilar to users:")
print filt.similarUsers(user1, sim='pearson')

