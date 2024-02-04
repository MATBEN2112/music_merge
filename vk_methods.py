import os
import requests
import json
import pickle
import time
import re
import aiohttp
import asyncio
import vk_audio
import shutil
from utils import *
from bs4 import BeautifulSoup
from hashlib import md5

DEFAULT_COOKIES = { 'remixaudio_show_alert_today':
    {
        'version': 0,
        'name': 'remixaudio_show_alert_today',
        'value': '0',
        'port': None,
        'port_specified': False,
        'domain': '.vk.com',
        'domain_specified': True,
        'domain_initial_dot': True,
        'path': '/',
        'path_specified': True,
        'secure': True,
        'expires': None,
        'discard': False,
        'comment': None,
        'comment_url': None,
        'rfc2109': False,
        'rest': {}
    }, 'remixmdevice': {
        'version': 0,
        'name': 'remixmdevice',
        'value': '1920/1080/2/!!-!!!!',
        'port': None,
        'port_specified': False,
        'domain': '.vk.com',
        'domain_specified': True,
        'domain_initial_dot': True,
        'path': '/',
        'path_specified': True,
        'secure': True,
        'expires': None,
        'discard': False,
        'comment': None,
        'comment_url': None,
        'rfc2109': False,
        'rest': {}
    }
}

REGEXP = {
    'ascii': re.compile(r'&#([0-9]+);'),
    'album_id': re.compile(r'act=audio_playlist(-?\d+)_(\d+)'),
    'access_hash': re.compile(r'access_hash=(\w+)'),
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

TRACKS_PER_USER_PAGE = 2000
TRACKS_PER_ALBUM_PAGE = 2000
ALBUMS_PER_USER_PAGE = 100

def search_re(reg, string):
    s = reg.search(string)
    if s:
        groups = s.groups()
        return groups[0]
    else:
        return ''
    
def clear_string(s):
    if s:
        return s.strip().replace('&nbsp;', '')

class VK_session(object):
    def __init__(self, session_obj, session_name):
        self.album_list = []
        self.audio_list = {}
        self._offset_a = 0
        self.session_obj = session_obj
        self.session_name = session_name
        self.path = session_obj.app.app_dir + f'/sessions/{self.session_name}/'
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}
        session_timeout =   aiohttp.ClientTimeout(total=None,sock_connect=5,sock_read=5)
        self.session = aiohttp.ClientSession(headers = headers, timeout = session_timeout,connector=aiohttp.TCPConnector(verify_ssl=False))
        

        try:
            with open(self.path + 'coockie_Jar', 'rb') as f:
                cookies = pickle.load(f)
                self.read_cookieJar(cookies)
            
        except FileNotFoundError:
            print('No valid session file')
            return shutil.rmtree(self.path)

        try:
            with open(self.path + 'uid', 'rb') as f:
                data = pickle.load(f)
                self.u_id =data['uid']
                print(self.u_id)
                
        except:
            print('No user id')
            return shutil.rmtree(self.path)
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
            self.session_obj.ids._left_container.clear_widgets()
            self.session_obj.title.source = self.img
            self.session_obj.ids._left_container.add_widget(self.session_obj.title)
            
            
            self.session_obj.secondary_text = self.u_id
            self.session_obj.on_release=lambda :self.session_obj.open_session()
            self.session_obj.bg_color = (1,1,1,1)
            
        else:
            self.connected = False
            self.session_obj.ids._left_container.clear_widgets()
            self.session_obj.ids._left_container.add_widget(self.session_obj.problem_title)
            self.session_obj.secondary_text = 'Could not connect'
            self.session_obj.on_release=lambda :self.session_obj.session_unavalible()

    
    async def send_get_request(self, url, params={}, allow_redirects = True):
        try:
            async with self.session.get(url, timeout=15, params=params,allow_redirects=allow_redirects) as response:
                print(response.real_url)
                if str(response.url).startswith('https://vk.com/429.html?'):
                    hash429_md5 = md5(self.session.cookies['hash429'].encode('ascii')).hexdigest()
                    self.session.cookies.pop('hash429')
                    response = await self.send_get_request(f'{response.url}&key={hash429_md5}', timeout=15, params=params,allow_redirects=allow_redirects)
                return await response.text()
            
        except asyncio.exceptions.TimeoutError:
            return None
                
    async def send_post_request(self, url, params={}, allow_redirects = True):
        try:
            async with self.session.post(url, params=params, timeout=15,allow_redirects=allow_redirects) as response:
                return await response.text()
                
        except asyncio.exceptions.TimeoutError:
            return None
        
    def read_cookieJar(self, cookies):
        
        self.session.cookie_jar.unsafe=True
        cookies_list = []
        self.cookies = cookies
        for c in cookies:
            cookies_list.append((c.name, c.value, c.domain, c.path,c.expires)) 

        self.cookies_list = cookies_list
        self.session.cookie_jar.update_cookies(self.cookies)
        self.session.cookie_jar.update_cookies(DEFAULT_COOKIES)
        
        
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
            
    async def load_user_audios(self,reload=False, album_id='__', load_more = False):
        print(f'### Load local {reload}. Album id: {album_id} ###')
        a_id = album_id.split('_')
        owner_id = a_id[0] if a_id[0] else self.u_id
        album_id = a_id[1] if a_id[1] else -1
        access_hash = a_id[2]

        if not reload and album_id in self.audio_list and not load_more:
            print('Local audio list used.')
            return self.audio_list[album_id][0]

        url = 'https://m.vk.com/'
        response = await self.send_get_request(url)

        if not response:
            print('No response')
            return ['EOL']
        
        url = 'https://m.vk.com/audio'
        params = {
            'act': 'load_section',
            'owner_id': owner_id,
            'playlist_id': album_id,
            'offset':  self.audio_list[album_id][1] if load_more else 0,
            'type': 'playlist',
            'access_hash': access_hash,
            'is_loading_all': 1
        }
        response = await self.send_post_request(url,params=params, allow_redirects=False)
        
        if not response: # relog needed [appear only in mobile version] [FIX]
            print('Relog needed')
            return ['EOL']
        
        response_json = json.loads(response)
        
        if not response_json['data'][0]: # no permissions
            print('No permissions')
            return ['EOL']

        audio_list = self.parse_audio_list(response_json['data'][0]['list'])
            
        if load_more:
            if  album_id == -1:
                self.audio_list[album_id] = [
                    self.audio_list[album_id][0] + audio_list,
                    self.audio_list[album_id][1] + TRACKS_PER_USER_PAGE
                ]
            else:
                self.audio_list[album_id] = [
                    self.audio_list[album_id][0] + audio_list,
                    self.audio_list[album_id][1] + TRACKS_PER_ALBUM_PAGE
                ]

            if not response_json['data'][0]['hasMore']:
                self.audio_list[album_id][0] += ['EOL']
                
        elif response_json['data'][0]['hasMore']:
            if  album_id == -1:
                self.audio_list[album_id] = [audio_list,TRACKS_PER_USER_PAGE]
                
            else:
                self.audio_list[album_id] = [audio_list,TRACKS_PER_ALBUM_PAGE]

        else:
            self.audio_list[album_id] = [audio_list+ ['EOL'],-1]
            
        return self.audio_list[album_id][0]


    def parse_album_list(self, html):
        album_list = []
        soup = BeautifulSoup(html, 'html.parser')

        for album in soup.find_all('div', {'class': 'audioPlaylistsPage__item'}):
            if album.select_one('.audioPlaylistsPage__cover')['style']:
                title = album.select_one('.audioPlaylistsPage__cover')['style'].split("'")[1]
            else:
                continue

            name = album.select_one('.audioPlaylistsPage__title').text + ' ' + album.select_one('.audioPlaylistsPage__author').text
            link = album.select_one('.audioPlaylistsPage__itemLink')['href']
            full_id = [g for g in REGEXP['album_id'].search(link).groups()]
            access_hash = search_re(REGEXP['access_hash'], link)

            album_list.append((full_id[0]+'_'+full_id[1]+'_'+access_hash,name,title))

        return album_list
    
    async def load_playlists(self, reload=False):
        print(f'### Load local {reload} ###')
        if not reload and self.album_list:
            print('### Local audio list used. ###')
            return self.album_list
        else:
            self.album_list= []
            self._offset_a = 0

        url = 'https://m.vk.com/'
        response = await self.send_get_request(url)
        if not response:
            return ['EOL']
        
        url = f'https://m.vk.com/audio?act=audio_playlists{self.u_id}'
        params = {'offset': self._offset_a}
        response = await self.send_post_request(url, params=params, allow_redirects = False)
        if not response:
            return ['EOL']
                      
        album_list = self.parse_album_list(response)

        if not album_list or len(album_list)<ALBUMS_PER_USER_PAGE:
            self.album_list = album_list + ['EOL']
            return self.album_list
        
        else:
            self._offset_a += ALBUMS_PER_USER_PAGE
            self.album_list += album_list
            return album_list

        
    async def get_link(self, audio_id):
        print(audio_id)
        url = 'https://vk.com/al_audio.php?act=reload_audio'
        params={
            'al': '1',
            'ids': audio_id
        }
        response = await self.send_post_request(url, params=params)
        if not response:
            return None
        #response = self.session.post('https://vk.com/al_audio.php?act=reload_audio', data=payload)
        response_json = json.loads(response.lstrip('<!--'))
        url_mp3 = response_json['payload'][1][0][0][2]
        url_m3u8 = vk_audio.encode_url(url_mp3, int(self.u_id)).rstrip('?siren=1')
        return url_m3u8

    async def search(self, isglobal, q=''):
        params = {
            'al': 1,
            'act': 'section',
            'claim': 0,
            'is_layer': 0,
            'owner_id': self.u_id,
            'section': 'search',
            'q': q
        }
        url = 'https://vk.com/al_audio.php'
        response = await self.send_post_request(url, params=params)
        if not response:
            return ['EOL']
        #response = self.session.post(url, data = payload)
        response_json = json.loads(response.lstrip('<!--'))

        if not response_json['payload'][1]: # no permissons
            return ['EOL']

        if not len(response_json['payload'][1][1]['playlists']): # no matches
            return ['EOL']
            
        if isglobal:
            return self.search_global(response_json)
        
        else:
            return self.search_user(response_json)
    
    def search_user(self, response_json):
        if response_json['payload'][1][1]['playlists'][0]['list'][0][11] == 'search_results:search_owned_audios':
            audio_list = self.parse_audio_list(response_json['payload'][1][1]['playlists'][0]['list'])
            return audio_list + ['EOL']
        else:
            return ['EOL']
    
    def search_global(self, response_json):
        if response_json['payload'][1][1]['playlists'][0]['list'][0][11] == 'search_results:search_owned_audios':
            audio_list = self.parse_audio_list(response_json['payload'][1][1]['playlists'][1]['list'])
            return audio_list + ['EOL']
        elif response_json['payload'][1][1]['playlists'][0]['list'][0][11] == 'search_results:search_global_audios':
            audio_list = self.parse_audio_list(response_json['payload'][1][1]['playlists'][0]['list'])
            return audio_list + ['EOL']
        else:
            return ['EOL']
        


