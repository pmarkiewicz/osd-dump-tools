import unittest

from osd.utils.find_slot import find_slots


class TestFindSlots(unittest.TestCase):
    def test_slots1(self):
        src = [5, 15]

        t1 = [2, 3, 8, 10, 16]
        e1 = [1, 2, 3]
        self.assertEqual(find_slots(t1, *src), e1)

        t2 = [2]
        e2 = [0]
        self.assertEqual(find_slots(t2, *src), e2)

        t3 = [18]
        e3 = []
        self.assertEqual(find_slots(t3, *src), e3)

        t4 = [2, 18]
        e4 = [0]
        self.assertEqual(find_slots(t4, *src), e4)

        t5 = []
        e5 = []
        self.assertEqual(find_slots(t5, *src), e5)

        t6 = [10]
        e6 = [None, 0]
        self.assertEqual(find_slots(t6, *src), e6)

        t7 = [5]
        e7 = [0]
        self.assertEqual(find_slots(t7, *src), e7)

        t8 = [15]
        e8 = []
        self.assertEqual(find_slots(t8, *src), e8)

        t9 = [5, 15]
        e9 = [0]
        self.assertEqual(find_slots(t9, *src), e9)

    def test_slots2(self):
        src = [26, 32]

        t1 = [2, 6, 16, 26, 35]
        e1 = [3]
        self.assertEqual(find_slots(t1, *src), e1)
