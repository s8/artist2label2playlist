# ========================================================================
# SPOTIFY methods
# ========================================================================

import spotipy
import spotipy.util as util

from music_apis_keys import SPOTIFY_CLIENT_ID as SPOTIPY_CLIENT_ID
from music_apis_keys import SPOTIFY_CLIENT_SECRET as SPOTIPY_CLIENT_SECRET
from music_apis_keys import SPOTIFY_REDIRECT_URI as SPOTIPY_REDIRECT_URI

SP_USERNAME = 's8'

def sp_create_playlist(username, playlist_name):

	scope = 'playlist-modify-public'
	token = util.prompt_for_user_token(username,scope, 
		client_id = SPOTIPY_CLIENT_ID, 
		client_secret = SPOTIPY_CLIENT_SECRET, 
		redirect_uri = SPOTIPY_REDIRECT_URI)

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
	token = util.prompt_for_user_token(username,scope, 
		client_id = SPOTIPY_CLIENT_ID, 
		client_secret = SPOTIPY_CLIENT_SECRET, 
		redirect_uri = SPOTIPY_REDIRECT_URI)

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

	return top_tracks
