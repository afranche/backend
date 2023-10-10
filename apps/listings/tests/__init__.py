from django.test import TransactionTestCase
from django.core.management import call_command

from apps.listings.models import Category


class TestInitCategories(TransactionTestCase):

    def setUp(self):
        call_command('init_listings')

    def test_init_categories(self):
        main_categories = Category.objects.filter(parent=None)
        expected = ['Alimentation', 'Autres', 'Bijoux', 'Textile']
        self.assertEqual(len(main_categories), len(expected))
        for cat in main_categories:
            self.assertIn(cat.name, expected)
            self.assertEqual(cat.parent, None)
        sub_categories = Category.objects.filter(parent__isnull=False)
        expected = ['Sweat-shirts', 'T-shirts', 'Colliers']
        self.assertEqual(len(sub_categories), len(expected))
        for cat in sub_categories:
            self.assertIn(cat.name, expected)
            if cat.name == 'Sweat-shirts' or cat.name == 'T-shirts':
                self.assertEqual(cat.parent.name, 'Textile')
            if cat.name == 'Colliers':
                self.assertEqual(cat.parent.name, 'Bijoux')