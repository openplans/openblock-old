from django.test import TestCase
from ebpub.streets.models import Block

class TestBlocks(TestCase):

    fixtures = ['wabash']

    def test_contains_number__no_numbers(self):
        block = Block.objects.get(street='WABASH', pk=1002)
        for i in range(16):
            i = i ** i
            self.assertEqual(block.contains_number(i),
                             (False, None, None))


    def test_contains_number__no_left_or_right(self):
        block = Block.objects.get(street='WABASH', from_num=200, to_num=298)
        self.assertEqual(block.contains_number(200),
                         (True, 200, 298))
        self.assertEqual(block.contains_number(201),
                         (True, 200, 298))
        self.assertEqual(block.contains_number(298),
                         (True, 200, 298))
        self.assertEqual(block.contains_number(299),
                         (False, 200, 298))
        self.assertEqual(block.contains_number(199),
                         (False, 200, 298))

    def test_contains_number__left_and_righ(self):
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=297,
                                  )
        self.assertEqual(block.contains_number(216),
                         (True, 216, 298))
        self.assertEqual(block.contains_number(217),
                         (True, 217, 297))
        self.assertEqual(block.contains_number(299),
                         (False, 217, 297))
        self.assertEqual(block.contains_number(215),
                         (False, 217, 297))
