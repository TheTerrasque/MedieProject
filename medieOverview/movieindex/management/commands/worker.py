from django.core.management.base import BaseCommand, CommandError
from multiprocessing import Process, JoinableQueue, Queue
from django.db import models, transaction
from django.conf import settings

from worker_module import file_worker

import time
import os
from movieindex import models

import logging
L = logging.getLogger("movieindex.worker")

PROCS = 4
EXTENSIONS = ["mpeg", "mp4", "mov", "flv", "avi", "wmv", "m4v", "mkv"]

def scan_folder(mf):
    queue = JoinableQueue()
    rqueue = Queue()
    files_to_add = 0
    workers = []

    print "Spawning workers.."

    for i in range(PROCS):
        p = Process(target=file_worker, args=(queue, rqueue))
        p.daemon = True
        p.start()
        workers.append(p)

    processed = 0

    for root, dirs, nfiles in os.walk(mf.folder):
        for filename in nfiles:
            stripped_root = root[len(mf.folder):]
            subpath = os.path.join(stripped_root, filename).lstrip("\\")
            ext = subpath.split(".")[-1].lower()
            full_path = os.path.join(mf.folder, subpath)

            if ext in EXTENSIONS and not mf.file_exists(subpath):
                d = {
                    "file": full_path,
                    "subpath": subpath
                }
                print "Adding %s to work" % d
                queue.put(d)
                files_to_add += 1
                yield {
                    "done": processed,
                    "total": files_to_add,
                    "file": filename,
                    "status": "Scanning for files"
                }

    while files_to_add > processed:

        processed +=1
        data = rqueue.get()
        err = data.get("error")
        if not err:
            with transaction.atomic():
                mf.add_movie_from_data(data["subpath"], data["movie"], data["screens"])
        yield {
            "done": processed,
            "total": files_to_add,
            "file": data["file"],
            "status": err or "OK"
        }

def handle_work(work):
    if work.task == "SCANFOLDER":
        work.status="Initializing"
        work.save()
        mf = models.MovieFolder.objects.get(id=work.target)
        print "MF is %s" % mf
        for status in scan_folder(mf):
            work.progress = "%s %%" % int(status["done"] / status["total"] * 100.0)
            work.status = "%(file)s: %(status)s" % status
            work.save()
        work.status="DONE"
        work.save()

class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            L.debug("test db")
            L.warn("test w")
            for work in models.WorkerCommand.objects.filter(status="NEW"):
                self.stdout.write("New work")
                handle_work(work)
            time.sleep(0.5)