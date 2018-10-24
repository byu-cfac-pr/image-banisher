from lib.wordpress import get_wordpress_pages
from lib.analyze_har import get_images_urls
from lib.ssh_client import Client
from lib.remote import get_all_image_paths, delete_images
from lib.cross_reference import get_unreferenced_image_paths
from lib.backup import create_backup
from paramiko.sftp_client import SFTPClient
from paramiko.ssh_exception import ChannelException
from ruamel.yaml import YAML
from pprint import pprint
from time import time

"""
@author: Chase Williams
Image Banishment Wizard that deletes unreferenced images for a Wordpress website.
"""
print("Welcome to the Image Banisher wizard!")

## TODO:
# only delete images that are older than a certain year? Maybe do some quick analysis - surely deleting pre-2015 images would be safe but also effective

yaml = YAML(typ="safe")
configs = {}
with open('config.yml') as f:
    configs = yaml.load(f)

WORDPRESS_SITE_URL = configs['wordpress']['url']
YEAR_MONTH_IMAGES_ONLY = configs['wordpress']['delete_year_month_images_only'] == 'true'
USERNAME = configs['server']['username']
SERVER_URL = configs['server']['url']
KEY_PATH = configs['server']['local_key_path']
PASSPHRASE = configs['server']['passphrase']
BANISHMENT_PATH = configs['server']['banishment_path']
CREATE_BACKUP = configs['backup']['create_backup'] == 'true'
BACKUP_PATH = configs['backup']['local_backup_path']

print("Be patient, this might take a while")
start_time = time()
pages = get_wordpress_pages()

print("Wordpress Live URLs identified")
with open('wordpress_urls.log', 'w') as f:
    for url in pages:
        f.write(url + "\n")

image_urls = get_images_urls(pages, threads=5)

with open('image_urls.log', 'w') as f:
    for url in image_urls:
        f.write(url + "\n")

print("HARs analyzed, all image URLs have been logged. {0} seconds so far.".format(time() - start_time))

## NOTE
# This creates the ~10 SFTP objects that can be used for either single or multithreading
# the I/O jobs
client = Client(USERNAME, SERVER_URL, KEY_PATH, PASSPHRASE)
MAX_THREADS = 10
print('Attempting to open {0} channels'.format(MAX_THREADS))
sftps = []
for i in range(MAX_THREADS):
    try:
        sftps.append(SFTPClient.from_transport(client.client.get_transport()))
    except ChannelException:
        break

image_paths = get_all_image_paths(client, BANISHMENT_PATH)
with open('image_paths.log', 'w') as f:
    for path in image_paths:
        f.write(path + "\n")
print("All image paths on the server have been logged. {0} seconds so far.".format(time() - start_time))

base_url = WORDPRESS_SITE_URL[(WORDPRESS_SITE_URL.find("//") + 2):]
unreferenced = get_unreferenced_image_paths(image_paths, image_urls, base_url, YEAR_MONTH_IMAGES_ONLY)
with open('images_to_delete.log', 'w') as f:
    for path in unreferenced:
        f.write(path + "\n")
print("Unreferenced images identified. {0} seconds so far.\n{1} / {2} images are unreferenced".format(time() - start_time, len(unreferenced), len(image_paths)))

if CREATE_BACKUP:
    create_backup(BANISHMENT_PATH, BACKUP_PATH, client, sftps)

delete_images(unreferenced, sftps)

print("Finished! Banishment took {0} seconds".format(time() - start_time))
# TODO:
# also print out number of images removed, storage reduction, and total number of images
