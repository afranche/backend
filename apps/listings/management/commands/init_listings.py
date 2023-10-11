import re
from django.core.management.base import BaseCommand
import requests
import pandas as pd
import io

from apps.listings.models import Category, Product, Listing, Characteristic



class Command(BaseCommand):
    def handle(self, *_, **__):
        if Product.objects.count() > 0:
            print("Listings already initialized.")
            return
        url = "https://docs.google.com/spreadsheets/d/1hXSw28QSZwnV31BbuNgGWlxi1kJ1DZd1vHlMshVgTy8/export?format=csv"
        res = requests.get(url)
        if res.status_code != 200:
            print("Failed to fetch listings.", res.content)
            return
        df = pd.read_csv(io.BytesIO(res.content), encoding='utf8', sep=",")
        df = self.clean_df(df)

        self.create_categories(df)
        print("Categories created.")
        print(Category.objects.all())
        self.create_listings(df)
        print("Listings created.")
        print(Listing.objects.all())

    
    def create_listings(self, df: pd.DataFrame) -> None:
        for _, row in df.iterrows():
            product = Product(
                name=row['name'],
                description=row['description'],
                price=row['price €'],
                manufacturer=row['commerçants'],
                weight=row['weight g'],
                type=Product.ProductType.FOOD if row['is food'] == 'VRAI' else Product.ProductType.OTHER,
                conservation=row['how to conserve it'],
                images=row['images'].split(' '),
            )
            product.save()
            listing = Listing(product=product)
            listing.save()
            cat_name = row['sous catégorie'].strip()
            cat_name = cat_name if cat_name != "" else row['category'].strip()
            listing.categories.add(Category.objects.get(name=cat_name))
            """
                    It is written this way:
                    Champ: label
                    Label: choices
            """
            for variables in ['Variable', 'Variable 2', 'Variable 3']:
                label_1 = re.findall(r'/Couleur\:|Champ\:|Motif\:/', row['Variable'])
                if len(label_1) == 0:
                    continue
                # breakpoint()
                label_1 = label_1[0]
                characteristic = Characteristic.objects.create(
                    label=row[variables].replace('Champ: ', '') if 'Champ' in label_1 else label_1,
                    type=Characteristic.CharacteristicType.INPUT if 'Champ' in label_1 else Characteristic.CharacteristicType.CHOICES,
                    choices=row[variables].split(', ') if 'Champ' not in label_1 else None,
                )
                listing.characteristics.add(characteristic)

            listing.save()
            product.save()


    def create_categories(self, df: pd.DataFrame) -> None:
        df['category'] = df.category.map(lambda x: x.strip())
        df_cat = df[['category', 'sous catégorie']].drop_duplicates()
        for name, group in df_cat.groupby(by="category", dropna=False):
            main_cat = Category(name=name)
            main_cat.save()
            for sub_name in group['sous catégorie'].dropna().unique():
                if sub_name == "":
                    continue
                sub_cat = Category(name=sub_name)
                sub_cat.parent = main_cat
                sub_cat.save()
            main_cat.save()

                
            # main_cat.save()

    def clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.fillna("")
        return df.drop(['dimensions cmxcmxcm', 'in stock'], axis=1)
