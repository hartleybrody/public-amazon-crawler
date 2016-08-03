import os
import random
from datetime import datetime
from urlparse import urlparse

import eventlet
requests = eventlet.import_patched('requests.__init__')
time = eventlet.import_patched('time')
import redis

from BeautifulSoup import BeautifulSoup
from requests.exceptions import RequestException

import settings

num_requests = 0

redis = redis.StrictRedis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)


def make_request(url, return_soup=True):
    # global request building and response handling

    url = format_url(url)

    if "picassoRedirect" in url:
        return None  # skip the redirect URLs

    global num_requests
    if num_requests >= settings.max_requests:
        raise Exception("Reached the max number of requests: {}".format(settings.max_requests))

    proxies = get_proxy()
    try:
        r = requests.get(url, headers=settings.headers, proxies=proxies)
    except RequestException as e:
        log("WARNING: Request for {} failed, trying again.".format(url))
        return make_request(url)  # try request again, recursively

    num_requests += 1

    if r.status_code != 200:
        os.system('say "Got non-200 Response"')
        log("WARNING: Got a {} status code for URL: {}".format(r.status_code, url))
        return None

    if return_soup:
        return BeautifulSoup(r.text), r.text
    return r


def format_url(url):
    # make sure URLs aren't relative, and strip unnecssary query args
    u = urlparse(url)

    scheme = u.scheme or "https"
    host = u.netloc or "www.amazon.com"
    path = u.path

    if not u.query:
        query = ""
    else:
        query = "?"
        for piece in u.query.split("&"):
            k, v = piece.split("=")
            if k in settings.allowed_params:
                query += "{k}={v}&".format(**locals())
        query = query[:-1]

    return "{scheme}://{host}{path}{query}".format(**locals())


def log(msg):
    # global logging function
    if settings.log_stdout:
        try:
            print "{}: {}".format(datetime.now(), msg)
        except UnicodeEncodeError:
            pass  # squash logging errors in case of non-ascii text


def get_proxy():
    # choose a proxy server to use for this request, if we need one
    if not settings.proxies or len(settings.proxies) == 0:
        return None

    proxy_ip = random.choice(settings.proxies)
    proxy_url = "socks5://{user}:{passwd}@{ip}:{port}/".format(
        user=settings.proxy_user,
        passwd=settings.proxy_pass,
        ip=proxy_ip,
        port=settings.proxy_port,

    )
    return {
        "http": proxy_url,
        "https": proxy_url
    }


def enqueue_url(u):
    url = format_url(u)
    return redis.sadd("listing_url_queue", url)


def dequeue_url():
    return redis.spop("listing_url_queue")


if __name__ == '__main__':
    # test proxy server IP masking
    r = make_request('https://api.ipify.org?format=json', return_soup=False)
    print r.text