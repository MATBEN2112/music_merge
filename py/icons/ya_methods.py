import os
import requests
import json
import pickle
import time
import re
import aiohttp
import asyncio
from utils import *#from yandex_music import ClientAsync

REGEXP = {
    'csrf': re.compile(r'"csrf":"(.*?)",'),
    'process_uuid': re.compile(r'"process_uuid":"(.*?)",'),
    'access_token':  re.compile(r'#access_token=(.*?)&')
}
def search_re(reg, string):
    s = reg.search(string)
    if s:
        groups = s.groups()
        return groups[0]
    else:
        return '-'
class YA_session:
    
    def __init__(self, session_obj, session_name):
        client = Client().init()
        self.album_list = []
        self.audio_list = {}
        self._offset_a = 0
        self.session_obj = session_obj
        self.session_name = session_name
        self.app = session_obj.app
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

    def c_audio_list(self, audio_list):
        pass
        
    def parse_audio_list(self, data):
        pass
            
    async def load_user_audios(self,reload=False, album_id='__', load_more = False):
        pass


    def parse_album_list(self, html):
        pass
    
    async def load_playlists(self, reload=False, load_more = False):
        pass
        
    async def get_link(self, audio_id):
        pass

    async def search(self, isglobal, q=''):
        pass
    
    def search_user(self, response_json):
        pass
    
    def search_global(self, response_json):
        pass

