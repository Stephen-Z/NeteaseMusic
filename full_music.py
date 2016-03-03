from flask import Flask,request,jsonify
import json, requests, hashlib, random
from urllib import quote

app = Flask(__name__)

ORIGIN_PLAY_URL_JSON={}

def encrypted_id(id):
	magic = bytearray('3go8&$8*3*3h0k(2)2')
	song_id = bytearray(id)
	magic_len = len(magic)
	for i in xrange(len(song_id)):
		song_id[i] = song_id[i] ^ magic[i % magic_len]
	m = hashlib.md5(song_id)
	result = m.digest().encode('base64')[:-1]
	result = result.replace('/', '_')
	result = result.replace('+', '-')
	return result

@app.route("/eapi/song/enhance/player/url", methods=['GET','POST'])
def get_song_api():
	global ORIGIN_PLAY_URL_JSON
	if (not 'ids' in request.args):
		return get_ios_response()
	origin_result = requests.post('http://music.163.com/eapi/song/enhance/player/url?br=' + quote(request.args['br']) + '&ids=' + quote(request.args['ids']), data={'params':request.form['params']}, headers={'Cookie':request.headers['Cookie']})
	origin_result_json = json.loads(origin_result.content)
	ORIGIN_PLAY_URL_JSON=origin_result_json
	#if (origin_result_json['data'][0]['url'] != None):
		#print('Returning origin result')
	#print origin_result_json
		#return origin_result.text
	song_id = json.loads(request.args['ids'])[0]
	song_id = song_id[0:song_id.find('_')]
	request_result = requests.get('http://music.163.com/api/song/detail/?ids=' + quote('["' + song_id + '"]') + '&id=' + song_id)
	result_json = request_result.json()
	#print result_json
	if (result_json['songs'][0]['hMusic']['dfsId'] == None):
		song_res_id = str(result_json['songs'][0]['bMusic']['dfsId'])
		mp3_url = "http://m%s.music.126.net/%s/%s.mp3" % (random.randrange(1, 3), encrypted_id(song_res_id), song_res_id)
		print('Returning new result')
		return jsonify({
			'code' : 200,
			'data' : [
				{
					'id' : song_id,
					'url': mp3_url,
					'br' : 64000,
					'size':result_json['songs'][0]['bMusic']['size'],
					'md5' : None,
					'code': 200,
					'expi':1200,
					'type':'mp3',
					'gain':0,
					'fee':0,
					'canExtend':False
				}
			]	
		})
	else:
		song_res_id = str(result_json['songs'][0]['hMusic']['dfsId'])
		mp3_url = "http://m%s.music.126.net/%s/%s.mp3" % (random.randrange(1, 3), encrypted_id(song_res_id), song_res_id)
		print('Returning new result(hMusic)')
		#print mp3_url
		#print result_json['songs'][0]['hMusic']['size']
		return jsonify({
			'code' : 200,
			'data' : [
				{
					'id' : song_id,
					'url': mp3_url,
					'br' : result_json['songs'][0]['hMusic']['bitrate'],
					'size':result_json['songs'][0]['hMusic']['size'],
					'md5' : None,
					'code': 200,
					'expi':1200,
					'type':'mp3',
					'gain':0,
					'fee':0,
					'canExtend':False
				}
			]	
		})

def get_ios_response():
	print 'get_ios_response running'
	origin_result = requests.post('http://music.163.com/eapi/song/enhance/player/url', data={'params':request.form['params']},headers={'Cookie':request.headers['Cookie']})
	origin_result_json = json.loads(origin_result.content)
	#if (origin_result_json['data'][0]['url'] != None):
		#print('Returning origin result')
		#print 'origin result:' ,origin_result_json
		#return origin_result.text
	song_id = str(origin_result_json['data'][0]['id'])
	request_result = requests.get('http://music.163.com/api/song/detail/?ids=' + quote('["' + song_id + '"]') + '&id=' + song_id)
	result_json = request_result.json()
	if (result_json['songs'][0].has_key('hMusic')):
		song_res_id = str(result_json['songs'][0]['hMusic']['dfsId'])
		mp3_url = "http://m%s.music.126.net/%s/%s.mp3" % (random.randrange(1, 3), encrypted_id(song_res_id), song_res_id)
		print('Returning new hMusic result')
		return jsonify({
			'code' : 200,
			'data' : [
				{
					'id' : song_id,
					'url': mp3_url,
					'br' : result_json['songs'][0]['hMusic']['bitrate'],
					'size':result_json['songs'][0]['hMusic']['size'],
					'md5' : None,
					'code': 200,
					'expi':1200,
					'type':'mp3',
					'gain':0,
					'fee':0,
					'canExtend':False
				}
			]	
		})
	else:
		song_res_id = str(result_json['songs'][0]['bMusic']['dfsId'])
		mp3_url = "http://m%s.music.126.net/%s/%s.mp3" % (random.randrange(1, 3), encrypted_id(song_res_id), song_res_id)
		print('Returning new result')
		#print mp3_url
		#print result_json['songs'][0]['hMusic']['size']
		return jsonify({
			'code' : 200,
			'data' : [
				{
					'id' : song_id,
					'url': mp3_url,
					'br' : result_json['songs'][0]['bMusic']['bitrate'],
					'size':result_json['songs'][0]['bMusic']['size'],
					'md5' : None,
					'code': 200,
					'expi':1200,
					'type':'mp3',
					'gain':0,
					'fee':0,
					'canExtend':False
				}
			]	
		})


@app.route("/eapi/song/enhance/download/url", methods=['GET','POST'])
def get_download_url():
	origin_result = requests.post('http://music.163.com/eapi/song/enhance/download/url',data={'params':request.form['params']})
	origin_content_json=json.loads(origin_result.content)
	songs_id=origin_content_json['data']['id']
	song_id=str(songs_id)
	print 'song_id: '+str(songs_id)

	request_result = requests.get('http://music.163.com/api/song/detail/?ids=' + quote('["' + song_id + '"]') + '&id=' + song_id)
	request_result_json=request_result.json()
	if request_result_json['songs'][0].has_key('hMusic'):
		song_res_id = str(request_result_json['songs'][0]['hMusic']['dfsId'])
		play_url = "http://m%s.music.126.net/%s/%s.mp3" % (random.randrange(1, 3), encrypted_id(song_res_id), song_res_id)
		play_br=request_result_json['songs'][0]['hMusic']['bitrate']
		play_size=request_result_json['songs'][0]['hMusic']['size']
	else:
		song_res_id = str(request_result_json['songs'][0]['bMusic']['dfsId'])
		play_url = "http://m%s.music.126.net/%s/%s.mp3" % (random.randrange(1, 3), encrypted_id(song_res_id), song_res_id)
		play_br=request_result_json['songs'][0]['bMusic']['bitrate']
		play_size=request_result_json['songs'][0]['bMusic']['size']		
	print play_url
	print play_br
	print play_size

	dwn_data='{"data":{"id":'+ str(songs_id) +',"url":"'+ play_url +'","br":'+ str(play_br) +',"size":'+ str(play_size) +',"md5":"None","code":200,"expi":1200,"type":"mp3","gain":0.0922,"fee":0,"uf":null,"payed":0,"canExtend":false},"code":200}'
	print 'returning joint download result'
	return dwn_data













if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5001)
