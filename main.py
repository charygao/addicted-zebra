#!/usr/bin/env python

# Torrent RSS pecification
# http://www.bittorrent.org/beps/bep_0036.html

import json
import urllib
import urllib2
import xml.etree.ElementTree as ET
import logging


PITCHFORK_RSS = 'http://pitchfork.com/rss/reviews/albums/'
TPB_SEARCH = 'http://apify.ifc0nfig.com/tpb/search?id={}'


def fetch_pitchfork_reviews_rss(url=PITCHFORK_RSS):
    # TODO(alexkuk) Namespace is actually 'atom' not ''
    ET.register_namespace('', 'http://www.w3.org/2005/Atom')
    return ET.parse(urllib2.urlopen(url))


def fetch_tpb_search_results(query, url=TPB_SEARCH):
    request = url.format(urllib.quote(query))
    return json.load(urllib2.urlopen(request))


def get_best_search_result(results):
    if results:
        music = filter(lambda r: r['category'] in ('Music', 'FLAC'), results)
        if music:
            popular = sorted(music,
                             key=lambda r: r['leechers'] + r['seeders'],
                             reverse=True)
            return popular[0]


def get_magnet_link(search_result):
    if search_result:
        return search_result['magnet']


def torrentify_rss(rss):
    for channel in rss.getroot():
        for item in channel.findall('item'):
            title = item.find('title').text
            magnet = get_magnet_link(get_best_search_result(fetch_tpb_search_results(title)))
            if magnet:
                enclosure = ET.SubElement(item, 'enclosure')
                enclosure.set('url', magnet)
                enclosure.set('type', 'application/x-bittorrent')
            else:
                channel.remove(item)
            

def save_rss(rss, filename='pitchfork.rss'):
    rss.write(filename, encoding='utf-8', xml_declaration=True)


