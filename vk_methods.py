import os
import requests
import json
import pickle
import time
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import vk_audio
from utils import *

REGEXP = {
    'ascii': re.compile(r'&#([0-9]+);'),
    'section_id': re.compile(r'"sectionId":"(.*?)",'),
    'data_next': re.compile(r"data-next='(.*?)'"),
    'next_from': re.compile(r'"nextFrom":"(.*?)",'),
    'block_id': re.compile(r'"blockId":"(.*?)",'),
    'playlist_owner_id': re.compile(r'<title>(.*?)</title>'),
    'u_img_name': re.compile(r'<img class="TopNavBtn__profileImg" src="(.*?)" />'),
    'uid': re.compile(r'id: ([0-9]+),'),
    'to': re.compile(r'"to":"(.*?)"'),
    'ip_h': re.compile(r'name="ip_h" value="([a-z0-9]+)"'),
    'lg_h': re.compile(r'name="lg_h" value="([a-z0-9]+)"'),
    'lg_domain_h': re.compile(r'name="lg_domain_h" value="([a-z0-9]+)"'),
    'auth_hash': re.compile(r"Authcheck\.init\('([a-z_0-9]+)'"),
    'captcha_sid': re.compile(r"onLoginCaptcha\('(\d+)'"),
    'number_hash': re.compile(r"al_page: '3', hash: '([a-z0-9]+)'"),
    'phone_postfix': re.compile(r'phone_postfix">.*?(\d+).*?<'),
    'phone_prefix': re.compile(r'label ta_r">\+(.*?)<')
    }

def search_re(reg, string):
    s = reg.search(string)
    if s:
        groups = s.groups()
        return groups[0]
    
def clear_string(s):
    if s:
        return s.strip().replace('&nbsp;', '')

def load_session(s):    
    session = requests.Session()
    session.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    if not s:
        return session
    try:
        with open(rf'./sessions/{s}/coockie_Jar', 'rb') as f:
            session.cookies.update(pickle.load(f))
            
    except FileNotFoundError:
        print('No valid session file')
    
    return session

def save_session(session):# Save session
    response = session.get('https://vk.com/settings')

    u_img_url, u_name= search_re(REGEXP['u_img_name'], response.text).split('" alt="')
    uid = search_re(REGEXP['uid'], response.text)
    os.mkdir(f'./sessions/vk_{uid}/')
    with open(rf'./sessions/vk_{uid}/coockie_Jar', 'wb') as f:
        pickle.dump(session.cookies, f)
        
    with open(rf'./sessions/vk_{uid}/u_img.jpg', 'wb') as f:
        f.write(session.get(u_img_url).content)
        
    with open(rf'./sessions/vk_{uid}/uid', 'wb') as f:
        pickle.dump({'uid': uid, 'u_name': u_name}, f)
    
def login_request(login, password, session_name = '', captcha_sid='', captcha_key = ''):
    session = load_session(session_name)
    response = session.get('https://vk.com/login')

    if response.status_code > 299: # Check if request status code is redirect
        if 400 > response.status_code:
            response = session.get('https://vk.com/settings')
            uid = search_re(REGEXP['uid'], response.text)
            return (session, None, 'Logged in')
        else:
            return (None, None, 'Could not connect')

    if (not login) or (not password):
        return (None, None, 'Fields should not be empty')
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://vk.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://vk.com',
    }
    payload = {
        'act': 'login',
        'role': 'al_frame',
        'expire': '',
        'to': search_re(REGEXP['to'], response.text),
        'recaptcha': '',
        'captcha_sid': captcha_sid,
        'captcha_key': captcha_key,
        '_origin': 'https://vk.com',
        'utf8': '1',
        'ip_h': search_re(REGEXP['ip_h'], response.text),
        'lg_h': search_re(REGEXP['lg_h'], response.text),
        'lg_domain_h': search_re(REGEXP['lg_domain_h'], response.text),
        'ul': '',
        'email': login,
        'pass': password
        }
            
    response = session.post('https://login.vk.com/?act=login',data=payload, headers=headers)

    if 'onLoginCaptcha(' in response.text: # captcha case
        captcha_sid = search_re(REGEXP['captcha_sid'], response.text)
        return (session, captcha_sid, 'Captcha needed', None)

    elif 'onLoginFailed(4' in response.text: # incorrect password case
        return (None, None, 'Wrong password', None)
        

    elif 'act=authcheck' in response.text: # 2FA case
        response = session.get('https://vk.com/login?act=authcheck')
        auth_hash = search_re(REGEXP['auth_hash'], response.text)
        if not auth_hash:
            return (None, None, 'Unknow error', None)
        
        return (session, None, 'Secure code', auth_hash)
    
    else: # Something else went wrong
        return (None, None, 'Unknow error', None)

                              
