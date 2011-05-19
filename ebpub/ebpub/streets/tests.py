from django.test import TestCase
from ebpub.streets.models import Block

class TestBlocks(TestCase):

    fixtures = ['wabash.yaml']
    urls = 'ebpub.urls'

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
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.contains_number(214),
                         (False, 216, 298))
        self.assertEqual(block.contains_number(215),
                         (False, 217, 299))
        self.assertEqual(block.contains_number(216),
                         (True, 216, 298))
        self.assertEqual(block.contains_number(217),
                         (True, 217, 299))
        self.assertEqual(block.contains_number(298),
                         (True, 216, 298))
        self.assertEqual(block.contains_number(299),
                         (True, 217, 299))
        self.assertEqual(block.contains_number(300),
                         (False, 216, 298))

    def test_block__street_url(self):
        # TODO: these tests depend on get_metro()['multiple_cities'] setting
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.street_url(), '/streets/wabash-ave/')

    def test_block__rss_url(self):
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.rss_url(), '/rss/streets/wabash-ave/216-299n-s/')


    def test_block__alert_url(self):
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.alert_url(), '/streets/wabash-ave/216-299n-s/alerts/')


    def test_block__url(self):
        block = Block.objects.get(street='WABASH',
                                  left_from_num=216, left_to_num=298,
                                  right_from_num=217, right_to_num=299,
                                  )
        self.assertEqual(block.url(), '/streets/wabash-ave/216-299n-s/')
