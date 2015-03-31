# ========================================================================
# ECHONEST METHODS
# ========================================================================

import pyen

from music_apis_keys import ECHONEST_API_KEY
from music_apis_keys import ECHONEST_CONSUMER_KEY
from music_apis_keys import ECHONEST_SHARED_SECRET


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