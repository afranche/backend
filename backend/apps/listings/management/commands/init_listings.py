import json
import re
import time
import warnings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import requests
import pandas as pd
import io

from apps.listings.models import Category, Manufacturer, Product, Listing
from apps.listings.serializers import ProductSerializer
from settings.settings import env
from os import environ

BEEN_THROUGH_BREAKPOINT = False

with open("./.cookies.json", 'r') as f:
    cookies = json.loads(f.read())

def download_image_from_drive(link: str) -> bytes | None:
    return None

class Command(BaseCommand):
    def handle(self, *_, **__):
        if Product.objects.count() > 0:
            print("Listings already initialized.")
            return
        url = environ.get("DRIVE_CSV_URL")
        res = requests.get(url)
        if res.status_code != 200:
            print("Failed to fetch listings.", res.content)
            return
        df = pd.read_csv(io.BytesIO(res.content), encoding='utf8', sep=",")
        df = self.clean_df(df)

        if Category.objects.count() == 0:
            self.create_categories(df)
            print("Categories created.")
        print(Category.objects.all())
        self.create_listings(df)
        print("Listings created.")
        print(Listing.objects.all())

    def create_listings(self, df: pd.DataFrame) -> None:

        for _, row in df.iterrows():

            if row['commerçants']:
                manufacturer, created = Manufacturer.objects.get_or_create(
                    name=row['commerçants'],
                    phone_number=f'+{row["manufacturer"]}')
            else:
                manufacturer, created = Manufacturer.objects.get_or_create(name="Unknown")
            listing = Listing.objects.create(
                name=row['name'],
                description=row['description'],
                price=row['price €'],
                weight=row['weight g'],
                type=Listing.ProductType.FOOD if row['is food'] == 'VRAI' else Listing.ProductType.OTHER,
                conservation=row['how to conserve it'],
                manufacturer=manufacturer,
            )

            cat_name = row['sous catégorie'].strip()
            cat_name = cat_name if cat_name != "" else row['category'].strip()
            listing.categories.add(Category.objects.get(name=cat_name))

            inc = 0
            pattern = r"Couleur\: |Champ\: |Motif\: |Taille\: |Couleur de l'imprimé\: |Genre\: " 
            for variables in ['Variable', 'Variable 2', 'Variable 3']:
                print("row[variables]", row[variables])
                if not re.match(pattern, row[variables]):
                    inc += 1
                    if inc < 3:
                        continue
                else:
                    label = re.findall(pattern, row[variables])[0]
                    print("label", label)
                    data={
                        'choices' : [
                            {
                                'characteristics': {
                                    'label': label,
                                    'value': '' if 'Champ' in row[variables] else choice,
                                },
                                'is_customized': True if 'Champ' in row[variables] else False,
                                'images': []
                            } for choice in re.sub(pattern, '', row[variables]).split(', ') if choice != ""
                        ]
                    }
                if inc == 3:
                    data = {
                        'choices': [
                            {
                                'is_customized': True,
                                'characteristics': {"label": "Ajoutez un commentaire", "value": ""},
                                'images': []  # deal with this later
                            }
                        ],
                    }
                for choice in data['choices']:
                    serializer = ProductSerializer(data=choice)
                    print(serializer)
                    if serializer.is_valid():
                        print("valid serializer")
                        serializer.save()
                        listing.products.add(serializer.instance) 
                    else:
                        print("oh no, invalid serializer", serializer.errors)
            listing.save()


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
