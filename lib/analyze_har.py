

# @author: Chase Williams
from pprint import pprint
from browsermobproxy import Server
from selenium import webdriver
from progress.bar import IncrementalBar
## TODO:
# check and see if it is waiting long enough for each page to load. Might need to work with the
# explicit wait.

## TODO:
# some pages aren't up to date and have illegal html formatting. Write in hardcoded rules to avoid those images?

def get_images_urls(page_urls):
    server, driver, proxy = create_chrome_driver()
    image_urls = []
    num_pages = len(page_urls)

    suffix = '%(percent)d%% [%(elapsed_td)s / %(eta)d / %(eta_td)s]'
    bar = IncrementalBar('Loading Webpages', max=num_pages, suffix=suffix)
    for url in page_urls:
        proxy.new_har()
        driver.get(url)
        links = [x['request']['url'] for x in proxy.har['log']['entries']]
        image_urls += filter_image_urls(links)
        bar.next()
    bar.finish()
    server.stop()
    driver.quit()

    return image_urls

def filter_image_urls(links):
    filtered = []
    for link in links:
        for s in ('jpg', 'png', 'jpeg', 'gif'):
            if s in link:
                filtered.append(link)
    return filtered

def create_chrome_driver():
    server = Server("./browsermob/bin/browsermob-proxy")
    server.start()
    proxy = server.create_proxy()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
    return server, webdriver.Chrome(chrome_options = chrome_options), proxy