class YandexMusicObject:
    """Базовый класс для всех объектов библиотеки."""

    #__metaclass__ = ABCMeta
    _id_attrs = ()

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self) :
        return str(self)

    def __getitem__(self, item):  # noqa: ANN401
        return self.__dict__[item]

    @staticmethod
    def is_valid_model_data(data, *, array = False):  # noqa: ANN401
        """Проверка на валидность данных.

        Args:
            data (:obj:`Any`): Данные для проверки.
            array (:obj:`bool`, optional): Является ли объект массивом.

        Returns:
            :obj:`bool`: Валидны ли данные.
        """
        if array:
            return data and isinstance(data, list) and all(isinstance(item, dict) for item in data)

        return data and isinstance(data, dict)

    @classmethod
    def de_json(cls, data, client):
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.
            client (:obj:`yandex_music.Client`, optional): Клиент Yandex Music.

        Returns:
            :obj:`yandex_music.YandexMusicObject` | :obj:`None`: :obj:`yandex_music.YandexMusicObject` или :obj:`None`.
        """
        if not cls.is_valid_model_data(data):
            return None

        data = data.copy()

        fields = {f.name for f in dataclasses.fields(cls)}

        cleaned_data = {}
        unknown_data = {}

        for k, v in data.items():
            if k in fields:
                cleaned_data[k] = v
            else:
                unknown_data[k] = v

        return cleaned_data

    def to_json(self, for_request = False):
        """Сериализация объекта.

        Args:
            for_request (:obj:`bool`): Подготовить ли объект для отправки в теле запроса.

        Returns:
            :obj:`str`: Сериализованный в JSON объект.
        """
        return json.dumps(self.to_dict(for_request), ensure_ascii=not ujson)

    def to_dict(self, for_request = False):
        """Рекурсивная сериализация объекта.

        Args:
            for_request (:obj:`bool`): Перевести ли обратно все поля в camelCase и игнорировать зарезервированные слова.

        Note:
            Исключает из сериализации `client` и `_id_attrs` необходимые в `__eq__`.

            К зарезервированным словам добавляет "_" в конец.

        Returns:
            :obj:`dict`: Сериализованный в dict объект.
        """

        def parse(val):  # noqa: ANN401
            if hasattr(val, 'to_dict'):
                return val.to_dict(for_request)
            if isinstance(val, list):
                return [parse(it) for it in val]
            if isinstance(val, dict):
                return {key: parse(value) for key, value in val.items()}
            return val

        data = self.__dict__.copy()
        data.pop('client', None)
        data.pop('_id_attrs', None)

        if for_request:
            for k, v in data.copy().items():
                camel_case = ''.join(word.title() for word in k.split('_'))
                camel_case = camel_case[0].lower() + camel_case[1:]

                data.pop(k)
                data.update({camel_case: v})
        else:
            for k, v in data.copy().items():
                if k.lower() in reserved_names:
                    data.pop(k)
                    data.update({f'{k}_': v})

        return parse(data)

    def __eq__(self, other):  # noqa: ANN401
        """Проверка на равенство двух объектов.

        Note:
            Проверка осуществляется по определённым атрибутам классов, перечисленных в множестве `_id_attrs`.

        Returns:
            :obj:`bool`: Одинаковые ли объекты (по содержимому).
        """
        if isinstance(other, self.__class__):
            return self._id_attrs == other._id_attrs
        return super(YandexMusicObject, self).__eq__(other)

    def __hash__(self):
        """Реализация хеш-функции на основе ключевых атрибутов.

        Note:
            Так как перечень ключевых атрибутов хранится в виде множества, для вычисления хеша он замораживается.

        Returns:
            :obj:`int`: Хеш объекта.
        """
        if self._id_attrs:
            frozen_attrs = tuple(frozenset(attr) if isinstance(attr, list) else attr for attr in self._id_attrs)
            return hash((self.__class__, frozen_attrs))
        return super(YandexMusicObject, self).__hash__()

class ClientAsync(YandexMusicObject):
    """Класс, представляющий клиент Yandex Music.

    Note:
        Доступные языки: en, uz, uk, us, ru, kk, hy.

        Поле `device` используется только при работе с очередью прослушивания.

    Attributes:
        logger (:obj:`logging.Logger`): Объект логгера.
        token (:obj:`str`): Уникальный ключ для аутентификации.
        base_url (:obj:`str`): Ссылка на API Yandex Music.
        me (:obj:`yandex_music.Status`): Информация об аккаунте.
        device (:obj:`str`): Строка, содержащая сведения об устройстве, с которого выполняются запросы.


    Args:
        token (:obj:`str`, optional): Уникальный ключ для аутентификации.
        base_url (:obj:`str`, optional): Ссылка на API Yandex Music.
        request (:obj:`yandex_music.utils.request.Request`, optional): Пре-инициализация
            :class:`yandex_music.utils.request.Request`.
        language (:obj:`str`, optional): Язык, на котором будут приходить ответы от API. По умолчанию русский.

    """

    def __init__(self, token = None, base_url = None, request = None, language = 'ru'):

        self.token = token

        if base_url is None:
            base_url = 'https://api.music.yandex.net'

        self.base_url = base_url

        if request:
            self._request = request
            self._request.set_and_return_client(self)
        else:
            self._request = Request(self)

        self.language = language
        self._request.set_language(self.language)


        self.me = None

    @property
    def request(self):
        """:obj:`yandex_music.utils.request.Request`: Объект вспомогательного класса для отправки запросов."""
        return self._request

    async def init(self):
        """Получение информацию об аккаунте использующихся в других запросах."""
        self.me = await self.account_status()
        return self

    async def account_status(self, *args, **kwargs):
        """Получение статуса аккаунта. Нет обязательных параметров.

        Args:
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`yandex_music.Status` | :obj:`None`: Информация об аккаунте если он валиден, иначе :obj:`None`.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        url = f'{self.base_url}/account/status'

        result = await self._request.get(url, *args, **kwargs)

        return Status.de_json(result, self)


    async def tracks_download_info(
        self,
        track_id,
        get_direct_links = False,
        *args,
        **kwargs,
    ):
        """Получение информации о доступных вариантах загрузки трека.

        Args:
            track_id (:obj:`str` | :obj:`list` из :obj:`str`): Уникальный идентификатор трека или треков.
            get_direct_links (:obj:`bool`, optional): Получить ли при вызове метода прямую ссылку на загрузку.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.DownloadInfo` | :obj:`None`: Варианты загрузки трека или :obj:`None`.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        url = f'{self.base_url}/tracks/{track_id}/download-info'

        result = await self._request.get(url, *args, **kwargs)

        return await DownloadInfo.de_list_async(result, self, get_direct_links)


    async def albums_with_tracks(self, album_id, *args, **kwargs):
        """Получение альбома по его уникальному идентификатору вместе с треками.

        Args:
            album_id (:obj:`str` | :obj:`int`): Уникальный идентификатор альбома.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.Album` | :obj:`None`: Альбом или :obj:`None`.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        url = f'{self.base_url}/albums/{album_id}/with-tracks'

        result = await self._request.get(url, *args, **kwargs)

        return Album.de_json(result, self)

    async def search(
        self,
        text,
        nocorrect = False,
        type_ = 'all',
        page = 0,
        playlist_in_best = True,
        *args,
        **kwargs,
    ):
        """Осуществление поиска по запросу и типу, получение результатов.

        Note:
            Известные значения для поля `type_`: `all`, `artist`, `user`, `album`, `playlist`, `track`, `podcast`,
            `podcast_episode`.

            При поиске `type=all` не возвращаются подкасты и эпизоды. Указывайте конкретный тип для поиска.

        Args:
            text (:obj:`str`): Текст запроса.
            nocorrect (:obj:`bool`): Если :obj:`False`, то ошибочный запрос будет исправлен. Например, запрос
                "Гражданская абарона" будет исправлен на "Гражданская оборона".
            type_ (:obj:`str`): Среди какого типа искать (трек, плейлист, альбом, исполнитель, пользователь, подкаст).
            page (:obj:`int`): Номер страницы.
            playlist_in_best (:obj:`bool`): Выдавать ли плейлисты лучшим вариантом поиска.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`yandex_music.Search` | :obj:`None`: Результаты поиска или :obj:`None`.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        url = f'{self.base_url}/search'

        params = {
            'text': text,
            'nocorrect': str(nocorrect),
            'type': type_,
            'page': page,
            'playlist-in-best': str(playlist_in_best),
        }

        result = await self._request.get(url, params, *args, **kwargs)

        if isinstance(result, str):
            raise BadRequestError(result)

        return Search.de_json(result, self)

    async def artists_tracks(
        self,
        artist_id,
        page = 0,
        page_size = 20,
        *args,
        **kwargs,
    ):
        """Получение треков артиста.

        Args:
            artist_id (:obj:`str` | :obj:`int`): Уникальный идентификатор артиста.
            page (:obj:`int`, optional): Номер страницы.
            page_size (:obj:`int`, optional): Количество треков на странице.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`yandex_music.ArtistsTracks` | :obj:`None`: Страница списка треков артиста или :obj:`None`.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        url = f'{self.base_url}/artists/{artist_id}/tracks'

        params = {'page': page, 'page-size': page_size}

        result = await self._request.get(url, params, *args, **kwargs)

        return ArtistTracks.de_json(result, self)




    async def _get_list(
        self,
        object_type,
        ids,
        params = None,
        *args,
        **kwargs,
    ):
        """Получение объекта/объектов.

        Args:
            object_type (:obj:`str`): Тип объекта.
            ids (:obj:`str` | :obj:`int` | :obj:`list` из :obj:`str` | :obj:`list` из :obj:`int`): Уникальный
                идентификатор объекта или объектов.
            params (:obj:`dict`, optional): Параметры, которые будут переданы в запрос.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.Artist` | :obj:`list` из :obj:`yandex_music.Album` |
                :obj:`list` из :obj:`yandex_music.Track` | :obj:`list` из :obj:`yandex_music.Playlist`: Запрошенный
                объект.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        if params is None:
            params = {}
        params.update({f'{object_type}-ids': ids})

        url = f'{self.base_url}/{object_type}s' + ('/list' if object_type == 'playlist' else '')

        result = await self._request.post(url, params, *args, **kwargs)

        return de_list[object_type](result, self)

    async def artists(self, artist_ids, *args, **kwargs):
        """Получение исполнителя/исполнителей.

        Args:
            artist_ids (:obj:`str` | :obj:`int` | :obj:`list` из :obj:`str` | :obj:`list` из :obj:`int`): Уникальный
                идентификатор исполнителя или исполнителей.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.Artist`: Исполнитель или исполнители.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        return await self._get_list('artist', artist_ids, *args, **kwargs)

    async def albums(self, album_ids, *args, **kwargs):
        """Получение альбома/альбомов.

        Args:
            album_ids (:obj:`str` | :obj:`int` | :obj:`list` из :obj:`str` | :obj:`list` из :obj:`int`): Уникальный
                идентификатор альбома или альбомов.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.Album`: Альбом или альбомы.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        return await self._get_list('album', album_ids, *args, **kwargs)

    async def tracks(
        self,
        track_ids,
        with_positions = True,
        *args,
        **kwargs,
    ):
        """Получение трека/треков.

        Args:
            track_ids (:obj:`str` | :obj:`int` | :obj:`list` из :obj:`str` | :obj:`list` из :obj:`int`): Уникальный
                идентификатор трека или треков.
            with_positions (:obj:`bool`, optional): С позициями TODO.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.Track`: Трек или Треки.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        return await self._get_list('track', track_ids, {'with-positions': str(with_positions)}, *args, **kwargs)

    async def playlists_list(
        self, playlist_ids, *args, **kwargs
    ):
        """Получение плейлиста/плейлистов.

        Note:
            Идентификатор плейлиста указывается в формате `owner_id:playlist_id`. Где `playlist_id` - идентификатор
            плейлиста, `owner_id` - уникальный идентификатор владельца плейлиста.

            Данный метод возвращает сокращенную модель плейлиста для отображения больших список.

        Warning:
            Данный метод не возвращает список треков у плейлиста! Для получения объекта :obj:`yandex_music.Playlist` c
            заполненным полем `tracks` используйте метод :func:`yandex_music.ClientAsync.users_playlists` или
            метод :func:`yandex_music.Playlist.fetch_tracks`.

        Args:
            playlist_ids (:obj:`str` | :obj:`int` | :obj:`list` из :obj:`str` | :obj:`list` из :obj:`int`): Уникальный
                идентификатор плейлиста или плейлистов.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.Playlist`: Плейлист или плейлисты.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        return await self._get_list('playlist', playlist_ids, *args, **kwargs)

    async def users_playlists_list(self, user_id = None, *args, **kwargs):
        """Получение списка плейлистов пользователя.

        Args:
            user_id (:obj:`str` | :obj:`int`, optional): Уникальный идентификатор пользователя. Если не указан
                используется ID текущего пользователя.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.Playlist`: Плейлисты пользователя.

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        if user_id is None and self.me is not None:
            user_id = self.me.account.uid

        url = f'{self.base_url}/users/{user_id}/playlists/list'

        result = await self._request.get(url, *args, **kwargs)

        return Playlist.de_list(result, self)

    async def _get_likes(
        self,
        object_type,
        user_id = None,
        params = None,
        *args,
        **kwargs,
    ):
        """Получение объектов с отметкой "Мне нравится".

        Args:
            object_type (:obj:`str`): Тип объекта.
            user_id (:obj:`str` | :obj:`int`, optional): Уникальный идентификатор пользователя. Если не указан
                используется ID текущего пользователя.
            params (:obj:`dict`, optional): Параметры, которые будут переданы в запрос.
            *args: Произвольные аргументы (будут переданы в запрос).
            **kwargs: Произвольные именованные аргументы (будут переданы в запрос).

        Returns:
            :obj:`list` из :obj:`yandex_music.Like` | :obj:`yandex_music.TracksList`: Объекты с отметкой "Мне нравится".

        Raises:
            :class:`yandex_music.exceptions.YandexMusicError`: Базовое исключение библиотеки.
        """
        if user_id is None and self.me is not None:
            user_id = self.me.account.uid

        url = f'{self.base_url}/users/{user_id}/likes/{object_type}s'

        result = await self._request.get(url, params, *args, **kwargs)

        if object_type == 'track':
            return TracksList.de_json(result.get('library'), self)

        return Like.de_list(result, self, object_type)

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
    client_id = '23cabbbdc6cd418abb4b39c32c41195d'
    retpath = f'https://oauth.yandex.ru/authorize?response_type=token&client_id={client_id}'
    response = session.get(retpath)
    if not response:
        return (None, None, 'To much requests')
    
    process_uuid = search_re(REGEXP['process_uuid'], response.text)
    csrf_token = search_re(REGEXP['csrf'], response.text)
    
    if (not login) or (not password):
        return (None, None, 'Fields should not be empty')
    
    payload = {
        'csrf_token': csrf_token,
        'login': login,
        'process_uuid': process_uuid,
        'retpath': retpath,
        'origin': 'oauth'
        }

    response = session.post(
        'https://passport.yandex.ru/registration-validations/auth/multi_step/start',
        data=payload,
    )
    # phone login callback
    '''
    {
        "status":"ok",
        "use_new_suggest_by_phone":false,
        "phone_number":{
            "masked_original":"+7 (999) ***-**-99",
            "masked_international":"+7 999 ***-**-99",
            "masked_e164":"+7999*****99",
            "original":"+7 (999) 999-99-99",
            "international":"+7 999 999-99-99",
            "e164":"+79999999999"
            },
        "country":"ru",
        "can_register":true,
        "account_type":"portal",
        "allowed_account_types":["portal","neophonish"],
        "login":null,
        "track_id":"a2e821d169b9542db557b8082ea61e8a49"
    }
    '''
    # email login callback
    '''
    {
        "status":"ok",
        "use_new_suggest_by_phone":false,
        "primary_alias_type":1,
        "csrf_token":"f14aab90bbfd2038b4d4b83dc3939a8b",
        "magic_link_email":"email@yandex.ru",
        "track_id":"7878acd0ae01cf9209f3594717724e7dcd",
        "can_authorize":true,
        "auth_methods":["password","magic_link","magic_x_token","magic_x_token_with_pictures"],
        "preferred_auth_method":"password",
        "is_rfc_2fa_enabled":false
    }
    '''
    response_json = response.json()
    print(response_json)
    is_2fa = response_json['is_rfc_2fa_enabled'] if 'is_rfc_2fa_enabled' in response_json else False
    track_id = response_json['track_id']
    print(is_2fa,track_id)
    if True: # login by email
        # commit_password
        payload = {
            'csrf_token': csrf_token,
            'track_id': track_id,
            'password': password,
            'retpath': retpath,
            'lang': 'ru'
            }
        
        response = session.post(
            'https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password',
            data=payload
        )

    
    else: # login by phone number
        # check phone possibilities
        payload = {
            'csrf_token': csrf_token,
            'track_id': track_id,
            'number': login,
        }
        
        response = session.post(
            'https://passport.yandex.ru/registration-validations/check-phone-possibilities',
            data=payload
        )
        # validate phone
        payload = {
            'csrf_token': csrf_token,
            'track_id': track_id,
            'validate_for_call': True,
            'phone_number': login,
            'validate_for_message_protocols': True
        }
        
        response = session.post(
            'https://passport.yandex.ru/registration-validations/validate-phone',
            data=payload
        )
        # phone confirm code submit
        payload = {
            'csrf_token': csrf_token,
            'track_id': track_id,
            'display_language': 'ru',
            'number': login,
            'isCodeWithFormat': True
        }
        response = session.post(
            'https://passport.yandex.ru/registration-validations/phone-confirm-code-submit',
            data=payload
        )
    print(response.text)
    # finally get an access token
    response = session.get('https://passport.yandex.ru/redirect?' \
          'url=https%3A%2F%2Foauth.yandex.ru' \
          f'%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3D{client_id}')

    access_token = search_re(REGEXP['access_token'], response.text)
    return (response, session, access_token)


                              
# 2FA case
def two_fa(session, code, auth_hash = '', captcha_sid='', captcha_key=''):
    pass

if __name__ == '__main__':
    #r, s, token = login_request('pod.pivasnick@yandex.ru','T3sT_case')

    token = 'y0_AgAAAABaYfW2AAG8XgAAAAEA0cd8AAAZRTiU9ltNd5kD4mOAqhrWLk2qQg'


    client = ClientAsync(token).init()
    client.users_likes_tracks()[0].fetch_track().download('example.mp3')
