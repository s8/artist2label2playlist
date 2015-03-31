'''
TO DO:
- *  split into different files
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
'''

from spotify_api_client import *
from discogs_api_client import *
from echonest_api_client import *

import subprocess
import operator
import pprint
import sys
import os

# request = 'zazen boys'
# request = 'polysics'
# request = 'jaga jazzist'
# request = 'aphex twin'
# request = 'moving units'
# request = 'kyuss'
# request = 'queens of the stone age'
# request = 'aerosmith'
# request = 'nicki minaj'
# request = 'flanger'
request = 'burnt friedman & jaki liebezeit'
# request = 'bernd friedmann'
# request = 'lcd soundsystem'
# request = 'deerhoof'
# request = 'senor coconut'
# request = 'other side'
# request = 'la maison'
# request = 'tasaday'
# request = 'd.a.f.'
# request = 'electronicat'
# request = 'lkfjbeaga'

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
	artist = DISCOGS['artists'].find_one({"l_name":request.lower()})
	
	try:
		
		print ('"{}" has the following discogs id: {}'
			.format(artist['name'], artist['id']))

		# 
		# identify the label on which the artist has the most releases:
		# 
		labels = get_labels(artist['l_name'])
		top_label = sorted(labels.items(), key=operator.itemgetter(1))[-1][0]
		top_label = DISCOGS['labels'].find_one({'name':top_label})
		
		print ('top label is: {}'.format(top_label['name']))

		# 
		# look up other artists on the same label and their discogs ID's
		# 

		label_mates = []
		label_releases = DISCOGS['releases'].find({'labels.name': top_label['name']})
		for lr in label_releases:
			
			for a in lr['artistJoins']:
				entry = {}
				if a['artist_name'].lower() is not 'various':
					entry['name'] = a['artist_name']
					entry['discogs_id'] = a['artist_id']
					if entry not in label_mates:
						print ('--------------------------')
						# print ('{}'.format(lr['title']))
						print entry
						label_mates.append(entry)


		# 
		# get the spotify id's for the artists
		# # 
		for lm in label_mates:
			# print ("looking up id's for {}".format(lm['name']))
			lm['spotify_id'], lm['echonest_id'] = en_get_artist_ids(lm['discogs_id'])


		# # 
		# # create Spotify playlist
		# # 
		playlist_name = (top_label['name'] + ' catalog')
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
	except TypeError as err:
		print ('no artist named "{}" found'.format(request))

	

if __name__ == '__main__':
	main()

