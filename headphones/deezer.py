#  This file is part of Headphones.
#
#  Headphones is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Headphones is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Headphones.  If not, see <http://www.gnu.org/licenses/>

import headphones
import json
import pprint
import os
import re
import deezercustom
import subprocess
import sys

from headphones import logger, helpers, metadata, request
from headphones.common import USER_AGENT
from difflib import SequenceMatcher

from beets.mediafile import MediaFile, UnreadableFileError

def diff_string(str1, str2):
	tolerance=0.8
	m = SequenceMatcher(None, str1, str2)
	#print m.ratio()
	if (m.ratio() > tolerance ):
		return True
	return False

def search(album, albumlength=None, page=1, resultlist=None):
	logger.debug("Deezer Search")

	dic = {'...': '', ' & ': ' ', ' = ': ' ', '?': '', '$': 's', ' + ': ' ',
			'"': '', ',': '', '*': '', '.': '', ':': ''}

	if resultlist is None:
		resultlist = []

	cleanalbum = helpers.latinToAscii(
        helpers.replace_all(album['AlbumTitle'], dic)
        ).strip()
	cleanartist = helpers.latinToAscii(
        helpers.replace_all(album['ArtistName'], dic)
        ).strip()
	
	client = deezercustom.Client()

	search_result = client.advanced_search({"album": cleanalbum.lower(), "artist": cleanartist.lower(), "limit": 100}, relation="album")

	for album in search_result:
		albumtitle_clean = re.sub(r"\([^()]*\)", "", album.title) # removing parenthesis in album title
		if (diff_string(albumtitle_clean.lower(), cleanalbum.lower())):
			if (diff_string(album.artist.name.lower(), cleanartist.lower())):
				logger.debug("Album AND Artist MATCH")
				alb = client.get_album(album.id)
				data = parse_album(alb)
				resultlist.append((
                    data['title'], data['size'], data['url'],
                    'deezer', 'deezer', True))
	pprint.pprint(resultlist)
	return resultlist

def parse_album(album):
	artist = album.artist.name.encode('utf-8')
	album_name = album.title.encode('utf-8')
	ddate = format(album.release_date.encode('utf-8')).split("-")
	year = ddate[0]
	url = album.link.encode('utf-8')
	duration_album = album.duration

	# MP3 offer 320kps 
	size = ((int(duration_album) * 320) / 8 * 1024)

	data = {"title": u'{} - {} [{}]'.format(artist, album_name, year),
            "artist": artist, "album": album_name,
            "url": url, "size": size}
	return data

def download(album, bestqual):
	## deemix prerequisites : python3 + deezer-py 
	logger.debug("downloading album on Deezer")

	# directory to write mp3
	directory = headphones.CONFIG.DEEZER_DIR
	directory = helpers.latinToAscii(directory)

	# working dir for deemix and arl file
	pathcwd = os.path.join(
		"/app/headphones/",
		"tools/deemix/")
	pathcwd = helpers.latinToAscii(pathcwd)

	arl = headphones.CONFIG.DEEZER_ARL
	arlfile = os.path.join(
		pathcwd,
		"config/.arl")
	arlfile = helpers.latinToAscii(arlfile)
	url = bestqual[2].decode('utf-8')

	logger.debug("DOWNLOAD INFO :{}: :{}: :{}:".format(directory, url, pathcwd))

	if not os.path.exists(directory):
		try:
			os.makedirs(directory)
		except Exception as e:
			logger.warn("Could not create directory ({})".format(e))
	
	# write arl file for deemix
	try:
		with open(arlfile, 'w') as f:
			f.write(arl)
	except Exception as e:
		logger.warn("Could write file ({})".format(e))

	# launch deemix with python3
	#p = subprocess.Popen(["python3", "-m", "deemix", "--portable", "--path", directory, url], cwd=pathcwd, stdout=open(os.devnull, 'wb'))
	p = subprocess.Popen(["python3", "-m", "deemix", "--portable", "--path", directory, url], cwd=pathcwd)
	p.communicate()

	return directory
