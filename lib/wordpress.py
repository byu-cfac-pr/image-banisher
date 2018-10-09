import requests as http
from pprint import pprint
from progress.bar import IncrementalBar

def get_wordpress_pages(base_url):
    BASE_PAGES_ENDPOINT = base_url + "/wp-json/wp/v2/pages?per_page=100&page="
    BASE_POSTS_ENDPOINT = base_url + "/wp-json/wp/v2/posts?per_page=100&page="
    links = []

    r_pages = http.get(BASE_PAGES_ENDPOINT + str(1))
    links += get_links(r_pages.json())
    r_posts = http.get(BASE_POSTS_ENDPOINT + str(1))
    links += get_links(r_posts.json())

    api_calls_to_make = int(r_pages.headers['X-WP-TotalPages']) + int(r_posts.headers['X-WP-TotalPages']) - 2
    suffix = '%(percent)d%% [%(elapsed_td)s / %(eta)d / %(eta_td)s]'
    bar = IncrementalBar('Collecting Wordpress URLs', max=api_calls_to_make, suffix=suffix)

    i = 2
    pages = int(r_pages.headers['X-WP-TotalPages'])
    while i <= pages:
        r = http.get(BASE_PAGES_ENDPOINT + str(i))
        links += get_links(r.json())
        i += 1
        bar.next()
    i = 2
    pages = int(r_posts.headers['X-WP-TotalPages'])
    while i <= pages:
        r = http.get(BASE_POSTS_ENDPOINT + str(i))
        links += get_links(r.json())
        i += 1
        bar.next()
    bar.finish()
    return links


def get_links(data):
    return [x['link'] for x in data]
