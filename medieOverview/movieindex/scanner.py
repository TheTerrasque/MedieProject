import os

EXTENSIONS = ["mpeg", "mp4", "mov", "flv", "avi", "wmv", "m4v", "mkv"]

def handle_file(mf, path, category):
    ext = path.split(".")[-1].lower()
    if ext in EXTENSIONS:
        #path = path[len(mf.folder):]
        if not mf.file_exists(path):
            mf.add_movie(path, category)
            return True
        
def scan(mf, category):
    for root, dirs, files in os.walk(mf.folder):
        for f in files:
            try:
                rr = root[len(mf.folder):]
                mr = os.path.join(rr, f).lstrip("\\")
                r = handle_file(mf, mr, category)
                yield mr, f, r and "Added" or "Skipped"
            except:
                yield mr, f, "Error"