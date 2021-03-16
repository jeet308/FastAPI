import os

def pathfound(filename):
    listing = os.walk('/')
    for root_path,directories,files in listing:
        if filename in files:
            path = os.path.join(root_path,filename)
            #print(path)
        else:
            None
    return path




