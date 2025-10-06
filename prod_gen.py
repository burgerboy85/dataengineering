import pandas as pd
import random
import string
#import unittest


class ProductGenerator:
    def __init__(self, num_rows=40):
        self.num_rows = num_rows
        self.product_ids = set()
        self.product_names = set()

    def generate_product_id(self):
        while True:
            product_id = f"P{random.randint(10000, 99999)}"
            if product_id not in self.product_ids:
                self.product_ids.add(product_id)
                return product_id

    def generate_product_name(self):
        prefix = "Product-"
        suffix = "".join(random.choices(string.ascii_uppercase, k=2)) + str(random.randint(1000, 9999))
        product_name = prefix + suffix
        self.product_names.add(product_name)
        return product_name

    def generate_category(self):
        categories = ["depressants", "hallucinogens", "stimulants"]
        return random.choice(categories)

    def generate_product_data(self):
        data = []
        for _ in range(self.num_rows):
            product_id = self.generate_product_id()
            product_name = self.generate_product_name()
            category = self.generate_category()
            data.append((product_id, product_name, category))
        return data

    def generate_product_dataframe(self):
        data = self.generate_product_data()
        df = pd.DataFrame(data, columns=["product_id", "product_name", "category"])
        return df

def main():
    generator = ProductGenerator(num_rows=40)
    product_df = generator.generate_product_dataframe()
    product_df.to_csv("product_dev.csv", index=False)
    print("Generated product_dev.csv successfully!")


""" class TestProductGenerator(unittest.TestCase):
    def test_generate_product_dataframe(self):
        generator = ProductGenerator(num_rows=40)
        product_df = generator.generate_product_dataframe()
        self.assertEqual(len(product_df), 40)
        self.assertTrue(all(product_df["product_id"].str.startswith("P")))
        self.assertTrue(all(product_df["product_name"].str.startswith("Product-")))
        self.assertTrue(all(product_df["category"].isin(["depressants", "hallucinogens", "stimulants"])))
 """
if __name__ == "__main__":
    #unittest.main()
    main()