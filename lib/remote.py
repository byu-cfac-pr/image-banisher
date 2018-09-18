
import re
from lib.analyze_har import filter_image_urls
from progress.spinner import Spinner
# handles all remote work

def get_all_image_paths(ssh_client, directory):
    ssh_client.do("cd " + directory)
    spinner = Spinner('Crawling...')
    paths = crawl_directory(ssh_client, directory, spinner)
    return filter_image_urls(paths)


def crawl_directory(ssh_client, directory, spinner):
    spinner.next()
    paths = []
    files = ssh_client.do("ls -l {0}| grep \"^-\"".format(directory))
    directories = ssh_client.do("ls -l {0}| grep \"^d\"".format(directory))

    paths = [directory + name for name in get_names_only(files)]
    for folder in get_names_only(directories):
        new_path = directory + "/" + folder
        paths += crawl_directory(ssh_client, new_path, spinner)
    return paths


def get_names_only(data):
    lines = data.split("\n")
    names = []
    for line in lines:
        indices = [m.start() for m in re.finditer("\s[^\s]", line)]
        # start on the eight space, where file name starts
        if len(indices) < 7:
            continue
        try:
            name = line[indices[7]:]
        except:
            print("failure")
            print(line)
            print(indices)
        names.append(name.strip())
    return names
"""
from ssh_client import Client
c = Client('cfacprwe', 'cfacprweb.byu.edu', './id_rsa', 'iuch2K284')
result = get_all_image_paths(c, '/home/cfacprwe/public_html/cfac-sandbox.byu.edu/wp-content/uploads')
with open('image_paths.log', 'w') as f:
    for path in result:
        f.write(path + "\n")
"""
