
from stat import S_ISDIR
import os
import datetime
import numpy as np
from progress.bar import IncrementalBar
from progress.spinner import Spinner
from paramiko.sftp_client import SFTPClient
from paramiko.ssh_exception import ChannelException, SSHException
from threading import Thread, current_thread


def create_backup(remote_path, local_path, client, sftps):
    sftp = client.client.open_sftp()
    print("Collecting paths to copy")
    spinner = Spinner('Collecting...')
    remote_paths = sftp_walk(sftp, remote_path, spinner)
    print()
    backup_path = os.path.join(local_path, 'backup-' + str(datetime.datetime.now()))
    os.mkdir(backup_path)
    index = len(remote_path)
    print("Creating local directories for file transfer")
    ## Create all local directories necessary
    local_paths = []
    for path in remote_paths:
        local = backup_path + path[index:]
        create_necessary_subfolders(local)
        local_paths.append(local)
        #sftp.get(path, local)
    print('Copying files over')
    ## Create worker threads
    # first check how many channels are allowed
    

    THREADS = len(sftps)
    print('Opening {0} channels'.format(THREADS))
    
    # set up the workers
    chunked_remote_paths = np.array_split(remote_paths, THREADS)
    chunked_local_paths = np.array_split(local_paths, THREADS)

    workers = []
    for _remote_paths, _local_paths, sftp in zip(chunked_remote_paths, chunked_local_paths, sftps):
        workers.append(Thread(target=copy_worker, args=(client, sftp, _remote_paths, _local_paths)))
    
    for worker in workers:
        worker.start()
    
    for worker in workers:
        worker.join()

def copy_worker(client, sftp, remote_paths, local_paths):
    i = 1
    for remote, local in zip(remote_paths, local_paths):
        if i % 500 == 0:
            print('{0}/{1} copied over {2}'.format(i, len(remote_paths), current_thread()))
        try:
            sftp.get(remote, local)
        except SSHException:
            client.construct_client()
            sftp = SFTPClient.from_transport(client.client.get_transport())
            sftp.get(remote, local)
        i = i + 1

def create_necessary_subfolders(path):
    dirs = path.split('/')[1:-1]
    for index, directory in enumerate(dirs):
        try:
            dir_path = '/' + '/'.join(dirs[:(index + 1)])
            os.mkdir(dir_path)
        except:
            continue

def sftp_walk(sftp, directory, spinner):
    spinner.next()
    paths = []
    files = []
    folders = []
    for f in sftp.listdir_attr(directory):
        if S_ISDIR(f.st_mode):
            folders.append(f.filename)
        else:
            files.append(f.filename)

    for f in files:
        paths.append(os.path.join(directory, f))
    for f in folders:
        paths += sftp_walk(sftp, os.path.join(directory, f), spinner)

    return paths
