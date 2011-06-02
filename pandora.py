# Copyright (C) 2011 598074 (http://github.com/598074)
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

import ast
import re
import urllib

from util import getSourceCode

regex_lyricIdCheckSum = re.compile('return fetchFullLyrics\((\d*), (\d*), false\)')
regex_trackUid = re.compile('trackUid: "([^"]*)"')

def getLyrics(track, artist):
    """
    Returns a dictionary with possible keys:
    lyrics
    If no match found, returns empty dictionary
    """
    track = track.encode('utf-8')
    artist = artist.encode('utf-8')
    url = 'http://www.pandora.com/music/song/%s/%s' % (urllib.quote_plus(artist.lower()), 
                                                       urllib.quote_plus(track.lower()))
    ret = getSourceCode(url)

    try:
        trackUid = regex_trackUid.search(ret).group(1)
        intermMatch = regex_lyricIdCheckSum.search(ret)

        lyricId = intermMatch.group(1)
        checkSum = intermMatch.group(2)
        nonExplicit = 'false'
        authToken = 'null'
    except AttributeError:
        return {}
    else:
        return __getEncryptedLyrics(trackUid, lyricId, checkSum, nonExplicit, authToken)

def __getEncryptedLyrics(trackUid, lyricId, checkSum, nonExplicit, authToken):
    url = "http://www.pandora.com/services/ajax/?"
    url += urllib.urlencode({   'method'       :'lyrics.getLyrics',
                                'trackUid'     :trackUid,
                                'checkSum'     :checkSum,
                                'nonExplicit'  :nonExplicit,
                                'authToken'    :authToken           }) 
    ret = getSourceCode(url)

    decryptionKey = re.search('var k="([^"]*)"', ret).group(1)

    # functions in javascript can contain ", which makes python dictionary 
    # parsing throw errors, workaround by replacing them out
    ret = re.sub('(function[^,]*)', '0', ret).replace('\\u00',r'\x')

    # use ast.literal_eval vs. eval because it's safer
    encrypted = ast.literal_eval(ret)

    encryptedLyrics= encrypted['lyrics']
    return __decryptLyrics(encryptedLyrics, decryptionKey)

def __decryptLyrics(encryptedLyrics, decryptionKey):
    # TODO: use string.join instead of + concatenation (might not be possible, 
    # since relies on mod func)
    decryptedLyrics = ""
    for i in range(0, len(encryptedLyrics)):
        decryptedLyrics += unichr(ord(encryptedLyrics[i]) ^ 
                                  ord(decryptionKey[i % len(decryptionKey)]) )
    return {'lyrics': decryptedLyrics}