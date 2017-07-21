from movieindex.film_parser import MovieDataExtractor
from movieindex.video_extracter import MovieDataExtractorFFmpeg
from django.conf import settings

fetcher = MovieDataExtractorFFmpeg(settings.FFMPEG)
extractor = MovieDataExtractor(fetcher)

import logging
L = logging.getLogger("movieindex.workermodule")

def file_worker(task_queue, return_queue):
    while True:
        task = task_queue.get()
        f = task.get("file")
        try:
            extractor.metadata = None
            d = {
                "movie": extractor.get_movie_info(f),
                "screens": extractor.make_screenshots(f),
                "file": f,
                "subpath": task.get("subpath")
            }
            return_queue.put(d)
            print "Processed %s" % task.get("subpath")
        except Exception as e:
            d = {
                "file": f,
                "error": "Couldn't parse file",
                "exception": unicode(e)
            }
            return_queue.put(d)
            print "Worker Exception: %s" % e
        task_queue.task_done()