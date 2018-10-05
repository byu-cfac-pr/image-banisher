
from collections import Counter
from progress.bar import IncrementalBar
import re

def get_unreferenced_image_paths(image_paths, image_urls, base_path, year_month_images_only):
    ## There are two constraints to deleting images found in both image_paths and image_urls:
    # - the image is not in a YYYY/MM/ folder and user constrains deletion to those paths
    # - the image is tracked by the bfi_thumb plugin

    ## NOTE
    # the bfi_thumb plugin is extraordinarily annoying. It passes temporary image URLs to the HTML
    # document, and regenerates copies of the base image periodically (not sure what the trigger is)
    # So, if the target image is /2018/03/des-21-1.jpg, the plugin will create the image 
    # /bfi_thumb/des-21-1-[ HASH ].jpg, where the hash is approximately 42+ characters. Then, that path
    # is placed in the HTML. So, we have to identify these mirror images, and then avoid deleting the 
    # base image, otherwise bfi_thumb will throw a fit when its unable to regenerate the image. 
    image_paths = filter_base_images(image_paths)

    if year_month_images_only:
        image_paths = [path for path in image_paths if is_year_month(path)]
    
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

def filter_base_images(paths):
    """
    Filters out the base image if it has mirror images 
    """
    filtered_paths = paths.copy()
    suffix = '%(percent)d%% [%(elapsed_td)s / %(eta)d / %(eta_td)s]'
    bar = IncrementalBar('Filtering mirror images', max=len(paths), suffix=suffix)   
    patterns = []
    for path in paths:
        # matches paths with a hyphen followed by a 30+ alphanumeric character hash, and then the filepath extension
        # we could do 42+ as aforementioned, but I'm playing it safe with 30. Better safe than sorry, 
        # as I'm not sure what algorithm creates the hash. 

        indices = [m.start() for m in re.finditer("-\w{30,}\.", path)] 
        
        if len(indices) > 0:
            # construct what must be the base image path
            begin = indices[0]
            patterns.append(path[path.rfind('/')+1:begin])

            #filtered_paths = list(filter(lambda x: re.search('{0}\.'.format(pattern), x) == None, filtered_paths))
        bar.next()
    filtered_paths = list(filter(lambda path: all([re.search('{0}\.'.format(pattern), path) == None for pattern in patterns]), filtered_paths))
    bar.finish()

    return filtered_paths

def is_year_month(path):
    indices = [m.start() for m in re.finditer("[0-9][0-9][0-9][0-9]/[0-9][0-9]", path)]
    # if it finds a match, indices will be populated
    return len(indices) > 0

def crop_paths(paths, base_path):
    cropped = []
    for path in paths:
        index = path.find(base_path)
        if index > -1:
            cropped.append(path[index:])
    return cropped
