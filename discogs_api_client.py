# ========================================================================
# DSICOGS METHODS
# ========================================================================

from pymongo import MongoClient

DO_CLIENT = MongoClient('localhost:27017')

DISCOGS = DO_CLIENT['discogs']

def get_labels (artist):
	artist_masters = [i for i in DISCOGS['masters'].find({'l_artist':artist})]
	artist_labels = {}
	for i in artist_masters:
		for j in DISCOGS['releases'].find({'title':i['title']}):
			for l in j['labels']:
				l_name = l['name']
				if l_name in artist_labels:
					artist_labels[l_name] += 1
				else:
					artist_labels[l_name] = 1
	return artist_labels
