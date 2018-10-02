import requests as http
from pprint import pprint

def get_wordpress_pages(base_url):
    BASE_ENDPOINT = base_url + "/wp-json/wp/v2/pages?per_page=100&page="
    links = []

    r = http.get(BASE_ENDPOINT + str(1))
    links += get_links(r.json())

    i = 2
    pages = int(r.headers['X-WP-TotalPages'])
    while i <= pages:
        r = http.get(BASE_ENDPOINT + str(i))
        links += get_links(r.json())
        i += 1
    return links


def get_links(data):
    return [x['link'] for x in data]
