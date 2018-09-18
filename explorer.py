import os
import datetime

## THIS IS PYTHON 2.7
# @author: chase

def check_files(directory):
    files = [] # every element is a tuple (name, size)
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        size = os.path.getsize(path)
        if os.path.isdir(path):
            files = files + check_files(path)
        else:
            files.append((path, size))
    return files


def is_image_file(path):
    for s in ('jpg', 'png', 'jpeg', 'gif'):
        if s in path:
            return True
    return False

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','Ti','Pi','Ei','Zi']:
        if abs(num) < 1000.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1000.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

files = check_files(os.getcwd())
total_storage_use = {}
for file in files:
    index = file[0].rfind('.')
    if index != -1:
        file_type = file[0][index:]
    else:
        file_type = file[0]
    if file_type in total_storage_use:
        total_storage_use[file_type] += file[1]
    else:
        total_storage_use[file_type] = file[1]


log_file_name = 'disk_usage_logs' + '.csv'
condensed_storage_use = []
for k, d in total_storage_use.iteritems():
    if d > 100:
        condensed_storage_use.append((k, d))

func = lambda x : x[1]
condensed_storage_use.sort(key=func, reverse=True)

with open(log_file_name, 'w') as f:
    for file in condensed_storage_use:
        f.write(file[0] + "," + sizeof_fmt(file[1]) + "\n")