# 2FA case
def two_fa(session, code, auth_hash = '', captcha_sid='', captcha_key=''):  
    payload = {
            'al': '1',
            'code': code,
            'hash': auth_hash,
            'remember': 1,
    }
    if captcha_sid and captcha_key:
        payload['captcha_sid'] = captcha_sid
        payload['captcha_key'] = captcha_key

    response = session.post('https://vk.com/al_login.php?act=a_authcheck_code', payload)
    response_json = json.loads(response.text.lstrip('<!--'))
    status = response_json['payload'][0]
    
    if status == '4':  # OK
        path = json.loads(response_json['payload'][1][0])
        session.get(path)
        return (session, None, 'Logged in')
    
    elif status in [0, '8']:  # Incorrect code case
        return (None, None, 'Secure code')
    
    elif status == '2' and data['payload'][1][1] != 2: # Captcha case
        captcha_sid = data['payload'][1][0][1:-1]
        return (session, captcha_sid, 'Captcha needed')
     
    else: # Something else went wrong
        return (session, None, 'Unknow error')

    
def pass_security_check(session, login):
    response = session.get('https://vk.com/settings')

    if 'security_check' not in response.url: # Security check case 
        return True

    phone_prefix = clear_string(search_re(REGEXP['phone_prefix'], response.text))
    phone_postfix = clear_string(search_re(REGEXP['phone_postfix'], response.text))

    code = None
    if login and phone_prefix and phone_postfix:
        code = code_from_number(phone_prefix, phone_postfix, login)

    if code:
        number_hash = search_re(REGEXP['number_hash'], response.text)
        values = {
            'act': 'security_check',
            'al': '1',
            'al_page': '3',
            'code': code,
            'hash': number_hash,
            'to': ''
        }

        response = session.post('https://vk.com/login.php', values)

        if response.text.split('<!>')[4] == '4':
            return True
        else:
            return False
        

    
def code_from_number(prefix, postfix, number):
    prefix_len = len(prefix)
    postfix_len = len(postfix)

    if number[0] == '+':
        number = number[1:]

    if (prefix_len + postfix_len) >= len(number):
        return

    # Сравниваем начало номера
    if number[:prefix_len] != prefix:
        return

    # Сравниваем конец номера
    if number[-postfix_len:] != postfix:
        return

    return number[prefix_len:-postfix_len]

# Captcha case        
def captcha(session=requests.Session(), sid='123'):
    captcha_img_link = f'https://api.vk.com/captcha.php?sid={sid}'
    with open('captcha.jpg', 'wb') as f:
        f.write(session.get(captcha_img_link).content)

def parse_audio_list(data):
    audio_list = {}
    for elem in data:
        if elem[12] == '[]': # Is it blocked
            h = elem[13].split('/')
            audio_id = elem[15]['content_id'] + '_' + h[2] + '_' + h[5]
            artist = valid_file_name(elem[4])
            song = valid_file_name(elem[3])
            audio_list[f'{audio_id}'] = {
                'song': convert_ASCII(song),
                'artist': convert_ASCII(artist),
                'img_link': elem[14].split(',')[0]}
    return audio_list
            
def load_user_audios(session, uid):
    audio_list = {}
    url = f'https://vk.com/audios{uid}?section=all'
    response = session.get(url)
    
    section_id = search_re(REGEXP['section_id'], response.text)
    
    url = 'https://vk.com/audio?act=load_catalog_section'
    payload = {
        'al': '1',
        'section_id': section_id
    }
    response = session.post(url, data=payload)
    next_from = search_re(REGEXP['next_from'], response.text)
    response_json = json.loads(response.text.lstrip('<!--'))
    audio_list.update(parse_audio_list(response_json['payload'][1][1]['playlist']['list']))


    url = 'https://vk.com/al_audio.php?act=load_catalog_section'
    payload['start_from'] = next_from
    response = session.post(url, data=payload)
    next_from = search_re(REGEXP['next_from'], response.text)
    response_json = json.loads(response.text.lstrip('<!--'))
    audio_list.update(parse_audio_list(response_json['payload'][1][1]['playlist']['list']))
    
    payload['section_id'] = next_from.split(' ')[1]
    payload['start_from'] = next_from
    response = session.post(url, data=payload)
    next_from = search_re(REGEXP['next_from'], response.text)
    response_json = json.loads(response.text.lstrip('<!--'))
    audio_list.update(parse_audio_list(response_json['payload'][1][1]['playlist']['list']))
    
    return (audio_list, next_from, payload['section_id'])

