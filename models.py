import psycopg2

import settings

conn = psycopg2.connect(database=settings.database, host=settings.host, user=settings.user)
cur = conn.cursor()


class ProductRecord(object):
    """docstring for ProductRecord"""
    def __init__(self, title, product_url, listing_url, price, primary_img, crawl_time):
        super(ProductRecord, self).__init__()
        self.title = title
        self.product_url = product_url
        self.listing_url = listing_url
        self.price = price
        self.primary_img = primary_img
        self.crawl_time = crawl_time

    def save(self):
        cur.execute("INSERT INTO products (title, product_url, listing_url, price, primary_img, crawl_time) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (
            self.title,
            self.product_url,
            self.listing_url,
            self.price,
            self.primary_img,
            self.crawl_time,
        ))
        conn.commit()
        return cur.fetchone()[0]


if __name__ == '__main__':

    # setup tables
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute("""CREATE TABLE products (
        id          serial PRIMARY KEY,
        title       varchar(2056),
        product_url         varchar(2056),
        listing_url varchar(2056),
        price       varchar(128),
        primary_img varchar(2056),
        crawl_time timestamp
    );""")
    conn.commit()
