import os
#import requests
import json
import pickle
import time
import re
import aiohttp
import asyncio
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
    print(type(string))
    s = reg.search(string)
    if s:
        groups = s.groups()
        return groups[0]
    
def clear_string(s):
    if s:
        return s.strip().replace('&nbsp;', '')

class VK_session(object):
    def __init__(self, session_obj, session_name):
        self.session_obj = session_obj
        self.session_name = session_name
        self.path = session_obj.app.app_dir + f'/sessions/{self.session_name}/'
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}
        session_timeout =   aiohttp.ClientTimeout(total=None,sock_connect=5,sock_read=5)
        self.session = aiohttp.ClientSession(headers = headers, timeout = session_timeout)
        

        try:
            with open(self.path + 'coockie_Jar', 'rb') as f:
                cookies = pickle.load(f)
                self.read_cookieJar(cookies)
            
        except FileNotFoundError:
            print('No valid session file')
            shutil.rmtree(self.path)

        try:
            with open(self.path + 'uid', 'rb') as f:
                data = pickle.load(f)
                self.u_id =data['uid']
                print(self.u_id)
                
        except:
            print('No user id')
            shutil.rmtree(self.path)
        else:
            try:
                with open(self.path + 'uid', 'rb') as f:
                    data = pickle.load(f)
                    self.u_name = data['u_name']
            except:
                self.u_name = self.u_id
                
        if 'u_img.jpg' in os.listdir(self.path):
            self.img = self.path + 'u_img.jpg'
        else:
            self.img = './icons/profile.png'

        asyncio.get_event_loop().create_task(self.connect())
    
    async def connect(self):
        response = await self.send_get_request('https://vk.com/login')
        
        if response: # Check if request status code is redirect
            print('Connected')
            self.connected = True
            self.session_obj.title.source = self.img
            self.session_obj.secondary_text = self.u_id
            self.session_obj.on_release=lambda :self.session_obj.open_session()
            self.session_obj.bg_color = (1,1,1,1)
            
        else:
            self.connected = False
            self.session_obj.title.source = "./icons/problem.png"
            self.session_obj.secondary_text = 'Could not connect'
            self.session_obj.on_release=lambda :self.session_obj.session_unavalible()

    
    async def send_get_request(self,url):
        #await asyncio.sleep(3)
        try:
            async with self.session.get(url, timeout=15) as response:
                return await response.text()
            
        except asyncio.exceptions.TimeoutError:
            return None
                
    async def send_post_request(self,url, payload={}):
        try:
            async with self.session.post(url,params=payload, timeout=15) as response:
                return await response.text()
                
        except asyncio.exceptions.TimeoutError:
            return None
        
    def read_cookieJar(self, cookies):
        cookies_list = []
        self.cookies = cookies
        for c in cookies:
            cookies_list.append((c.name, c.value, c.domain, c.path,c.expires))

        self.cookies_list = cookies_list
        self.session.cookie_jar.update_cookies(self.cookies)
        
    def parse_audio_list(self, data):
        audio_list = []
        for elem in data:
            if elem[12] == '[]': # Is it blocked
                h = elem[13].split('/')
                audio_id = elem[15]['content_id'] + '_' + h[2] + '_' + h[5]

                audio_list.append((
                    None,
                    audio_id,
                    convert_ASCII(elem[4]),
                    convert_ASCII(elem[3]),
                    elem[14].split(',')[-1],
                    self
                ))
        return audio_list
            
    async def load_user_audios(self):
        # GET
        url = f'https://vk.com/audios{self.u_id}?section=all'
        response = await self.send_get_request(url)
        if not response:
            return []
        # POST
        section_id_t = search_re(REGEXP['section_id'], response)
        url = 'https://vk.com/audio?act=load_catalog_section'
        payload = {
            'al': '1',
            'section_id': section_id_t
        }
        response = await self.send_post_request(url,payload=payload)
        if not response:
            return []
        # POST
        next_from_t = search_re(REGEXP['next_from'], response)
        response_json = json.loads(response.lstrip('<!--'))
        audio_list = self.parse_audio_list(response_json['payload'][1][1]['playlist']['list'])
        if not next_from_t:
            return audio_list + ['EOF']
        url = 'https://vk.com/al_audio.php?act=load_catalog_section'
        payload['start_from'] = next_from_t
        response = await self.send_post_request(url,payload=payload)
        if not response:
            return []
        # POST
        next_from_t = search_re(REGEXP['next_from'], response)
        response_json = json.loads(response.lstrip('<!--'))
        audio_list += self.parse_audio_list(response_json['payload'][1][1]['playlist']['list'])
        if not next_from_t:
            return audio_list + ['EOF']

        payload['section_id'] = next_from_t.split(' ')[1]
        payload['start_from'] = next_from_t
        response = await self.send_post_request(url,payload=payload)
        if not response:
            return []

        self.next_from_t = search_re(REGEXP['next_from'], response)
        response_json = json.loads(response.lstrip('<!--'))
        audio_list += self.parse_audio_list(response_json['payload'][1][1]['playlist']['list'])
        self.section_id_t = payload['section_id']

        return audio_list if self.next_from_t else audio_list + ['EOF']

    async def load_more_t(self):
        url = 'https://vk.com/al_audio.php?act=load_catalog_section'
        payload = {
            'al': '1',
            'section_id': self.section_id_t,
            'start_from': self.next_from_t
        }
        response = await self.send_post_request(url,payload=payload)
        if not response:
            return []
        #response = self.session.post(url, data=payload)
        response_json = json.loads(response.lstrip('<!--'))
        self.next_from_t = response_json['payload'][1][1]['playlist']['nextOffset']
        audio_list = self.parse_audio_list(response_json['payload'][1][1]['playlist']['list'])
        return audio_list if self.next_from_t else audio_list + ['EOF']

    def parse_album_list(self, data):
        album_list = []
        for playlist in data:
            if playlist['permissions']['play']:
                playlist_name = valid_file_name(playlist['title']) + ' - ' + valid_file_name(playlist['authorName'])
                playlist_id = str(playlist['ownerId'])+'_'+str(playlist['id'])
                album_list.append((playlist_id,convert_ASCII(playlist_name),playlist['coverUrl']))
        return album_list
    
    async def load_playlists(self):
        url = f'https://vk.com/audios{self.u_id}?block=my_playlists&section=all'
        #response = self.session.get(url)
        response = await self.send_get_request(url)
        if not response:
            return []
        self.section_id_a = search_re(REGEXP['section_id'], response)
        url = 'https://vk.com/audio?act=load_catalog_section'
        payload = {
            'al': '1',
            'section_id': self.section_id_a
        }
        response = await self.send_post_request(url,payload=payload)
        if not response:
            return []
        #response = self.session.post(url, data=payload)

        response_json = json.loads(response.lstrip('<!--'))
        self.next_from_a = search_re(REGEXP['data_next'], response_json['payload'][1][0][0])
            
        return self.parse_album_list(response_json['payload'][1][1]['playlists'])
            
    async def load_more_a(self):
        url = 'https://vk.com/al_audio.php?act=load_catalog_section'
        payload = {
            'al': '1',
            'section_id': self.section_id_a,
            'start_from': self.next_from_a
        }
        response = await self.send_post_request(url,payload=payload)
        if not response:
            return []
        #response = self.session.post(url, data=payload)
        response_json = json.loads(response.lstrip('<!--'))
        self.next_from_a = search_re(REGEXP['section_id'], response_json['payload'][1][0][0])
        
        return self.parse_album_list(response_json['payload'][1][1]['playlists'])

    async def load_playlist_content(self, playlist_data):
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
        response = await self.send_post_request(url, payload=payload)
        if not response:
            return []
        #response = self.session.post(url, data=payload)
        response_json = json.loads(response.lstrip('<!--'))
        if response_json['payload'][1][0] == False:
            print('Error load playlist data')

        return self.parse_audio_list(response_json['payload'][1][0]['list'])
        
    async def get_link(self, audio_id):
        print(audio_id)
        url = 'https://vk.com/al_audio.php?act=reload_audio'
        payload={
            'al': '1',
            'ids': audio_id
        }
        response = await self.send_post_request(url,payload=payload)
        if not response:
            return None
        #response = self.session.post('https://vk.com/al_audio.php?act=reload_audio', data=payload)
        response_json = json.loads(response.lstrip('<!--'))
        url_mp3 = response_json['payload'][1][0][0][2]
        url_m3u8 = vk_audio.encode_url(url_mp3, int(self.u_id)).rstrip('?siren=1')
        return url_m3u8

    async def search(self, isglobal, q=''):
        payload = {
            'al': 1,
            'act': 'section',
            'claim': 0,
            'is_layer': 0,
            'owner_id': self.u_id,
            'section': 'search',
            'q': q
        }
        url = 'https://vk.com/al_audio.php'
        response = await self.send_post_request(url,payload=payload)
        if not response:
            return []
        #response = self.session.post(url, data = payload)
        response_json = json.loads(response.lstrip('<!--'))

        if not response_json['payload'][1]: # no permissons
            return []
        
        if isglobal:
            return self.search_global(response_json)
        
        else:
            return self.search_user(response_json)
    
    def search_user(self, response_json):
        if len(response_json['payload'][1][1]['playlists'])==14:
            audio_list = self.parse_audio_list(response_json['payload'][1][1]['playlists'][0]['list'])
            return audio_list
        else:
            return []
    
        
    def search_global(self, response_json):
        if len(response_json['payload'][1][1]['playlists'])==14:
            audio_list = self.parse_audio_list(response_json['payload'][1][1]['playlists'][1]['list'])
        
        else:
            audio_list = self.parse_audio_list(response_json['payload'][1][1]['playlists'][0]['list'])

        return audio_list
        


