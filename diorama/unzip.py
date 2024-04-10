"""Unzip a file to a directory"""

from sys import exit as sysexit
import zipfile
from typing import Any, Union
from consts import Status, pprint, Platform
from alive_progress import alive_bar

def unzip(file: Union[str, bytes, Any], directory: str) -> None:
    """Unzip a file to a directory"""
    old_platform = pprint.platform
    pprint.platform = Platform.SYSTEM
    try:
        with zipfile.ZipFile(file, 'r') as z:
            pprint.print(Status.INFO, f'Unzipping {file}')
            with alive_bar(len(z.infolist())) as bar:
                for f in z.infolist():
                    z.extract(f, directory)
                    bar()
            pprint.print(Status.PASS, f'Unzipped {file}')
        pprint.platform = old_platform
        return
    except zipfile.BadZipFile:
        pprint.print(Status.FAIL, f'Failed to unzip {file}: Not a valid ZIP file or it is corrupted') 
    except zipfile.LargeZipFile:
        pprint.print(Status.FAIL, f'Failed to unzip {file}: ZIP file is too large')
    except Exception as e:
        pprint.print(Status.FAIL, f'Failed to unzip {file}: {e}')

    sysexit(1)