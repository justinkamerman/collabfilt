import random
import unittest
import logging


class CollabFiltTest(unittest.TestCase):
    
    def setUp(self):
        log.debug("setup...")
        self.seq = range(10)


    def tearDown(self):
        log.debug("teardown...")


    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))


    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)


    def test_sample(self):
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)



logging.basicConfig(format='%(asctime)-15s [%(levelname)s][%(name)s] %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
suite = unittest.TestLoader().loadTestsFromTestCase(CollabFiltTest)
unittest.TextTestRunner(verbosity=2).run(suite)
