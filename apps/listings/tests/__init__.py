from django.test import TransactionTestCase
from django.core.management import call_command

from apps.listings.models import Category, Listing, Product, Characteristic


class TestInitCategories(TransactionTestCase):

    def setUp(self):
        queryset = Category.objects.all()
        if queryset.exists():
            queryset.delete()
        call_command('init_listings')

    def test_init_categories(self):
        main_categories = Category.objects.filter(parent__isnull=True)
        expected = ['Alimentation', 'Autres', 'Bijoux', 'Textile']
        self.assertEqual(len(main_categories), len(expected))
        for cat in main_categories:
            self.assertIn(cat.name, expected)
            self.assertEqual(cat.parent, None)
        sub_categories = Category.objects.filter(parent__isnull=False)
        expected = ['Sweat-shirts', 'T-shirts', 'Colliers', 'Accessoires']
        self.assertEqual(len(sub_categories), len(expected))
        for cat in sub_categories:
            self.assertIn(cat.name, expected)
            if cat.name == 'Sweat-shirts' or cat.name == 'T-shirts' or cat.name == 'Accessoires':
                self.assertEqual(cat.parent.name, 'Textile')
            if cat.name == 'Colliers':
                self.assertEqual(cat.parent.name, 'Bijoux')

    def test_init_listings(self):
        listing = Listing.objects.all().filter(product__name='Tote bag blanc avec un imprimé au choix').first()
        self.assertEqual(
            listing.product.images,
            ["https://drive.google.com/file/d/14IDwe6TQBhDu6Y1eKp3hfvj3LMqkOjoi/view?usp=share_link",
             "https://drive.google.com/file/d/1paNwU3aP1fjZ3zI8O4xpcSPK0EwHd2wJ/view?usp=share_link",
             "https://drive.google.com/file/d/1KcEYvUZ4ux0_MYeKBcyZEG70Sp5WF55g/view?usp=share_link"]
        )
        self.assertEqual(listing.product.name, 'Tote bag blanc avec un imprimé au choix')
        self.assertEqual(listing.categories.first().name, 'Accessoires')
        self.assertEqual(listing.product.type, Product.ProductType.OTHER)
        self.assertEqual(listing.product.price, 25)
        self.assertEqual(listing.product.description,  "Tote-bag blanc en coton fabriqué en Palestine et imprimé par Aladin, un vendeur palestinien de la vieille ville de Jérusalem. Le tote-bag est doublé, comporte une fermeture éclaire ainsi que deux poches internes dont l'une avec fermeture éclaire. L'imprimé est au choix.")
        self.assertEqual(listing.product.weight, 100)
        self.assertEqual(listing.product.manufacturer, 'Aladin')
        self.assertEqual(listing.product.conservation, "Pour le lavage, suivre les instructions sur l'étiquette du tote bag. Laver à l'envers. Ne pas repasser l'imprimé. ")
        self.assertEqual(listing.product.lang, 'fr')
        self.assertEqual(listing.characteristics.first().label, 'le motif que vous voulez')
        self.assertEqual(listing.characteristics.first().type, Characteristic.CharacteristicType.INPUT)



    def tearDown(self) -> None:
        Category.objects.all().delete()
        Listing.objects.all().delete()
        Characteristic.objects.all().delete()
        Product.objects.all().delete()