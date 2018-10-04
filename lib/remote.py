
import re
from lib.analyze_har import filter_image_urls
from progress.spinner import Spinner
from progress.bar import IncrementalBar
from threading import Thread, current_thread
import numpy as np

# handles all remote work
##TODO:
# asynchronize the calls?

def delete_images(paths, sftps):
    print("Banishing {0} images".format(len(paths)))
    THREADS = len(sftps)
    chunked_paths = np.array_split(paths, THREADS)
    workers = []

    for _paths, _sftp in zip(chunked_paths, sftps):
        workers.append(Thread(target=delete_worker_task, args=(_paths, _sftp)))
    
    for worker in workers:
        worker.start()
    
    for worker in workers:
        worker.join()

def delete_worker_task(paths, sftp):
    for i, path in enumerate(paths):
        if i % 500 == 0:
            print('{0}/{1} images deleted {2}'.format(i, len(paths), current_thread()))
        sftp.remove(path)

def get_all_image_paths(ssh_client, directory):
    ssh_client.do("cd " + directory)
    spinner = Spinner('Crawling...')
    paths = crawl_directory(ssh_client, directory, spinner)
    print()
    return filter_image_urls(paths)

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