def save_session(app_dir, session):# Save session
    response = session.get('https://vk.com/settings')

    u_img_url, u_name= search_re(REGEXP['u_img_name'], response.text).split('" alt="')
    uid = search_re(REGEXP['uid'], response.text)
    i = 0
    while True:
        try:
            os.mkdir(app_dir + f'/sessions/vk_{uid}_{i}/')
        except FileExistsError:
            i += 1
        else:
            break
        
    with open(app_dir + rf'/sessions/vk_{uid}_{i}/coockie_Jar', 'wb') as f:
        pickle.dump(session.cookies, f)
        
    with open(app_dir + rf'/sessions/vk_{uid}_{i}/u_img.jpg', 'wb') as f:
        f.write(session.get(u_img_url).content)
        
    with open(app_dir + rf'/sessions/vk_{uid}_{i}/uid', 'wb') as f:
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
    print(response.text)
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

    if number[:prefix_len] != prefix:
        return

    if number[-postfix_len:] != postfix:
        return

    return number[prefix_len:-postfix_len]

# Captcha case        
def captcha(app_dir,session=requests.Session(), sid='123'):
    captcha_img_link = f'https://api.vk.com/captcha.php?sid={sid}'
    with open(app_dir+'captcha.jpg', 'wb') as f:
        f.write(session.get(captcha_img_link).content)