def load_more(session, next_from, section_id):
    url = 'https://vk.com/al_audio.php?act=load_catalog_section'
    payload = {
        'al': '1',
        'section_id': section_id,
        'start_from': next_from
    }
    response = session.post(url, data=payload)
    next_from = search_re(REGEXP['next_from'], response.text)
    response_json = json.loads(response.text.lstrip('<!--'))
    audio_list = parse_audio_list(response_json['payload'][1][1]['playlist']['list'])
    return (audio_list, next_from, section_id)
    
def load_playlists(session, uid):
    album_list = {}
    url = f'https://vk.com/audios{uid}?block=my_playlists&section=all'
    response = session.get(url)
    section_id = search_re(REGEXP['section_id'], response.text)
    url = 'https://vk.com/audio?act=load_catalog_section'
    payload = {
        'al': '1',
        'section_id': section_id
    }
    response = session.post(url, data=payload)

    response_json = json.loads(response.text.lstrip('<!--'))
    start_from = search_re(REGEXP['data_next'], response_json['payload'][1][0][0])
    playlists = response_json['payload'][1][1]['playlists']
    while True: 
        for playlist in playlists:
            if playlist['permissions']['play']:
                playlist_name = valid_file_name(playlist['title']) + ' - ' + valid_file_name(playlist['authorName'])
                e = {'playlist_name': convert_ASCII(playlist_name),'img_link': playlist['coverUrl']}
                playlist_id = str(playlist['ownerId'])+'_'+str(playlist['id'])
                album_list[playlist_id] = e
            
        if start_from:
            url = 'https://vk.com/al_audio.php?act=load_catalog_section'
            payload = {
                'al': '1',
                'section_id': section_id,
                'start_from': start_from
            }
            response = session.post(url, data=payload)
            response_json = json.loads(response.text.lstrip('<!--'))
            start_from = search_re(REGEXP['section_id'], response_json['payload'][1][0][0])
            playlists = response_json['payload'][1][1]['playlists']
        else:
            return album_list

def load_playlist_content(session, playlist_data):
    audio_list={}
    owner_id, playlist_id = playlist_data.split('_')
    url = 'https://vk.com/al_audio.php?act=load_section'
    payload = {
        'al': '1',
        'claim': '0',
        'from_id': 0,
        'is_loading_all': '1',
        'is_preload': '0',
        'offset': '0',
        'owner_id': owner_id,
        'playlist_id': playlist_id,
        'type': 'playlist'
    }
    
    response = session.post(url, data=payload)
    response_json = json.loads(response.text.lstrip('<!--'))
    if response_json['payload'][1][0] == False:
        print('Error load playlist data')

    audio_list.update(parse_audio_list(response_json['payload'][1][0]['list']))
    return audio_list
    
def download_audio(session, uid, audio_id, artist, song, img_link):
    payload={
        'al': '1',
        'ids': audio_id
        }
    response = session.post('https://vk.com/al_audio.php?act=reload_audio', data=payload)
    response_json = json.loads(response.text.lstrip('<!--'))
    url_mp3 = response_json['payload'][1][0][0][2]
    url_m3u8 = vk_audio.encode_url(url_mp3, int(uid))
    audio_file = vk_audio.m3u8_parser(url_m3u8)
    
    key = meta_new_track(artist, song, img=img_link)
    with open(f'./downloads/{key}.mp3', 'wb') as f:
        f.write(audio_file)
        
    if img_link:
        print('image saved')
        with open(f'./images/t/{key}.jpg', 'wb') as f:
            f.write(requests.get(img_link).content)

def download_album(session, uid, audio_id, name, img_link=None):
    pass

