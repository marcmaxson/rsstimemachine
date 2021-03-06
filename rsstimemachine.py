#!/usr/bin/env python
# python=3.7
# FROM FILE: https://github.com/bburky/rsstimemachine/blob/master/rsstimemachine.py

# Example usage CLI:
#   ./rss_timemachine.py example.com | wget --force-directories --input-file=-
# Example usage as python module
# import rss_timemachine
# urls = rss_timemachine.search_archive(domain)

import sys
import requests

CDX_API_URL = 'http://web.archive.org/cdx/search/cdx'

# This uses an (undocumented?) flag 'id_' to force getting unmodified original files
DOWNLOAD_URL_PATTERN = 'http://web.archive.org/web/{timestamp}id_/{original}'

MIMETYPES = [
    # Possibly add some more general plain text or unkown format mimetypes
    'application/rss+xml',
    'application/rdf+xml',
    'application/atom+xml',
    'application/xml',
    'text/rss+xml',
    'text/xml'
]

# Not sure how restrictive to make this
# (?i) makes the Java format regex case insensitive
# RSS_ORIGINAL_REGEX =  r'(?i).*(rss|atom|feed|blog|podcast|).*\.(xml|rss|atom)
RSS_ORIGINAL_REGEX =  r'(?i).*\.(xml|rss|atom)'

def rss_urls_by_mimetype(domain):
    params = {
        'collapse': 'digest',
        'url': domain,
        'matchType': 'domain',
        'filter': 'mimetype:' + '|'.join(MIMETYPES)
    }

    req = requests.get(CDX_API_URL, params=params)
    # requests.content is 'b' but requests.text is str/unicode -- and line.split requires str not bytestring. changed for 2to3 conversion
    for line in req.text.splitlines():
        urlkey, timestamp, original, mimetype, statuscode, digest, length = line.split(' ')
        if statuscode == '200':
            yield DOWNLOAD_URL_PATTERN.format(timestamp=timestamp, original=original)


def rss_urls_by_original_regex(domain):
    params = {
        'collapse': 'digest',
        'url': domain,
        'matchType': 'domain',
        'filter': 'original:' + RSS_ORIGINAL_REGEX
    }

    req = requests.get(CDX_API_URL, params=params)

    for line in req.text.splitlines():
        urlkey, timestamp, original, mimetype, statuscode, digest, length = line.split(' ')

        if statuscode == '200':
            yield DOWNLOAD_URL_PATTERN.format(timestamp=timestamp, original=original)


def search_archive(domain):
    urls = set()
    urls.update(rss_urls_by_mimetype(domain))
    urls.update(rss_urls_by_original_regex(domain))
    return urls    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('USAGE: %s example.com' % sys.argv[0])

    domain = sys.argv[1]

    urls = set()
    urls.update(rss_urls_by_mimetype(domain))
    urls.update(rss_urls_by_original_regex(domain))

    for url in urls:
        print( url )
