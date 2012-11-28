#!/usr/local/bin/python
import logging
import os
import sys
import unittest

sys.path.append(os.getcwd() + "/..")
from CollabFilt import Filt


class CollabFiltTest(unittest.TestCase):

    def setUp(self):
        log.debug("setup...")
        self.filtNA = Filt(missingaszero=False)
        self.filtNA.addUser('u1', {'i1':5.0, 'i2':3.0, 'i3':2.5})
        self.filtNA.addUser('u2', {'i1':2.0, 'i2':2.5, 'i3':5.0})
        self.filtNA.addUser('u3', {'i1':2.5})
        self.filtNA.addUser('u4', {'i1':5.0, 'i3':3.0})
        self.filtNA.addUser('u5', {'i1':4.0, 'i2':3.0, 'i3':2.0})

        self.filtZE = Filt(missingaszero=True)
        self.filtZE.addUser('u1', {'i1':5.0, 'i2':3.0, 'i3':2.5})
        self.filtZE.addUser('u2', {'i1':2.0, 'i2':2.5, 'i3':5.0})
        self.filtZE.addUser('u3', {'i1':2.5})
        self.filtZE.addUser('u4', {'i1':5.0, 'i3':3.0})
        self.filtZE.addUser('u5', {'i1':4.0, 'i2':3.0, 'i3':2.0})


    def tearDown(self):
        log.debug("teardown...")

    def test_GetUserCount(self):
        self.assertEqual(self.filtNA.getUserCount(), 5)
        self.assertEqual(self.filtZE.getUserCount(), 5)

    def test_GetItemCount(self):
        self.assertEqual(self.filtNA.getItemCount(), 3)
        self.assertEqual(self.filtZE.getItemCount(), 3)

    def test_GetRatings(self):
        u1 = {'i1':5.0, 'i2':3.0, 'i3':2.5}
        u3 = {'i1':2.5}
        u3ZE = {'i1':2.5, 'i2':0, 'i3':0}
        self.assertEqual(self.filtNA.getRatings('u1'), u1)
        self.assertEqual(self.filtNA.getRatings('u3'), u3)
        self.assertEqual(self.filtZE.getRatings('u1'), u1)
        self.assertEqual(self.filtZE.getRatings('u3'), u3ZE)

        
    def test_GetRatingsMean(self):
        mean = self.filtNA.getRatingsMean(self.filtNA.getRatings('u1'))
        self.assertAlmostEqual(mean, 3.5, delta=0.001)
        mean = self.filtNA.getRatingsMean(self.filtNA.getRatings('u3'))
        self.assertAlmostEqual(mean, 2.5, delta=0.001)
        mean = self.filtZE.getRatingsMean(self.filtZE.getRatings('u1'))
        self.assertAlmostEqual(mean, 3.5, delta=0.001)
        mean = self.filtZE.getRatingsMean(self.filtZE.getRatings('u3'))
        self.assertAlmostEqual(mean, 0.8333, delta=0.001)


    def test_Euclid (self):
        # NA
        sim =  self.filtNA.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':5.0, 'i2':3.0, 'i3':2.5})
        self.assertAlmostEqual(sim, 1.0, delta=0.001)
        sim =  self.filtNA.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':2.0, 'i2':2.5, 'i3':5.0})
        self.assertAlmostEqual(sim, 0.203, delta=0.001)
        sim =  self.filtNA.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':2.5})
        self.assertAlmostEqual(sim, 0.286, delta=0.001)
        sim =  self.filtNA.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':5.0, 'i3':3.0})
        self.assertAlmostEqual(sim, 0.667, delta=0.001)
        sim =  self.filtNA.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':4.0, 'i2':3.0, 'i3':2.0})
        self.assertAlmostEqual(sim, 0.472, delta=0.001)

        # ZE
        sim =  self.filtZE.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':5.0, 'i2':3.0, 'i3':2.5})
        self.assertAlmostEqual(sim, 1.0, delta=0.001)
        sim =  self.filtZE.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':2.0, 'i2':2.5, 'i3':5.0})
        self.assertAlmostEqual(sim, 0.203, delta=0.001)
        sim =  self.filtZE.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':2.5})
        self.assertAlmostEqual(sim, 0.177, delta=0.001)
        sim =  self.filtZE.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':5.0, 'i3':3.0})
        self.assertAlmostEqual(sim, 0.247, delta=0.001)
        sim =  self.filtZE.euclid({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':4.0, 'i2':3.0, 'i3':2.0})
        self.assertAlmostEqual(sim, 0.472, delta=0.001)


    def test_Pearson (self):
        sim =  self.filtNA.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':5.0, 'i2':3.0, 'i3':2.5})
        self.assertAlmostEqual(sim, 1.0, delta=0.001)
        sim =  self.filtNA.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':2.0, 'i2':2.5, 'i3':5.0})
        self.assertAlmostEqual(sim, -0.764, delta=0.001)
        sim =  self.filtNA.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':2.5})
        self.assertIsNone(sim)
        sim =  self.filtNA.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':5.0, 'i3':3.0})
        self.assertAlmostEqual(sim, 1.0, delta=0.001)
        sim =  self.filtNA.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':4.0, 'i2':3.0, 'i3':2.0})
        self.assertAlmostEqual(sim, 0.945, delta=0.001)

        # ZE
        sim =  self.filtZE.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':5.0, 'i2':3.0, 'i3':2.5})
        self.assertAlmostEqual(sim, 1.0, delta=0.001)
        sim =  self.filtZE.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':2.0, 'i2':2.5, 'i3':5.0})
        self.assertAlmostEqual(sim, -0.764, delta=0.001)
        sim =  self.filtZE.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':2.5})
        self.assertAlmostEqual(sim, 0.982, delta=0.001)
        sim =  self.filtZE.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':5.0, 'i3':3.0})
        self.assertAlmostEqual(sim, 0.676, delta=0.001)
        sim =  self.filtZE.pearson({'i1':5.0, 'i2':3.0, 'i3':2.5}, {'i1':4.0, 'i2':3.0, 'i3':2.0})
        self.assertAlmostEqual(sim, 0.945, delta=0.001)
        




# Main
logging.basicConfig(format='%(asctime)-15s [%(levelname)s][%(name)s] %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CollabFiltTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

