import os


class MovieDataExtractor(object):
    metadata = None
    
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def get_movie_data(self, path):
        self.metadata = None
        e = {
            "movie": self.get_movie_info(path),
            "screens": self.make_screenshots(path),
        }
        return e
    
    def get_info(self, path):
        if not self.metadata:
            self.metadata = self.fetcher.get_info(path)
        return self.metadata
        
    def get_movie_info(self, path):
        i = self.get_info(path)
        m = {}
        m["title"] = os.path.basename(path)
        m["size"] = os.path.getsize(path)
        m["length"] = i["seconds"]
        m["height"] = [int(x) for x in i["resolution"].split("x")][0]
        m["width"] = [int(x) for x in i["resolution"].split("x")][1]
        m["fps"] = float(i["fps"])
        m["codec"] = i["codec"]
        m["bitrate"] = int(i["bitrate"])
        return m
        
    def make_screenshots(self, path, num=9):
        length = self.get_info(path).get("seconds")
        dur = length / (num + 2)
        c = 0
        l = []
        for x in range(num):
            c += dur
            data = self.fetcher.get_thumb(path, c)
            l.append({
                "data": data,
                "seconds": c,
            })
        return l