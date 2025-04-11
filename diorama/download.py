import requests as req
from fake_useragent import FakeUserAgent
from alive_progress import alive_bar

from consts import pprint, Status

def download_archive() -> bool:
    url = 'https://files.shokoanime.com/files/shoko-server/other/Anime_HTTP.zip'
    ua = FakeUserAgent().random
    headers = {'User-Agent': ua}
    try:
        with req.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            pprint.print(Status.INFO, 'Downloading Anime_HTTP.zip')
            total_size = int(r.headers.get('content-length', 0)) + 1
            with open('Anime_HTTP.zip', 'wb') as f, alive_bar(total_size, unit="B", scale="IEC") as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar(8192)
            pprint.print(Status.PASS, 'Downloaded Anime_HTTP.zip')
            return True
    except req.exceptions.RequestException as e:
        pprint.print(Status.FAIL, f'Failed to download Anime_HTTP.zip: {e}')
        return False
