# ========================================================================
# DSICOGS METHODS
# ========================================================================

from __future__ import unicode_literals


from pymongo import MongoClient

DO_CLIENT = MongoClient('localhost:27017')

DISCOGS = DO_CLIENT['discogs']

big_four_file = '../data/big_four.csv'

def get_labels (artist):
	# artist_masters = [i for i in DISCOGS['masters'].find({'l_artist':artist['l_name']})]
	artist_masters = [i for i in DISCOGS['masters'].find({'artists':artist['name']})]
	artist_labels = {}
	for i in artist_masters:
		for j in DISCOGS['releases'].find({'master_id':i['id']}):
			for l in j['labels']:
				l_name = l['name']
				if l_name in artist_labels:
					artist_labels[l_name] += 1
				else:
					artist_labels[l_name] = 1
	return artist_labels

def get_sony_labels():
	sony_labels = []
	for l in DISCOGS['labels'].find():
		if ('sony' in l['l_name']) or ('sony' in l['parentLabel']):
			sony_labels.append(l['l_name'])
			if len(l['sublabels']) > 0:
				[sony_labels.append(sl) for sl in l['sublabels']]
	return list(set(sony_labels))

def get_warner_labels():
	warner_labels = []
	for l in DISCOGS['labels'].find():
		if ('warner' in l['l_name']) or ('warner' in l['parentLabel']):
			warner_labels.append(l['l_name'])
			if len(l['sublabels']) > 0:
				[warner_labels.append(sl) for sl in l['sublabels']]
	return list(set(warner_labels))

def get_universal_labels():
	universal_labels = []
	for l in DISCOGS['labels'].find():
		if ('universal' in l['l_name']) or ('universal' in l['parentLabel']):
			warner_labels.append(l['l_name'])
			if len(l['sublabels']) > 0:
				[universal_labels.append(sl) for sl in l['sublabels']]
	return list(set(universal_labels))

def update_big_four(bf_file, *args):
	''' 
	if big_four file exists - wipe it clean
	create new big_four file
	write all arrays passed to it as a csv file
	'''
	with open(bf_file, 'w') as bf:
		for a in args:
			for line in a:
				try:
  					bf.write("%s\n" % line)
  				except UnicodeEncodeError:
  					# print line
  					continue




if __name__ == '__main__':

	# print (DISCOGS['masters'].find_one({'l_artist':'zzz'}))
	# zzz_releases = DISCOGS['masters'].find({'artists':'zZz'})

	# for r in zzz_releases:
	# 	print (r)


	# artist_masters = [i for i in DISCOGS['masters'].find({'l_artist':artist['l_name']})]
	artist_masters = [i for i in DISCOGS['masters'].find({'artists':'zZz'})]
	# print artist_masters
	artist_labels = {}
	for i in artist_masters:
		for j in DISCOGS['releases'].find({'master_id':i['id']}):
			print('---------')
			print j['labels']
	# 		for l in j['labels']:
	# 			l_name = l['name']
	# 			if l_name in artist_labels:
	# 				artist_labels[l_name] += 1
	# 			else:
	# 				artist_labels[l_name] = 1
	# return artist_labels



	# ============================
	# UPDATE THE BIG FOUR CATALOG
	# ============================
	# sony_labels = get_sony_labels()
	# warner_labels = get_warner_labels()
	# universal_labels = get_universal_labels()
	# update_big_four(big_four_file, sony_labels,warner_labels, universal_labels)

	# print ('********************************************************')
	# print ('********************************************************')
	# print ('********************************************************')
	# print ("Sony has {} sublabels".format(len(sony_labels)))
	# # print (sony_labels)
	# for l in sony_labels:
	# 	try:
	# 		print (l.decode('utf-8'))
	# 	except UnicodeEncodeError as err:
	# 		print ('*** unicode error ***')

	# print ('********************************************************')
	# print ('********************************************************')
	# print ('********************************************************')
	# warner_labels = get_warner_labels()
	# print ("Warner has {} sublabels".format(len(warner_labels)))
	# print (warner_labels)
	# # for l in warner_labels:
	# # 	try:
	# # 		print (l)
	# # 	except UnicodeEncodeError as err:
	# # 		print ('*** unicode error ***')
