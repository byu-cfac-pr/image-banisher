from lib.wordpress import get_wordpress_pages
from lib.analyze_har import get_images_urls
from lib.ssh_client import Client
from lib.remote import get_all_image_paths
from lib.cross_reference import get_unreferenced_image_paths
from lib.backup import create_backup
from pprint import pprint
from time import time

# TODO:
# https://medium.com/@keagileageek/paramiko-how-to-ssh-and-file-transfers-with-python-75766179de73

print("Welcome to the Image Banisher wizard!")
# TODO:
# any other advice?
print("While completing the wizard, please do not end any URLs with trailing slashes. Additionally, include the http protocol in the url.")
print("What is the Wordpress site URL you are cleaning up today?")
WORDPRESS_SITE_URL = input()
## ssh authentication assumption: going to use id_rsa on local machine
print("Please provide the username and server URL")
USERNAME = input("username: ")
SERVER_URL = input("server_url: ")
print("Please provide the path to the private key file and the passphrase")
KEY_PATH = input("key path: ")
PASSPHRASE = input("passphrase: ")
print("Please provide the path to the root folder you wish to initiate image banishment (probably at ..../wp-content/uploads/)")
BANISHMENT_PATH = input()
print("Where would you like to store a backup of {0} on your local machine?".format(BANISHMENT_PATH))
BACKUP_PATH = input()

# TODO:
# need to also ask for Box information and backup method


# TODO:
# print out all entered information
print("Do you wish to start image banishment? (y/n)")
if input() == 'y':
    print("Be patient, this might take a while")
    start_time = time()
    pages = get_wordpress_pages(WORDPRESS_SITE_URL)
    image_urls = get_images_urls(pages)

    with open('image_urls.log', 'w') as f:
        for url in image_urls:
            f.write(url + "\n")

    print("HARs analyzed, all image URLs have been logged. {0} seconds so far.".format(time() - start_time))

    client = Client(USERNAME, SERVER_URL, KEY_PATH, PASSPHRASE)
    image_paths = get_all_image_paths(client, BANISHMENT_PATH)
    with open('image_paths.log', 'w') as f:
        for path in image_paths:
            f.write(path + "\n")
    print("All image paths on the server have been logged. {0} seconds so far.".format(time() - start_time))

    base_url = WORDPRESS_SITE_URL[(WORDPRESS_SITE_URL.find("//") + 2):]
    unreferenced = get_unreferenced_image_paths(image_paths, image_urls, base_url)
    with open('images_to_delete.log', 'w') as f:
        for path in unreferenced:
            f.write(path + "\n")
    print("Unreferenced images identified. {0} seconds so far.\n{1} / {2} images will be banished".format(time() - start_time, len(unreferenced), len(image_paths)))

    ## TODO:
    # create backup (of /uploads/ folder or BANISHMENT_PATH, not entire website)

    create_backup(BANISHMENT_PATH, BACKUP_PATH, client)
    ## TODO:
    # copy unreferenced images to archive location

    print("Finished! Banishment took {0} seconds".format(time() - start_time))
    # TODO:
    # also print out number of images removed, storage reduction, and total number of images
