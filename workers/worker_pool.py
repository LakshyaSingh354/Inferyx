from multiprocessing import Process
from workers.worker_loop import worker_loop

MAX_WORKERS = 6


def start_worker_pool():
    workers = []
    for i in range(MAX_WORKERS):
        p = Process(target=worker_loop, args=(i,))
        p.start()
        workers.append(p)

    for p in workers:
        p.join()