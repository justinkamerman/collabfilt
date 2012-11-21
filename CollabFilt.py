import logging
from  math import sqrt


class Filt:
    """Collaborative Filter
    """

    def __init__ (self, missingaszero=False):
        """ 
        :param missingaszero: ratings stored as a sparse
        matrix. True if missing values are considered a rating of zero
        :type missingaszero: Boolean
        
        """
        self.items = set([])
        """ [rating, ...] """
        self.users = {}
        """ {userId:{rating:value},...} """
        self.logger = logging.getLogger(__name__)
        self.missingaszero = missingaszero
        """ Missing values assumed to be zero if True, else None """


    def dumpMatrix(self):
        """ Dump ratings matrix 
        """
        items = sorted(self.items)
        users = self.users.keys()
        users.sort()
        buf = []
        buf.append("id %s\n" % (' '.join(items)))
        for id in users:
            row = [id]
            for item in items:
                row.append (str(self.users[id].get(item, (None, 0)[self.missingaszero])))
                
            buf.append(' '.join(row))
            buf.append("\n")

        return ''.join(buf)


    def getUserCount(self):
        """ Return number of users
        """
        return len(self.users)
    
    
    def getItemCount(self):
        """ Return number of items
        """
        return len(self.items)
    
    
    def addUser(self, userId, ratings):
        """ Add a user and associated ratings
        
        :param userId: 
        :param ratings: user ratings (sparse)
        :type req: dict
        """
        user = {}
        for (item, rating) in ratings.items():
            self.items.add(item)
            user[item] = rating

        self.users[userId] = user


    def addUserRatings(self, userId, ratings):
        """ Add ratings to an user. Creates user if it doesn't already exist.
        
        :param userId: 
        :param ratings: user ratings
        :type req: dict
        """
        user = self.users.setdefault(userId, {})
        if user is None:
            self.users
        for (item, rating) in ratings.items():
            self.items.add(item)
            user[item] = rating


    def centerRatings(self):
        """ Normalize the ratings

        """
        for (userId, ratings) in self.users.items():
            mean = self.getRatingMean(ratings)
            if not mean == 0:
                for item in self.items:
                    unnorm = self.users[userId].get(item)
                    if unnorm:
                        self.users[userId][item] = unnorm - mean
                    elif self.missingaszero:
                        self.users[userId][item] = - mean
                    

    def getRatings (self, userId):
        """ Get ratings for a specific user
        
        :param userId: 
        :return: user ratings map
        :rtype: dict
        """
        return self.users[userId]

    
    def getRatingMean (self, ratings):
        """ Get mean rating for a specific user
        
        :param ratings: ratings 
        :type ratings: dict {rating:value,...}
        :return: mean user rating
        :rtype: float
        """
        if len(ratings) == 0: 
            return 0
        else:
            total = 0
            for value in ratings.values():
                total += value

        # If missing values are assigned a valid rating by default
        # then we need to include these in our calculation
        if self.missingaszero:
            return (total/float(self.getItemCount()))
        else:
            return (total/float(len(ratings)))
                     

    def euclid (self, user1, user2):
        """ Calculate Euclidean similarity between two users. Because
        of the sparse storage format, we have to iterate through the
        key set union as opposed to the intersection.
        
        :param user1: user ratings
        :type user1: dict
        :param user2: user ratings
        :type user1: dict
        :return: euclidean similarity between user1 and user2
        :rtype: float
        """
        dsqr = 0
        items = set(user1.keys())
        items.update(user2.keys())
        for item in items:
            u1rating = user1.get(item, (None, 0)[self.missingaszero])
            u2rating = user2.get(item, (None, 0)[self.missingaszero])
            if u1rating is not None and u2rating is not None:
                dsqr += (u1rating - u2rating)**2
        
        distance = sqrt(dsqr)
        return 1/(1+distance)


    def pearson (self, user1, user2):
        """ Calculate pearson similarity between two users. Because
        of the sparse storage format, we have to iterate through the
        key set union as opposed to the intersection.    
        As required by Pearson, checks that there is more than a
        single factor overlap.
        
        :param user1: user ratings
        :type user1: dict
        :param user2: user ratings
        :type user1: dict
        :return: euclidean similarity between user1 and user2
        :rtype: float
        """
        dsqr = 0
        overlap = len(list(set(user1.keys()) & set(user2.keys())))
        if overlap < 2 and not self.missingaszero:
            return None
        else:
            Sx = 0
            Sy = 0
            Sxy = 0
            Sx2 = 0
            Sy2 = 0
            N = 0
            items = set(user1.keys())
            items.update(user2.keys())
            for item in items:
                xi = user1.get(item, (None, 0)[self.missingaszero])
                yi = user2.get(item, (None, 0)[self.missingaszero])
                if xi is not None and yi is not None:
                    N += 1
                    Sx += xi
                    Sy += yi
                    Sxy += xi*yi
                    Sx2 += xi**2
                    Sy2 += yi**2
        
            cor = (Sxy-Sx*Sy/N)/sqrt((Sx2-Sx**2/N)*(Sy2-Sy**2/N))
            return cor


    def similarUsers (self, target, sim='euclid', n=None):
        """ Return ordered (ascending) list of similar users to the given users
        
        :param target: target item ratings
        :type target: dict {item: rating}
        :param sim: similarity calculator function
        :type sim: function (self, <user1 ratings dict>, <user2 ratings dict>)
        :param n: return top n users. Default all.
        :type n: int
        :return: list of tuples ordered by similarity
        :rtype: (userId, similarity) 
        """
        simlist = []
        simFunction = getattr(self, sim)
        for (userId, ratings) in self.users.items():
            similarity = simFunction (target, ratings)
            simlist.append(( userId, similarity))
            
        simlist.sort(key=lambda x: x[1], reverse=True)
        if n:
            del simlist[n:]
        return simlist
        



            
