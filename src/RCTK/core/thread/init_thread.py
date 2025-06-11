import multiprocessing as mp

def init():
    mp.set_start_method("forkserver")