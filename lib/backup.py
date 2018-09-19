
from stat import S_ISDIR
import os
import datetime
from progress.bar import IncrementalBar
from progress.spinner import Spinner

##TODO:
# asynchronize the calls?

def create_backup(remote_path, local_path, client):
    sftp = client.client.open_sftp()
    print("Collecting paths to copy")
    spinner = Spinner('Collecting...')
    paths = sftp_walk(sftp, remote_path, spinner)
    print()
    backup_path = os.path.join(local_path, 'backup-' + str(datetime.datetime.now()))
    os.mkdir(backup_path)
    index = len(remote_path)
    num_paths = len(paths)
    print("Copying files into backup")
    suffix = '%(percent)d%% [%(elapsed_td)s / %(eta)d / %(eta_td)s]'
    bar = IncrementalBar('SFTP', max=num_paths, suffix=suffix)
    for path in paths:

        local = backup_path + path[index:]
        create_necessary_subfolders(local)
        sftp.get(path, local)
        bar.next()
    bar.finish()
    return paths

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
