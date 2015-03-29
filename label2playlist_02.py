import subprocess
import operator
import pprint
import sys
import os

import pyen

import spotipy
import spotipy.util as util

from pymongo import MongoClient

from music_apis_keys import ECHONEST_API_KEY
from music_apis_keys import ECHONEST_CONSUMER_KEY
from music_apis_keys import ECHONEST_SHARED_SECRET

from music_apis_keys import SPOTIFY_CLIENT_ID as SPOTIPY_CLIENT_ID
from music_apis_keys import SPOTIFY_CLIENT_SECRET as SPOTIPY_CLIENT_SECRET
from music_apis_keys import SPOTIFY_REDIRECT_URI as SPOTIPY_REDIRECT_URI

SP_USERNAME = 's8'

DO_CLIENT = MongoClient('localhost:27017')

DISCOGS = DO_CLIENT['discogs']
DO_ARTISTS = DISCOGS['artists']
DO_MASTERS = DISCOGS['masters']
DO_RELEASES = DISCOGS['releases']
DO_LABELS = DISCOGS['labels']

# request = 'zazen boys'
# request = 'polysics'
# request = 'jaga jazzist'
# request = 'aphex twin'
request = 'moving units'
# request = 'kyuss'
# request = 'queens of the stone age'
# request = 'aerosmith'
# request = 'nicki minaj'
# request = 'flanger'
# request = 'burnt friedman & jaki liebezeit'
# request = 'bernd friedmann'
# request = 'lcd soundsystem'


# ========================================================================
# SPOTIFY methods
# ========================================================================

def sp_create_playlist(username, playlist_name):

	scope = 'playlist-modify-public'
	token = util.prompt_for_user_token(username,scope, client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET, redirect_uri = SPOTIPY_REDIRECT_URI)

	if token:
		sp = spotipy.Spotify(auth=token)
		sp.trace = False

		playlists = sp.user_playlists(username)

		playlist = None

		# check if playlist with this name already exists
		for p in playlists['items']:
			if p['name'] == playlist_name:
				playlist = p
				print ('"{}" playlist found. Skipping creation of a new playlist'.format(playlist_name))
		
		# if not found - create new one
		if not playlist:
			print ('"{}" playlist not found. Creating new playlist'.format(playlist_name))
			playlist = sp.user_playlist_create(username, playlist_name)

		return playlist

	else:
		print ("Can't get token for {}".format(username))
		return None
	

def sp_add_tracks_to_playlist(username, playlist_id, track_ids):
	scope = 'playlist-modify-public'
	token = util.prompt_for_user_token(username,scope, client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET, redirect_uri = SPOTIPY_REDIRECT_URI)

	if token:
		sp = spotipy.Spotify(auth=token)
		sp.trace = False
		results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
		print results
	else:
		print ("Can't get the token for {}".format(username))

def sp_get_top_tracks(username, artist):

	top_tracks = []
	sp = spotipy.Spotify()
	request = sp.artist_top_tracks(artist)

	# print top_tracks
	for track in request['tracks']:
		# print track['uri']
		top_tracks.append(track['uri'])
		# print ('---------')
		# print ('{} yo'.format(track))

	return top_tracks


# ========================================================================
# DISCOGS methods
# ========================================================================

def do_get_masters(artist, masters):
	return [i for i in masters.find({'l_artist':request})]

def do_get_labels (artist, masters, releases):
	artist_masters = do_get_masters(artist, masters)
	artist_labels = {}
	for i in artist_masters:
		for j in releases.find({'title':i['title']}):
			for l in j['labels']:
				l_name = l['name']
				if l_name in artist_labels:
					artist_labels[l_name] += 1
				else:
					artist_labels[l_name] = 1
	return artist_labels


# ========================================================================
# ECHONEST METHODS
# ========================================================================
def en_get_artist_ids(discogs_id):
	en = pyen.Pyen(ECHONEST_API_KEY)
	r = 'discogs:artist:' + discogs_id
	b = 'id:spotify'
	
	spotify_id = None
	echonest_id = None
	response = None

	try:
		response = en.get('artist/profile', id=r, bucket=b)
		echonest_id = response['artist']['id']

		try:
			for f_id in response['artist']['foreign_ids']:	
				if f_id['catalog'] == 'spotify':
					spotify_id = f_id['foreign_id']

		except KeyError as err:
			# report_error(err)
			print ''

	except pyen.PyenException as err:
		# report_error(err)
		print ''

	return spotify_id, echonest_id

# ========================================================================
# other helper methods
# ========================================================================
def report_error(err):
	print ('*********************************')
	print ('an error occurred: {}'.format(err))
	print ('*********************************')


# ========================================================================
# MAIN
# ========================================================================

def main():

	# 
	# look up artist in the DISCOGS databse
	# 
	do_artist = DO_ARTISTS.find_one({"l_name":request})
	do_artist_id = do_artist['_id']
	
	print ('looking up "{}"'.format(do_artist['name']))
	print ('discogs id is: {}'.format( do_artist_id))

	# 
	# get the label on which the artist has released the most
	# 
	do_artist_labels = do_get_labels(do_artist, DO_MASTERS, DO_RELEASES)
	do_top_label = sorted(do_artist_labels.items(), key=operator.itemgetter(1))[-1][0]
	do_top_label = DO_LABELS.find_one({'name':do_top_label})
	
	print ('top label is: {}'.format(do_top_label['name']))

	# 
	# look up other artists on the same label and their discogs ID's
	# 

	label_mates = []
	do_label_releases = DO_RELEASES.find({'labels.name': do_top_label['name']})
	for lr in do_label_releases:
		
		for a in lr['artistJoins']:
			entry = {}
			if a['artist_name'].lower() is not 'various':
				entry['name'] = a['artist_name']
				entry['discogs_id'] = a['artist_id']
				if entry not in label_mates:
					print ('--------------------------')
					print ('{}'.format(lr['title']))
					# print entry
					label_mates.append(entry)


	# 
	# get the spotify id's for the artists
	# # 
	for lm in label_mates:
		print ("looking up id's for {}".format(lm['name']))
		lm['spotify_id'], lm['echonest_id'] = en_get_artist_ids(lm['discogs_id'])
		


	# # 
	# # create Spotify playlist
	# # 
	playlist_name = (do_top_label['name'] + ' catalog')
	playlist = sp_create_playlist(SP_USERNAME, playlist_name)


	# 
	# get top tracks for every artist
	# 
	top_tracks = []
	for mate in label_mates:
		print ('--------------------------')
		# mate = mate.split(':')[2]
		if mate['spotify_id']:
			t = sp_get_top_tracks(SP_USERNAME, mate['spotify_id'])
			[top_tracks.append(i) for i in t]
			print ('adding {}'.format(t))

	print ("======= TOP TRACKS ======")
	print top_tracks
 
 	# 
	# add tracks to the playlist
	# 

	sp_add_tracks_to_playlist(SP_USERNAME, playlist['id'], top_tracks[0:99])

	print ('added 100 tracks to the "{}" playlist'.format(playlist['name']))
	

if __name__ == '__main__':
	main()

