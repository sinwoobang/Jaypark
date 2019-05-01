import multiprocessing


workers = multiprocessing.cpu_count() * 2 + 1  # Following the guide in Gunicorn Homepage
