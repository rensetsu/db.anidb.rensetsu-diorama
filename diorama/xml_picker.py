from enum import Enum
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from librensetsu.models import ConventionalMapping

class SiteEnum(Enum):
    ANIMENEWSNETWORK = "1"
    MYANIMELIST = "2"
    ANIMENFO = "3"
    OFFWEB = "4"
    OFFENGWEB = "5"
    WIKIENG = "6"
    WIKIJAP = "7"
    SYOBOI = "8"
    ALLCINEMA = "9"
    ANISON = "10"
    LAIN = "11"
    VNDB = "14"
    MARUMEGANE = "15"
    ANIMEMORIAL = "16"
    TVANIMEMUSEUM = "17"
    WIKIKOR = "18"
    WIKIZHO = "19"
    FACEBOOK = "22"
    TWITTER = "23"
    YOUTUBE = "26"
    CRUNCHYROLL = "28"
    MEDIAARTDATABASE = "31"
    AMAZONVIDEO = "32"
    BAIDUBAIKE = "33"
    OFFSTREAM = "34"
    OFFBLOG = "35"
    BANGUMI = "38"
    DOUBAN = "39"
    NETFLIX = "41"
    HIDIVE = "42"
    IMDB = "43"
    TMDB = "44"
    FUNIMATION = "45"
    WEIBOQQ = "46"
    BILIBILI = "47"
    AMAZONPRIMEVIDEO = "48"

