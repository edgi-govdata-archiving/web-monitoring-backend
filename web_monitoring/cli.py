# Command Line Interface
# All the functionality is implemented in this module. See scripts/ for
# executables.
from docopt import docopt
import hashlib
import io
import lxml.html
import requests
from tqdm import tqdm
from web_monitoring import internetarchive as ia
from web_monitoring import db


# These functions lump together library code into monolithic operations for the
# CLI. They also print. To access this functionality programmatically, it is
# better to use the underlying library code.


def _extract_title(content_bytes):
    "Return content of <title> tag as string."
    content_as_file = io.StringIO(content.decode(errors='ignore'))
    title = lxml.html.parse(content_as_file).find(".//title").text
    return title


def import_ia(url, agency, site):
    print('obtaining versions list from Internet Archive...')
    versions = ia.list_versions(url)
    # Collect all the results and POST them as a unit (rather than streaming).
    formatted_versions = []
    for dt, uri in tqdm(versions, desc='formatting versions'):
        res = requests.get(uri)
        assert res.ok
        version_hash = hashlib.sha256(res.content).digest()
        title = _extract_title(res.content)
        v = ia.format_version(url=url, dt=dt, uri=uri,
                              version_hash=version_hash, title=title,
                              agency=agency, site=site)
        formatted_versions.append(v)
    print('posting to db....')
    db.post_to_db(formatted_versions)


def main():
    doc = """Command Line Interface to the web_monitoring Python package

    Usage:
    wm import ia <url> --site <site> --agency <agency>
    wm import pf <url>

    Options:
    -h --help     Show this screen.
    --version     Show version.

    """
    arguments = docopt(doc, version='0.0.1')
    if arguments['import']:
        if arguments['ia']:
            import_ia(url=arguments['<url>'],
                      agency=arguments['<agency>'],
                      site=arguments['<site>'])
