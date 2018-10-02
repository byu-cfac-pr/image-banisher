
import re
from lib.analyze_har import filter_image_urls
from progress.spinner import Spinner
from progress.bar import IncrementalBar

# handles all remote work
##TODO:
# asynchronize the calls?

def delete_images(paths, ssh_client, year_month_images_only):
    paths = [path for path in paths if is_year_month(path)]
    print("Banishing {0} images".format(len(paths)))
    suffix = '%(percent)d%% [%(elapsed_td)s / %(eta)d / %(eta_td)s]'
    bar = IncrementalBar('Deleting Images', max=len(paths), suffix=suffix)
    for path in paths:
        ssh_client.do("rm -f {0}".format(path))
        bar.next()
    bar.finish()

def get_all_image_paths(ssh_client, directory):
    ssh_client.do("cd " + directory)
    spinner = Spinner('Crawling...')
    paths = crawl_directory(ssh_client, directory, spinner)
    print()
    return filter_image_urls(paths)

def is_year_month(path):
    indices = [m.start() for m in re.finditer("[0-9][0-9][0-9][0-9]/[0-9][0-9]", path)]
    # if it finds a match, indices will be populated
    return len(indices) > 0


def crawl_directory(ssh_client, directory, spinner):
    spinner.next()
    paths = []
    files = ssh_client.do("ls -l {0}| grep \"^-\"".format(directory))
    directories = ssh_client.do("ls -l {0}| grep \"^d\"".format(directory))

    paths = [directory + "/" + name for name in get_names_only(files)]
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
