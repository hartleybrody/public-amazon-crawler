import os
import csv
from datetime import datetime
import psycopg2

import settings
from helpers import log

conn = psycopg2.connect(database=settings.database, host=settings.host, user=settings.user)
cur = conn.cursor()


def dump_latest_scrape():
    # Export everything
    # cur.execute("SELECT products.* FROM products")

    # Export only the latest crawl
    # cur.execute("SELECT products.* FROM products JOIN (SELECT MAX(crawl_time) FROM products) AS p ON products.crawl_time = p.max;")

    # Dedupe products on their primary_img URL
    cur.execute("SELECT DISTINCT ON (primary_img) * FROM products;")
    return cur.fetchall()


def write_to_csv(data):

    file_name = "{}-amazon-crawl.csv".format(datetime.today().strftime("%Y-%m-%d"))
    file_path = os.path.join(settings.export_dir, file_name)

    with open(file_path, "w") as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

    return file_path


if __name__ == '__main__':
    log("Beginning export")

    rows = dump_latest_scrape()
    log("Got {} rows from database".format(len(rows)))

    file_path = write_to_csv(rows)
    log("Wrote data to {}".format(file_path))