class XMLPicker:
    """XMLPicker class"""
    def __init__(self, xml: str):
        """
        XMLPicker class constructor
        :param xml: XML string
        :type xml: str
        """
        self.xml = xml
        self.dom = parseString(xml)
        self.etree = ET.fromstring(xml)

    def _get_text(self, tag: str, attrs: dict[str, str] | None = None) -> str:
        """
        Get text from XML tag
        :param tag: XML tag
        :type tag: str
        :param attrs: XML tag attributes
        :type attrs: dict[str, str]
        :return: Text from XML tag
        :rtype: str
        """
        if attrs is None:
            return self.dom.getElementsByTagName(tag)[0].firstChild.nodeValue
        else:
            for element in self.dom.getElementsByTagName(tag):
                if all(element.getAttribute(key) == value for key, value in attrs.items()):
                    return element.firstChild.nodeValue
        return ""

    @property
    def media_id(self) -> int:
        """
        Get aniDB anime ID
        :return: aniDB anime ID
        :rtype: int
        """
        # <anime id="1" restricted="false">
        return int(self.dom.getElementsByTagName("anime")[0].getAttribute("id"))

    @property
    def media_type(self) -> str:
        """
        Get aniDB anime type
        :return: aniDB anime type
        :rtype: str
        """
        mtype = self._get_text("type")
        mal_eq = {
            "TV Series": "TV",
            "OVA": "OVA",
            "Movie": "Movie",
            "Other": "Special",
            "Web": "ONA",
            "TV Special": "Special",
            "Music Video": "Music",
        }
        return mal_eq.get(mtype, "Unknown")

    @property
    def total_episodes(self) -> int:
        """
        Get aniDB anime total episodes
        :return: aniDB anime total episodes
        :rtype: int
        """
        return int(self._get_text("episodecount"))

    @property
    def start_date(self) -> list[int | None]:
        """
        Get aniDB anime start date
        :return: aniDB anime start date
        :rtype: str
        """
        try:
            start = self._get_text("startdate")
        except IndexError:
            start = ""
        nulled = [None, None, None]
        if start == "":
            return nulled
        elif re.match(r"^\d{4}$", start):
            return [int(start), None, None]
        elif re.match(r"^\d{4}-\d{2}$", start):
            return [int(start.split("-")[0]), int(start.split("-")[1]), None]

        dtime = datetime.strptime(start, "%Y-%m-%d")
        is_end = self.end_date
        if is_end[0] is None and start == "1970-01-01":
            return nulled
        return [dtime.year, dtime.month, dtime.day]

    @property
    def end_date(self) -> list[int | None]:
        """
        Get aniDB anime end date
        :return: aniDB anime end date
        :rtype: list[int | None]
        """
        try:
            end = self._get_text("enddate")
        except IndexError:
            end = ""
        if end == "":
            return [None, None, None]
        elif re.match(r"^\d{4}$", end):
            return [int(end), None, None]
        elif re.match(r"^\d{4}-\d{2}$", end):
            return [int(end.split("-")[0]), int(end.split("-")[1]), None]

        dtime = datetime.strptime(end, "%Y-%m-%d")
        return [dtime.year, dtime.month, dtime.day]

    @property
    def season(self) -> str | None:
        """
        Get aniDB anime season
        :return: aniDB anime season
        :rtype: str
        """
        date = self.start_date
        if date[0] is None or date[1] is None:
            return None

        seasons = {
            "winter": [1, 2, 3],
            "spring": [4, 5, 6],
            "summer": [7, 8, 9],
            "fall": [10, 11, 12],
        }
        for season, months in seasons.items():
            if date[1] in months:
                return season
        return None

    @property
    def display_title(self) -> str:
        """
        Get aniDB anime display title
        :return: aniDB anime display title
        :rtype: str
        """
        # find title with type="main"
        return self._get_text("title", {"type": "main"})

    @property
    def english_title(self) -> str:
        """
        Get aniDB anime english title
        :return: aniDB anime english title
        :rtype: str
        """
        # find title with type="official"
        return self._get_text("title", {"type": "official", "xml:lang": "en"}) 

    @property
    def country_of_origin(self) -> str | None:
        """
        Get aniDB anime country of origin
        :return: aniDB anime country of origin
        :rtype: str
        """
        # Find <name>Japanese*</name>, Chinese*, or South Korean* inside <tags> of every <tag> with ET
        aliases: dict[str, list[str]] = {
            "KR": [
                "South Korean production",
                "South Korean animation",
                "South Korean anime",
                "South Korean cartoon",
                "aeni"
            ],
            "KP": [
                "North Korean production",
                "North Korean animation",
                "North Korean anime",
                "North Korean cartoon",
            ],
            "CN": [
                "Chinese production",
                "Chinese anime",
                "Chinese cartoon",
                "donghua"
            ],
            "JP": [
                "Japanese production",
            ],
            "TW": [
                "Taiwanese production",
            ],
        }
        for tag in self.etree.findall(".//tag"):
            for name in tag.findall("name"):
                for country, values in aliases.items():
                    for value in values:
                        if name.text.lower() == value.lower():
                            return country
        return None

    @property
    def native_title(self) -> str | None:
        """
        Get aniDB anime native title
        :return: aniDB anime native title
        :rtype: str
        """
        # find title with type="official" from self.country_of_origin
        country = self.country_of_origin
        def default_dict(language: str) -> dict[str, str]:
            return {"type": "official", "xml:lang": language}

        final: str = ""

        if country == "CN":
            hans = self._get_text("title", default_dict("zh-Hans"))
            hant = self._get_text("title", default_dict("zh-Hant"))
            final = hans if hans != "" else hant
        elif country == "JP":
            final = self._get_text("title", default_dict("ja"))
        elif country in ["KR", "KP"]:
            final = self._get_text("title", default_dict("ko"))
        return final if final != "" else None

    transliterated_title = display_title

    @property
    def synonyms(self) -> list[str]:
        """
        Get aniDB anime synonyms
        :return: aniDB anime synonyms
        :rtype: list[str]
        """
        final = []
        # get all titles, any attribute
        for title in self.etree.findall("./titles/title"):
            final.append(title.text)
        # remove display, english, and native titles
        try:
            final.remove(self.display_title)
        except ValueError:
            pass
        try:
            final.remove(self.english_title)
        except ValueError:
            pass
        try:
            final.remove(self.native_title)
        except ValueError:
            pass
        names = list(set(final))
        return names.sort()

    @property
    def description(self) -> str:
        """
        Get aniDB anime description
        :return: aniDB anime description
        :rtype: str
        """
        return self._get_text("description")

    @property
    def poster_url(self) -> str | None:
        """
        Get aniDB anime poster URL
        :return: aniDB anime poster URL
        :rtype: str
        """
        try:
            uri = self._get_text("picture")
            url = "https://cdn-us.anidb.net/images/main/"
            if uri == "":
                raise IndexError
            return url + uri
        except IndexError:
            return None

    @property
    def ratings(self) -> dict[str, dict[str, int | float]]:
        """
        Get aniDB anime ratings
        :return: aniDB anime ratings
        :rtype: dict[str, dict[str, int | float]]
        """
        ratings = {}
        #<ratings>
        #    <permanent count="4921">8.22</permanent>
        #    <temporary count="4951">8.21</temporary>
        #    <review count="12">8.70</review>
        #</ratings>
        for rating in self.etree.find("ratings"):
            ratings[rating.tag] = {
                "count": int(rating.get("count")),
                "value": float(rating.text),
            }
        return ratings

    def minutes(self) -> list[int]:
        """
        Get aniDB anime minutes
        :return: aniDB anime minutes
        :rtype: list[int]
        """
        # <episode><length>25</length></episode>
        final = []
        for episode in self.etree.findall(".//episode"):
            try:
                final += [int(episode.find("length").text)]
            except AttributeError:
                final += [0]
        return final[:self.total_episodes]

    @property
    def total_minutes(self) -> int:
        """
        Get aniDB anime total minutes
        :return: aniDB anime total minutes
        :rtype: int
        """
        return sum(self.minutes())

    @property
    def episode_length(self) -> int:
        """
        Get aniDB anime episode length
        :return: aniDB anime episode length
        :rtype: int
        """
        try:
            length = round(self.total_minutes / self.total_episodes)
        except ZeroDivisionError:
            length = 0
        return length

    def _get_identifier(self, site: SiteEnum) -> list[str] | str | None:
        """
        Get identifier from XML tag
        :param site: SiteEnum
        :type site: SiteEnum
        :return: Identifier from XML tag
        :rtype: str
        """
        # <resource type="44">
        #     <externalentity>
        #         <identifier>26209</identifier>
        #         <identifier>tv</identifier>
        #     </externalentity>
        # </resource>
        elm = self.etree.find(f".//resource[@type='{site.value}']")
        if elm is not None:
            return [e.text for e in elm.findall(".//identifier")]
        return None

    @property
    def ann_id(self) -> int | None:
        """
        Get AnimeNewsNetwork ID
        :return: AnimeNewsNetwork ID
        :rtype: int
        """
        ann = self._get_identifier(SiteEnum.ANIMENEWSNETWORK)
        if ann is not None:
            return int(ann[0])
        return None

    @property
    def mal_id(self) -> int | None:
        """
        Get MyAnimeList ID
        :return: MyAnimeList ID
        :rtype: int
        """
        mal = self._get_identifier(SiteEnum.MYANIMELIST)
        if mal is not None:
            return int(mal[0])
        return None

    @property
    def syoboi_tid(self) -> int | None:
        """
        Get Syoboi ID
        :return: Syoboi ID
        :rtype: int
        """
        syoboi = self._get_identifier(SiteEnum.SYOBOI)
        if syoboi is not None:
            return int(syoboi[0])
        return None

    @property
    def allcinema_id(self) -> int | None:
        """
        Get AllCinema ID
        :return: AllCinema ID
        :rtype: int
        """
        allcinema = self._get_identifier(SiteEnum.ALLCINEMA)
        if allcinema is not None:
            return int(allcinema[0])
        return None

    @property
    def mediaartdatabase_id(self) -> str | None:
        """
        Get MediaArtDatabase ID
        :return: MediaArtDatabase ID
        :rtype: str
        """
        madb = self._get_identifier(SiteEnum.MEDIAARTDATABASE)
        if madb is not None:
            return madb[0]
        return None

    @property
    def imdb_id(self) -> ConventionalMapping | None:
        """
        Get IMDb ID
        :return: IMDb ID
        :rtype: str
        """
        imdb = self._get_identifier(SiteEnum.IMDB)
        if imdb is not None:
            return ConventionalMapping(
                id=imdb[0]
            )
        return None

    @property
    def tmdb_id(self) -> ConventionalMapping | None:
        """
        Get TheMovieDatabase ID
        :return: TheMovieDatabase ID
        :rtype: int
        """
        tmdb = self._get_identifier(SiteEnum.TMDB)
        if tmdb is not None:
            return ConventionalMapping(
                id=int(tmdb[0]),
                media_type=tmdb[1]
            )
        return None

    @property
    def bangumi_id(self) -> int | None:
        """
        Get Bangumi ID
        :return: Bangumi ID
        :rtype: int
        """
        bangumi = self._get_identifier(SiteEnum.BANGUMI)
        if bangumi is not None:
            return int(bangumi[0])
        return None

    @property
    def douban_id(self) -> int | None:
        """
        Get Douban ID
        :return: Douban ID
        :rtype: int
        """
        douban = self._get_identifier(SiteEnum.DOUBAN)
        if douban is not None:
            return int(douban[0])
        return None

    @property
    def anison_id(self) -> int | None:
        """
        Get Anison ID
        :return: Anison ID
        :rtype: int
        """
        anison = self._get_identifier(SiteEnum.ANISON)
        if anison is not None:
            return int(anison[0])
        return None