def save_session(app_dir, session):# Save session
    response = session.get('https://vk.com/settings')

    u_img_url, u_name= search_re(REGEXP['u_img_name'], response.text).split('" alt="')
    uid = search_re(REGEXP['uid'], response.text)
    os.mkdir(app_dir + f'/sessions/vk_{uid}/')
    with open(app_dir + rf'/sessions/vk_{uid}/coockie_Jar', 'wb') as f:
        pickle.dump(session.cookies, f)
        
    with open(app_dir + rf'/sessions/vk_{uid}/u_img.jpg', 'wb') as f:
        f.write(session.get(u_img_url).content)
        
    with open(app_dir + rf'/sessions/vk_{uid}/uid', 'wb') as f:
        pickle.dump({'uid': uid, 'u_name': u_name}, f)
    
def login_request(login, password, captcha_sid='', captcha_key = ''):
    
    session = requests.Session()
    session.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'

    response = session.get('https://vk.com/login')
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
    print(response.text)
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
    
    else:
        response = session.get('https://vk.com/login')
        if response.status_code == 200:
            return (session, None, None, 'Logged in')
        else: # Something else went wrong
            return (None, None, 'Unknow error', None)

                              
# 2FA case
def two_fa(session, code, auth_hash = '', captcha_sid='', captcha_key=''):
    if not auth_hash:
        return (session, None, 'Unknow error')
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




