import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as utills

cid 		= '2dbb1a45a22249aea988931d9d8bc0c6' 
secret 		= '6c90bbf62d8d467fb280f54b4dae7211'
username 	= 'sparlund'
scope 		= 'user-library-read playlist-read-private user-read-currently-playing user-read-playback-state playlist-modify-public playlist-modify-private'
redir_uri 	= 'http://localhost/'
token 		= util.prompt_for_user_token(username,scope,client_id=cid,client_secret=secret,redirect_uri='http://localhost/')
sp 			= spotipy.Spotify(auth=token)



r = requests.get('http://www.radiotreby.se/')
s = BeautifulSoup(r.content, 'html.parser')
senasts_spelat = s.find("span", id="playlist")
song_list = senasts_spelat.text.split('\n')
# Delete last item, it'll just be an empty entry.
song_list.pop()
song_list = [a[6:] for a in song_list]

songs = list()
for song in song_list:
	artist,song_name = song.split('-')
	artist = artist.rstrip(' ').strip(' ')	
	song_name = song_name.rstrip(' ')
	songs.append({'artist': artist, 'song': song_name})

# See which songs already are in the list:
#radio_treby_list = sp.user_playlists(user, limit=50, offset=0)
list_uri = 'spotify:user:sparlund:playlist:2edTLPX9eFi1a9Dgr8EqW0'
# Want to see which songs are already in the list so that we don't add duplicates
radio_treby_list = sp.user_playlist(username, playlist_id = list_uri, fields=['tracks'])
tracks_in_radio_treby_list = list()
for track in radio_treby_list['tracks']['items']: 
	tracks_in_radio_treby_list.append(track['track']['uri'])
tracks_in_radio_treby_list = set(tracks_in_radio_treby_list)
#sp.user_playlist_create(username, 'Radio Treby', public=True, description='')
# Want to search for the songs we scraped for and add to the playlist:
for j,song in enumerate(songs):
	if ',' in song['artist']:
		artist_search_string = ''
		for counter,individual_artist in enumerate(song['artist'].split(',')):
			artist_search_string = artist_search_string +  '\"'+individual_artist+'\"'
			if counter % 2 != 0:
				artist_search_string = artist_search_string + ' AND'
	else:
		artist_search_string = '\"'+song['artist']+'\"'		


	search_string = 'artist:' + artist_search_string + ' track:' + '\"'+song['song']+'\"'
	results = sp.search(q=search_string, type='track',limit=1)
	print(search_string)
	# Check if a song is found:
	if results['tracks']['items']:
		# Save the track's id
		track_id = results['tracks']['items'][0]['uri']	
		if track_id not in tracks_in_radio_treby_list:
			print('track added: '+track_id)
			sp.user_playlist_add_tracks(username,list_uri,[track_id],position=None)
		else:
			print('track not added bc already in list')
	else:
		print('track not found')	
			
	


