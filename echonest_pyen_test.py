import pyen

from music_apis_keys import ECHONEST_API_KEY
from music_apis_keys import ECHONEST_CONSUMER_KEY
from music_apis_keys import ECHONEST_SHARED_SECRET

en = pyen.Pyen(ECHONEST_API_KEY)

request = 'zazen boys'
# request = 'polysics'
# request = 'jaga jazzist'
# request = 'aphex twin'
# request = 'moving units'
# request = 'kyuss'
# request = 'queens of the stone age'
# request = 'aerosmith'
# request = 'nicki minaj'
# request = 'flanger'

# request = 'burnt friedman & jaki liebezeit'
# request = 'bernd friedmann'
# request = 'lcd soundsystem'

def print_similar_artists(r):
	response = en.get('artist/similar', name=r)

	for artist in response['artists']:
		try:
			print ('name: {}, id: {}'.format(artist['name'],artist['id']))
		except UnicodeEncodeError as err:
			print ('unicode error: {}'.format(err))


def print_playlist_form_artist(r):
	response = en.get('playlist/static', artist = r, type = 'artist-radio')

	for i, song in enumerate(response['songs']):
		try:
			print ("%d %-32.32s %s" % (i, song['artist_name'], song['title']))
		except UnicodeEncodeError as err:
			print ('unicode error: {}'.format(err))

def en_get_spotidy_id(discogs_id):
	r = 'discogs:artist:' + discogs_id
	response = en.get('artist/profile', id=r)

	return response['artist']['id']


# def print_blog_references(r):

# print_similar_artists(request)
# print_playlist_form_artist(request)

# {u'status': {u'code': 0, u'message': u'Success', u'version': u'4.2'}, u'artist': {u'id': u'AR3Q48J1187FB55278', u'name': u'The Rapture'}}
# {'discogs_id': u'9985', 'echonest_id': u'AR3Q48J1187FB55278', 'name': u'Rapture, The'}
s_id = en_get_spotidy_id('9985')
print (s_id)



