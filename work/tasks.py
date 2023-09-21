import logging

import coiled
from dask.distributed import Queue

import contextlib
import threading

lock = threading.Lock()

global cached_client
cached_client = None


@contextlib.contextmanager
def get_client(name):
    global cached_client
    with lock:
        if (cached_client
                and cached_client.scheduler  # check if client is still connected to scheduler
        ):
            yield cached_client
        else:
            logging.warning("making a new client")
            cluster = coiled.Cluster(name=name, shutdown_on_close=False, n_workers=1)
            cluster.adapt(minimum=1, maximum=10, target_duration=60)
            client = cluster.get_client()
            cached_client = client
            yield client


def submit_task(f, arg):
    with get_client("prod") as client:
        future = client.submit(f, arg,
                               # Use "pure=False" if the task should be re-computed even if inputs
                               # match previous inputs. (By default Dask caches, assuming functions are pure.)
                               pure=False)
        Queue(name="prod").put(future)  # Keeps the future around until we clear the queue
        return future.key


def check_status(id):
    with get_client("prod") as client:
        def f(dask_scheduler, key):
            try:
                task = dask_scheduler.tasks[key]
            except KeyError:
                return "does-not-exist"
            else:
                return task.state

        return client.run_on_scheduler(f, key=id)
