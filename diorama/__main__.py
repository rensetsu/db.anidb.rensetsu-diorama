from sys import exit as sysexit

from download import download_archive
from unzip import unzip
from consts import pprint, Status
from loops import do_loop
from time import time
from librensetsu.humanclock import convert_float_to_time

def main():
    start = time()
    try:
        pprint.print(Status.INFO, 'Starting Diorama scraper for AniDB')
        if not download_archive():
            pprint.print(Status.ERR, 'Failed to download Anime_HTTP.zip')
            sysexit(1)
        unzip('Anime_HTTP.zip', '')
        pprint.print(Status.INFO, 'Starting loop')
        do_loop()
        end = time()
        pprint.print(Status.PASS, 'Finished loop, exiting')
        pprint.print(Status.INFO, f'Time elapsed: {convert_float_to_time(end - start)}')
        sysexit(0)
    except Exception as e:
        pprint.print(Status.ERR, f'An error occurred: {e}')
        end = time()
        pprint.print(Status.INFO, f'Time elapsed: {convert_float_to_time(end - start)}')
        sysexit(1)

if __name__ == '__main__':
    main()
