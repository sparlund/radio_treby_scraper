import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

cid 		= '2dbb1a45a22249aea988931d9d8bc0c6' 
secret 		= ''
username 	= 'sparlund'
scope 		= 'user-library-read playlist-read-private user-read-currently-playing user-read-playback-state playlist-modify-public playlist-modify-private'
redir_uri 	= 'http://localhost/'
token 		= util.prompt_for_user_token(username,scope,client_id=cid,client_secret=secret,redirect_uri='http://localhost/')
sp 			= spotipy.Spotify(auth=token)


# Website to crawl songs from
r = requests.get('http://www.radiotreby.se/')
s = BeautifulSoup(r.content, 'html.parser') 
# This is the box where the latest played songs are found
senasts_spelat = s.find("span", id="playlist")
# Do some text manipulations to extract song names and artist
song_list = senasts_spelat.text.split('\n')
song_list.pop()
song_list = [a[6:] for a in song_list] # Remove time stamp!
songs = list()
for song in song_list:
	# Split to artist and song
	artist,song_name = song.split('-')
	# Remove whitespace characters
	artist = artist.rstrip(' ').strip(' ')	
	song_name = song_name.rstrip(' ').strip(' ')
	songs.append({'artist': artist, 'song': song_name})

# Check if a playlist called "Radio Treby" already exists
# If it exists, we just need to find the id of it.
# Other we need to create a playlist.
sp_playlist_info = sp.user_playlists(username, limit=50, offset=0)
playlists = sp_playlist_info['items']
for counter,list_name in enumerate(playlists):
	if list_name == 'Radio Treby':
		list_uri = playlists['items'][counter]['id']
		break
	if counter+1 == len(playlists):
		created_playlist = sp.user_playlist_create(username, 'Radio Treby', public=True, description='')
		list_uri = created_playlist['uri']	
# Want to see which songs are already in the list so that we don't add duplicates
songs_in_playlist = sp.user_playlist(username, playlist_id = list_uri, fields=['tracks'])
tracks_2_add = list()
for track in songs_in_playlist['tracks']['items']: 
	tracks_2_add.append(track['track']['uri'])
# Want to search for the songs we scraped for and add to the playlist:
for j,song in enumerate(songs):
	# Create the search string
	if ',' in song['artist']:
		artist_search_string = ''
		for counter,individual_artist in enumerate(song['artist'].split(',')):
			artist_search_string = artist_search_string +  '\"'+individual_artist+'\"'
			if counter % 2 != 0:
				artist_search_string = artist_search_string + ' AND'
	else:
		artist_search_string = '\"'+song['artist']+'\"'		

	search_string = 'artist:' + artist_search_string + ' track:' + '\"'+song['song']+'\"'
	# Perform search
	results = sp.search(q=search_string, type='track',limit=1)
	# Check if a song is found:
	if results['tracks']['items']:
		# Save the track's id
		track_id = results['tracks']['items'][0]['uri']	
		if track_id not in tracks_2_add:
			sp.user_playlist_add_tracks(username,list_uri,[track_id],position=None)
		else:
			print('track not added bc already in list')
	else:
		print('track not found')	
			
	


