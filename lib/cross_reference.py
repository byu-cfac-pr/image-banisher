
from collections import Counter

def get_unreferenced_image_paths(image_paths, image_urls, base_path):
    index = image_paths[0].find(base_path)
    prefix = image_paths[0][:index]

    image_paths = crop_paths(image_paths, base_path)
    image_urls = crop_paths(image_urls, base_path)

    c = Counter(image_paths + image_urls)
    duplicates = []
    for key, value in c.items():
        if value > 1: # there is a duplicate
            duplicates.append(key)
    return [prefix + x for x in image_paths if x not in duplicates]


def crop_paths(paths, base_path):
    cropped = []
    for path in paths:
        index = path.find(base_path)
        if index > -1:
            cropped.append(path[index:])
    return cropped
