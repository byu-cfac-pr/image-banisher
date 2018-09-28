

# @author: Chase Williams
from pprint import pprint
from browsermobproxy import Server
from selenium import webdriver
from progress.bar import IncrementalBar
import os
import platform
from time import sleep
from pprint import pprint
import requests
import re
import numpy as np
from threading import Thread
## TODO:
# need to add some selenium logic
# - scroll through a website to force loading of all images
# - scroll through slider if present

## TODO: 
# use threading in order to drastically speed this process up. 

def get_image_urls(page_urls):
    THREADS = 5

    chunked_urls = np.array_split(page_urls, THREADS)
    workers = []
    for worker_urls in chunked_urls:
        workers.append(Thread(target=worker_get_images_urls, args=(worker_urls,)))

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()

def worker_get_images_urls(page_urls):
    print('Handling {0} urls'.format(len(page_urls)))
    server, driver, proxy = create_chrome_driver()
    image_urls = []

    #suffix = '%(percent)d%% [%(elapsed_td)s / %(eta)d / %(eta_td)s]'
    #bar = IncrementalBar('Loading Webpages', max=len(page_urls), suffix=suffix)
    for c, url in enumerate(page_urls):
        if c % 5 == 0:
            print('{0} / {1} completed'.format(c, len(page_urls)))
        proxy.new_har()
        driver.get(url)
        scroll_height = driver.execute_script('return document.body.scrollHeight')
        for x in range(0, scroll_height, 1000):
            driver.execute_script('window.scrollTo(0, {0})'.format(x))
            sleep(1)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        sleep(1)
        html = requests.get(url).content.decode('utf-8')
        html_urls = [ html[m.start():m.end()].strip("'\"") for m in re.finditer("[\"']https://[^\s,:]*[\"']", html) ]
        html_urls = filter_image_urls(html_urls)
        links = [x['request']['url'] for x in proxy.har['log']['entries']]
        image_urls += filter_image_urls(links)
        #bar.next()
    #bar.finish()
    
    all_image_urls = list(set(image_urls + html_urls))

    server.stop()
    driver.quit()

    return all_image_urls

def filter_image_urls(links):
    filtered = []
    for link in links:
        for s in ('jpg', 'png', 'jpeg', 'gif'):
            if s in link:
                filtered.append(link)
    return filtered

def create_chrome_driver():
    server = Server(os.path.join(os.getcwd(), 'browsermob', 'bin', 'browsermob-proxy'))
    server.start()
    proxy = server.create_proxy()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
    return server, webdriver.Chrome(chrome_options = chrome_options), proxy
