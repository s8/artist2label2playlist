'''
TO DO:
- * split into different files
- * BIG FOUR label sorter

- * make spotify playlists longer than 100 records

- refactor Echonest api requests !!!

- check for duplicate tracks in the playlist before adding
- transition discogs stuff from the local database to the cloud api
- store complete label records, not just their names
- resolve unicode errors
- refactor authorizations into a separate method
- optimize api requests
	- discogs
	- echonest
	- spotify
		- before adding - check if songs are already in the playlist
- set api lookup timeouts
- transition to original discogs database
- make web interface
- deploy on google app engine
- search artist's masters by ID instead of l_name
- label playlist caching
'''

'''
BIG FOUR issues
!!! not on the list !!! :
	Geffen Records not on the list
	CBS not on the list
	A&M not on the list
	Tamla Motown
	Jive
	Mute
	Young Money Entertainment
	Republic Records
warner
	Warner Music Japan
	Warner Music Sweden
sony
	Sony Music House Inc.
	Sony Music
	Sony BMG Music Entertainment
universal
	Universal Licensing Music (ULM)
	Universal Records
	Universal
emi
bmi
virgin
'''

from spotify_api_client import *
from discogs_api_client import *
from echonest_api_client import *

import subprocess
import operator
import pprint
import csv
import sys
import os


# request = 'lafayette afro rock band'
# request = 'zazen boys' # no associated labels on discogs
# request = 'polysics'
# request = 'pizzicato five'
# request = 'brian eno'
# request = 'jaga jazzist'
# request = 'aphex twin'
# request = 'moving units'
# request = 'krafty kuts'
# request = 'kyuss' # spotipy.client.SpotifyException: http status: 400, code:-1 - https://api.spotify.com/v1/users/s8/playlists/1EpyLg6gZfIYa7NVWIEeGM/tracks:
# request = 'queens of the stone age'
# request = 'aerosmith'
# request = 'nicki minaj'
# request = 'flanger'
# request = 'burnt friedman & jaki liebezeit'
# request = 'bernd friedmann' # found, but no playlist created
# request = 'burnt friedman' # artist not found????
# request = 'lcd soundsystem'
request = 'deerhoof'
# request = 'senor coconut'
# request = 'other side'
# request = 'la maison'
# request = 'tasaday'
# request = 'd.a.f.'
# request = 'electronicat'
# request = 'zzz'
# request = 'lkfjbeaga'



# ========================================================================
# MAIN
# ========================================================================

def main():

	bootleg_labels = ['Star Mark', 'Not On Label']

	# ---------------------------------------------------
	# load the big four file
	# ---------------------------------------------------
	with open(big_four_file, 'r') as bf:
		big_four = bf.read().splitlines() 

	# ---------------------------------------------------
	# look up artist in the DISCOGS databse
	# ---------------------------------------------------
	artist = DISCOGS['artists'].find_one({"l_name":request.lower()})
	try:
		print ('"{}" has the following discogs id: {}'
			.format(artist['name'], artist['id']))
	except TypeError as err:
		print ('no artist named "{}" found on discogs'.format(request))
		return

	# ---------------------------------------------------
	# make a sorted list of labels where the artist has had releases
	# ---------------------------------------------------

	labels = sorted(get_labels(artist).items(), 
		key=operator.itemgetter(1), reverse=True)

	if len(labels) == 0:
		print('no associated labels found')
		return

	print ('"{}" has had releases on the following labels: {}'.
		format(artist['name'],[l[0].encode('utf-8') for l in labels]))

	# ---------------------------------------------------
	# identify top label not in big four
	# ---------------------------------------------------

	top_label = None

	for l in labels:
		if l[0] in big_four:
			print ('{} is part of big four'.format(l[0]))
		elif l[0] in bootleg_labels:
			print ('{} is a bootleg label'.format(l[0]))
		else:
			top_label = DISCOGS['labels'].find_one({'name':l[0]})
			break

	if top_label:
		print ('')
		print ('>>> top independent label is: "{}" <<<'.format(top_label['name']))
	else:
		print ('no independent labels found')
		return

	# ---------------------------------------------------
	# look up other artists on the same label and their discogs ID's
	# ---------------------------------------------------

	label_mates = []
	label_releases = DISCOGS['releases'].find({'labels.name': top_label['name']})

	label_release_counter = 0
	for lr in label_releases:
		label_release_counter += 1
		for a in lr['artistJoins']:
			entry = {}
			if a['artist_name'].lower() is not 'various':
				entry['name'] = a['artist_name']
				entry['discogs_id'] = a['artist_id']
				if entry not in label_mates:
					# print ('--------------------------')
					# print ('{}'.format(lr['title']))
					# print entry
					label_mates.append(entry)

	print ('{} total releases on "{}"'
		.format(label_release_counter,top_label['name']))

	print ('"{}"" has {} label mates on "{}"'
		.format(artist['name'],len(label_mates
			),top_label['name']))


	# ---------------------------------------------------
	# get the spotify id's for the artists
	# ---------------------------------------------------
	for i, lm in enumerate(label_mates):
		# print ("looking up id's for {}".format(lm['name']))
		print ('looking up ids...{}'.format(i))
		lm['spotify_id'], lm['echonest_id'] = en_get_artist_ids(lm['discogs_id'])


	# ---------------------------------------------------
	# create Spotify playlist
	# ---------------------------------------------------
	playlist_name = (top_label['name'] + ' catalog')
	playlist = sp_create_playlist(SP_USERNAME, playlist_name)


	# ---------------------------------------------------
	# get top tracks for every artist
	# ---------------------------------------------------
	top_tracks = []
	for mate in label_mates:
		print ('--------------------------')
		# mate = mate.split(':')[2]
		if mate['spotify_id']:
			t = sp_get_top_tracks(SP_USERNAME, mate['spotify_id'])
			[top_tracks.append(i) for i in t]
			print ('adding {}'.format(t))

 	# ---------------------------------------------------
	# add tracks to the playlist
	# ---------------------------------------------------

	sp_add_tracks_to_playlist(SP_USERNAME, playlist['id'], top_tracks)

	print ('added {} tracks to the "{}" playlist'.format(len(top_tracks),playlist['name']))


if __name__ == '__main__':
	main()

