from xml_picker import XMLPicker
from librensetsu.models import MediaInfo, Date, RelationMaps, PictureUrls
from librensetsu.formatter import remove_empty_keys
from uuid import uuid4
import json
import os
import re
from alive_progress import alive_bar
from dataclasses import asdict
from consts import pprint, Status
from copy import deepcopy

def process_file(file_path: str, data_uuid: str | None = None) -> MediaInfo:
    """
    Process a file
    :param file_path: Path to the file
    :type file_path: str
    :param data_uuid: UUID of the data, if any
    :type data_uuid: str | None
    :return: MediaInfo object
    :rtype: MediaInfo
    """
    with open(file_path, 'r') as f:
        xml = f.read()
    picker = XMLPicker(xml)
    start_date = picker.start_date
    end_date = picker.end_date
    episodes: int | None = picker.total_episodes
    if episodes == 0:
        episodes = None
    picture = picker.poster_url
    picstruct = PictureUrls(
        original=picture,
    )
    media_info = MediaInfo(
        uuid=data_uuid or str(uuid4()),
        title_display=picker.display_title,
        title_native=picker.native_title,
        title_english=picker.english_title,
        title_transliteration=picker.transliterated_title,
        synonyms=picker.synonyms,
        is_adult=None,
        media_type="anime",
        media_sub_type=picker.media_type,
        year=start_date[0],
        start_date=Date(
            year=start_date[0],
            month=start_date[1],
            day=start_date[2]
        ),
        end_date=Date(
            year=end_date[0],
            month=end_date[1],
            day=end_date[2]
        ),
        unit_counts=episodes,
        unit_order=None,
        subunit_counts=picker.total_minutes,
        subunit_order=picker.episode_length,
        volume_counts=None,
        volume_order=None,
        season=picker.season,
        picture_urls=[picstruct] if picture else [],
        country_of_origin=picker.country_of_origin,
        mappings=RelationMaps(
            anidb=picker.media_id,
            allcinema=picker.allcinema_id,
            animenewsnetwork=picker.ann_id,
            myanimelist=picker.mal_id,
            syoboical=picker.syoboi_tid,
            bangumi=picker.bangumi_id,
            douban=picker.douban_id,
            anison=picker.anison_id,
            tmdb=picker.tmdb_id,
            imdb=picker.imdb_id,
        ),
        source_data="anidb",
    )
    return media_info

def do_loop() -> list[MediaInfo]:
    """
    Looping all files in the Anime_HTTP/ directory
    :return: List of MediaInfo objects
    :rtype: list[MediaInfo]
    """
    try:
        with open("anidb.json", 'r') as f:
            old_info = json.load(f)
    except FileNotFoundError:
        old_info = []
        loi = len(old_info)
    new_info = []
    with alive_bar(len(os.listdir("Anime_HTTP"))) as bar:
        for file in os.listdir("Anime_HTTP"):
            if not file.endswith(".xml"):
                bar()
                continue
            file_path = os.path.join("Anime_HTTP", file)
            data_uuid = None
            # get AniDB ID from Anime_HTTP/AnimeDoc_{id}.xml
            media_id = int(re.search(r"AnimeDoc_(\d+).xml", file).group(1))
            if loi > 0:
                for info in old_info:
                    if info['mappings']['anidb'] == media_id:
                        data_uuid = info['uuid']
                        break
            new_info.append(process_file(file_path, data_uuid))
            bar()
    # dump new info
    pprint.print(Status.INFO, "Completed loop, converting dataclasses to dict")
    new_info = [asdict(info) for info in new_info]
    # sort by anidb id
    pprint.print(Status.INFO, "Sorting by AniDB ID")
    new_info.sort(key=lambda x: int(x['mappings']['anidb']))
    pprint.print(Status.INFO, "Dumping to anidb.json")
    with open("anidb.json", 'w') as f:
        json.dump(new_info, f, ensure_ascii=False)
    # remove all keys that the value is either None, empty list, or empty dict, recursively
    pprint.print(Status.INFO, "Creating anidb_min.json")
    mininfo = deepcopy(new_info)
    mininfo = remove_empty_keys(mininfo)
    pprint.print(Status.INFO, "Dumping to anidb_min.json")
    with open("anidb_min.json", 'w') as f:
        json.dump(mininfo, f, ensure_ascii=False)
    return new_info
