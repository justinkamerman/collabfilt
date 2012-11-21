#!/usr/bin/python

import os
import sys
import getopt
import logging
import logging.config
import re
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from xml.etree import ElementTree
from CollabFilt import Filt

sys.path.append(os.getcwd() + "/..")
from pycloud import Api

input = None
out = 'topicterms.dat'
url = 'https://localhost/socialcloud/v1'
appkey = 'myapp'
username = 'me@radian6.com'
password = 'mypassword'


def usage():
    print ("Usage: %s [-h] [-i file]")
    print ("Options and arguments:")
    print ("-h          : help")
    print ("-i file     : load topic data from named file")
    print ("-o file     : write topic-term matrix to named file. Default %s" % out)
    print ("-u url      : Socialcloud url. Default %s" % url)
    print ("-a appkey   : Socialcloud application key. Default %s" % appkey)
    print ("-n username : Socialcloud username. Default %s" % username)
    print ("-p password : Socialcloud password. Default %s\n" % password)



def main():
    global input, out, url, appkey, username, password
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:u:a:n:p:")
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
        elif o in ("-o"):
            out = a
        elif o in ("-u"):
            url = a
        elif o in ("-a"):
            appkey = a
        elif o in ("-n"):
            username = a
        elif o in ("-p"):
            password = a
        else:
            usage()
            sys.exit(2)
    
    #try
    topicsxml = ''
    if input is not None:
        topicsxml = ElementTree.parse(input).getroot()
    else:
        api = Api (url, appkey, username, password)
        api.auth_authenticate()
        topicsxml = api.topics()
    
    #print ElementTree.tostring(topicsxml)
    #sys.exit()
    filt = Filt(missingaszero=True)
    #stemmer = PorterStemmer()
    #for topic in topicsxml.findall('topicFilter'):
    #    name = topic.findtext('name')
    #    id = topic.findtext('topicFilterId')
    #    ratings = {}
    #    for query in topic.findall ('filterGroups/filterGroup/filterQueries/filterQuery/query'):
    #        for term in re.split(r'\W+', query.text):
    #            term = term.lower()
    #            if len(term)>2 and term not in stopwords.words():
    #                ratings[term] = ratings.get(term, 0) + 1
    #
    #    filt.addUser(id, ratings)
    #    logger.debug ("Topic %s: %s: %s" % (id, name, ratings))
    #    
    #logger.info ("Processed %d topic profiles. Encountered %d unique terms." 
    #             % (filt.getUserCount(), filt.getItemCount()))

    
    filt2 = Filt(missingaszero=False)
    filt2.addUser('U1', {'item101':5, 'item102':3, 'item103':2.5})
    filt2.addUser('U2', {'item101':2, 'item102':2.5, 'item103':5})
    filt2.addUser('U3', {'item101':2.5})
    filt2.addUser('U4', {'item101':5, 'item103':3})
    filt2.addUser('U5', {'item101':4, 'item102':3, 'item103':2})
    print(filt2.dumpMatrix())
    print

    users = filt2.similarUsers({'item101':5, 'item102':3, 'item103':2.5},
                               sim='pearson')
    print (users)

    filt2.addUserRatings('U6', {'item101':99, 'item103':100})
    print(filt2.dumpMatrix())

    #except Exception, exception:
    #        logger.error("Error retrieving topic query terms: %s" % (exception))
    #        raise exception



if __name__ == '__main__': 
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger(__name__)
    main() 
