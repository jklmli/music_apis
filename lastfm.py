# Copyright (C) 2011 Jiawei Li (http://github.com/jiaweihli)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import urllib
import urllib2
import xml.etree.ElementTree

from music_apis import LASTFM_API_KEY
from music_apis.util import getSourceCode

albumCache = {}
pictureCache = {}

def getPicture(url):
    """
    Returns a dictionary with possible keys:
    'mimetype', 'data'
    """
    if url in pictureCache:
        return pictureCache[url]
    (file, hdr) = urllib.urlretrieve(url)
    mimetype = hdr['Content-Type']
    data = open(file, 'rb').read()
    info = {    'mimetype':mimetype,
                'data':data         }
    pictureCache[url] = info
    return info

def getTrackInfo(track, artist):
    """
    Returns a dictionary with possible keys:
    'title', 'artist', 'album', 'trackPosition', 'picture'
    If no match found, returns empty dictionary
    """
    track = track.encode('utf-8')
    artist = artist.encode('utf-8')
    try:
        url = 'http://ws.audioscrobbler.com/2.0/?'
        url += urllib.urlencode({   'method'        :'track.getinfo',
                                    'api_key'       :LASTFM_API_KEY,
                                    'artist'        :artist,
                                    'track'         :track,
                                    'autocorrect'   :1                  })

        ret = getSourceCode(url)
    #except urllib2.HTTPError:
    except AttributeError:
        return {}
    else:
        info = {}
        tree = xml.etree.ElementTree.XML(ret)
        if tree is not None:
            tree = tree.find('track')
            info['title'] = tree.find('name').text
            info['artist'] = tree.find('artist').find('name').text
            try:
                tree = tree.find('album')
                info['album'] = tree.find('title').text
                info['trackPosition'] = tree.attrib['position']
                info['picture'] = getPicture(tree.findall('image')[-1].text)
            except AttributeError:
                pass
        return info

def getAlbumInfo(album, artist):
    """
    Returns a dictionary with possible keys:
    'album', 'artist', 'picture', 'totalTracks'
    If no match found, returns empty dictionary
    """
    if (album, artist) in albumCache:
        return albumCache[(album,artist)]

    album = album.encode('utf-8')
    artist = artist.encode('utf-8')
    try:
        url = 'http://ws.audioscrobbler.com/2.0/?'
        url += urllib.urlencode({   'method'        :'album.getinfo',
                                    'api_key'       :LASTFM_API_KEY,
                                    'album'         :album,
                                    'artist'        :artist,
                                    'autocorrect'   :1                  })
        ret = getSourceCode(url)
    except urllib2.HTTPError:
        return {}
    else:
        info = {}
        tree = xml.etree.ElementTree.XML(ret)
        if tree is not None:
            tree = tree.find('album')
            info['album'] = tree.find('name').text
            info['artist'] = tree.find('artist').text
            try:
                info['picture'] = getPicture(tree.findall('image')[-1].text)
            except AttributeError:
                pass
            tree = tree.find('tracks')
            info['totalTracks'] = str(len(list(tree)))
            albumCache[(album,artist)] = info
        return info
