
from collections import Counter

def get_unreferenced_image_paths(image_paths, image_urls, base_path):
    image_paths = crop_paths(image_paths, base_path)
    image_urls = crop_paths(image_urls, base_path)
    c = Counter(image_paths + image_urls)
    duplicates = []
    for key, value in c.items():
        if value > 1: # there is a duplicate
            duplicates.append(key)
    return [x for x in image_paths if x not in duplicates]


def crop_paths(paths, base_path):
    cropped = []
    for path in paths:
        index = path.find(base_path)
        if index > -1:
            cropped.append(path[index:])
    return cropped

"""
_image_paths = []
_image_urls = []
with open("./image_paths.log") as f:
    _image_paths = f.read().splitlines()
with open("./image_urls.log") as f:
    _image_urls = f.read().splitlines()

unreferenced = get_unreferenced_image_paths(_image_paths, _image_urls, 'cfac-sandbox.byu.edu')
print(len(unreferenced))
"""
