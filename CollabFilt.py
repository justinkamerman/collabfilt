import logging
from collections import defaultdict
from  math import sqrt


class Filt:
    """ Collaborative Filter
    """
    def __init__ (self, missingaszero=False):
        """ 
        :param missingaszero: ratings stored as a sparse matrix. True if missing values are considered a rating of zero
        :type missingaszero: Boolean
        """

        self.items = set([])
        """ [rating, ...] 
        """
        self.users = {}
        """ {userId:{rating:value},...} """
        self.logger = logging.getLogger(__name__)
        self.missingaszero = missingaszero
        """ Missing values assumed to be zero if True, else None """
        self.similarityMetric = 'euclid'
        """ User similarity metric. Defaults to Euclidean Distance. """


    def setSimilarityMetric (self, similarityMetric):
        """ Sets the user similarity metric 
        """
        self.similarityMetric = similarityMetric


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
            user[item] = float(rating)


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
                    

    def getUserRatings (self, userId):
        """ Get all item ratings for a specific user
        
        :param userId: 
        :return: user ratings map (indexed by item)
        :rtype: dict
        """
        if self.missingaszero:
            ratings = dict.fromkeys(self.items, 0)
            ratings.update(self.users[userId])
            return ratings
        else:
            return self.users[userId]


    def getUserRatingCounts(self):
        """ Get the number of items rated by each user
        
        :return: list of the number of items ranked by each user
        :rtype: list of (userId, rated_item_count) tuples
        """
        if self.missingaszero:
            return [(userId, self.getItemCount()) for userId in self.users.keys()]
        else:
            return [(userId, len(ratings)) for (userId, ratings) in self.users.items()]

    
    def getItemRatings (self, item):
        """ Get all user ratings for a specific item

        :param item: item name
        :return: item ratings map (indexed by user)
        :rtype: dict
        """
        ratings = {}
        for (userId, userRatings) in self.users.items():
            if userRatings.has_key(item):
                ratings[userId] = userRatings[item]
            elif self.missingaszero:
                ratings[userId] = 0
        return ratings


    def getItemRatingCounts(self):
        """ Get the number of ratings per item
        
        :return: list of the number of ratings for each item
        :rtype: list of (item, rating_count) tuples
        """
        if self.missingaszero:
            return [(item, self.getUserCount()) for item in self.items]

        else:
            ratingCounts = defaultdict(int)
            for  userRatings in self.users.values():
                for item in userRatings.keys():
                    ratingCounts[item] += 1
            return [(item, count) for (item, count) in ratingCounts.items()]

    
    def getRatingMean (self, ratings):
        """ Calculate mean of a given collection of item ratings
        
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
        overlap = len(list(set(user1.keys()) & set(user2.keys())))
        if overlap < 1 and not self.missingaszero:
            return None
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

        Note: Pearson coefficient is only defined if the variance of
        both vectors are nonzero.
        
        :param user1: user ratings
        :type user1: dict
        :param user2: user ratings
        :type user1: dict
        :return: euclidean similarity between user1 and user2
        :rtype: float
        """
        overlap = len(list(set(user1.keys()) & set(user2.keys())))
        if overlap < 2 and not self.missingaszero:
            return None
        else:
            Sx = 0.0
            Sy = 0.0
            Sxy = 0.0
            Sx2 = 0.0
            Sy2 = 0.0
            N = 0.0
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
        
            denominator = (Sx2-Sx**2/N)*(Sy2-Sy**2/N)
            if denominator:
                cor = (Sxy-Sx*Sy/N)/sqrt((Sx2-Sx**2/N)*(Sy2-Sy**2/N))
            else:
                cor = None
            return cor


    def similarUsers (self, target, n=None, sim=None):
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
        if not sim: sim = self.similarityMetric
        simFunction = getattr(self, sim)
        for (userId, ratings) in self.users.items():
            similarity = simFunction (target, ratings)
            if similarity:
                simlist.append(( userId, similarity))
            
        simlist.sort(key=lambda x: x[1], reverse=True)
        if n:
            del simlist[n:]
        return simlist


    def predictRatings (self, target, n=None, m=None, weight=True, sim=None):
        """ Return predicted ratings for given user
        
        :param target: target item ratings
        :type target: dict {item: rating}
        :param n: use n most similar users to predict ratings. Default all.
        :param m: return m most highly rated items. Default all.
        :param weight: Weight candidate item ratings by similarity score. Default True.
        :type boolean:
        :type n: int
        :return: list of tuples ordered by estimates rating
        :rtype: (userId, rating) 
        """
        totalRatings = defaultdict(int)
        totalSims = defaultdict(int)
        users = self.similarUsers (target, n, sim=sim)
        for (user, similarity) in users:
            if weight:
                weighting = similarity
            else:
                weighting = 1

            # Sum similar user ratings for items not rated by the target user
            for (item, rating) in self.getUserRatings(user).items():
                if not target.has_key(item):
                    totalRatings[item] += (rating * weighting)
                    totalSims[item] += abs(weighting)
                
        rankings = [(item, total/totalSims[item]) 
                    for (item, total) in totalRatings.items() if totalSims[item] != 0]
        rankings.sort(key=lambda x: x[1], reverse=True)
        if m:
            del rankings[m:]
        return rankings




            
