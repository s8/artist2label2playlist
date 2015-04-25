import discogs_client

from music_apis_keys import DISCOGS_CONSUMER_KEY
from music_apis_keys import DISCOGS_CONSUMER_SECRET
from music_apis_keys import DISCOGS_TOKEN

d = discogs_client.Client('ExampleApplication/0.1')

d.set_consumer_key(DISCOGS_CONSUMER_KEY, DISCOGS_CONSUMER_SECRET)
auth_url = d.get_authorize_url()
print auth_url