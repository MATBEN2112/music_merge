import functools
import re
from tempfile import NamedTemporaryFile
import requests

def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

def convert_ASCII(string):
    return re.sub(r'&#([0-9]+);',lambda x: chr(int(x.groups()[0])) if x[0] != 0 else chr(int(x.groups()[0][1:])), string)

def valid_file_name(string):
    string = convert_ASCII(string)
    string = re.sub(r'[Ёё]',lambda x: 'е', string)
    string = re.sub(r'(\s+-\s+)+',lambda x: '-', string)
    return re.sub(r'[^\sA-Za-zА-Яа-я0-9_-]+',lambda x: '', string)

from csv import DictWriter, DictReader
import os
import sqlite3

class Meta(object):
    def __init__(self, app_path):
        self.app_path = app_path
        self.db = sqlite3.connect(self.app_path + "/music_meta.db")
        self.cursor = self.db.cursor()
        #self.db.close()
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS AlbumList (
            id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            path      TEXT GENERATED ALWAYS AS ({"'"+self.app_path+"'"}||'/downloads/'||id||'/') VIRTUAL,
            name    TEXT,
            img       TEXT DEFAULT ('./icons/song.png'));
        """)
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS TrackList (
            id                 INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            path             TEXT GENERATED ALWAYS AS ({"'"+self.app_path+"'"}||'/downloads/'||id||'.mp3') VIRTUAL,
            artist            TEXT,
            song            TEXT,
            img              TEXT DEFAULT ('./icons/track.png'));
        """)
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS Relationship (
        
            track_id            INTEGER NOT NULL,
            album_id          INTEGER DEFAULT NULL,
        
            FOREIGN KEY(album_id) REFERENCES AlbumList(id),
            FOREIGN KEY(track_id) REFERENCES TrackList(id));
        """)
        
    def reasseble_db(self):
        ''' DB bug fix case '''
        pass
    
    def album_list(self):
        ''' Return list of albums '''
        self.cursor.execute("SELECT * FROM AlbumList;")
        return self.cursor.fetchall()[::-1]

    def track_list(self, key = None):
        ''' Search for album content or outer content '''
        self.cursor.execute('''SELECT * FROM TrackList WHERE id in
            (SELECT track_id FROM Relationship WHERE album_id is ?);''', (key,)
        )
        return self.cursor.fetchall()[::-1]
        
    def add_album(self, name, img=None):
        ''' Create new album '''
        if img:
            self.cursor.execute("INSERT INTO AlbumList (name, img) VALUES (?, ?);",(name, img))
        else:
            self.cursor.execute("INSERT INTO AlbumList (name) VALUES (?);",(name,))

        self.db.commit()
        return self.cursor.lastrowid

    def new_track(self, artist, song, img):
        ''' Function to append track data to existing meta file '''
        self.cursor.execute('''
            INSERT INTO TrackList (artist, song, img) VALUES (?, ?, ?);''',(artist, song, img,))
        last_row_id = self.cursor.lastrowid
        if img!="./icons/track.png":
            print('image saved')
            img_path = self.app_path + f'/images/t/{last_row_id}.jpg'
            with open(img_path, 'wb') as f:
                f.write(requests.get(img).content)
            self.cursor.execute(''' UPDATE TrackList SET img=? WHERE id=?;''',(img_path,last_row_id,))
        
        self.cursor.execute('''INSERT INTO Relationship (track_id, album_id)
            SELECT max(id), NULL FROM TrackList;''')

        
        self.db.commit()
        return last_row_id

        
    def add_to_album(self, key_track, key_album):
        self.cursor.execute('''
                INSERT INTO Relationship (track_id, album_id) VALUES (?,?);
                       ''',(key_track, key_album,))
        self.db.commit()
    
    def edit_track(self, key, artist, song):
        self.cursor.execute("UPDATE TrackList SET artist=?, song=? WHERE id=?;", (artist, song, key,))
        self.db.commit()
        
    def edit_album(self, key, name):
        self.cursor.execute("UPDATE AlbumList SET name=? WHERE id=?;", (name, key,))
        self.db.commit()
    
    def delete_track(self, key_track, key_album=None):
        self.cursor.execute('''DELETE FROM Relationship WHERE track_id=? AND album_id is ?;''',
                   (key_track, key_album,))
        # check if any relationship remains
        self.cursor.execute('''SELECT path, img FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
        for path, img in self.cursor.fetchall():
            os.remove(path)
            if img != './icons/track.png':
                os.remove(img)
    
        self.cursor.execute('''DELETE FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
        self.db.commit()

    def delete_album(self, key):
        self.cursor.execute('''DELETE FROM Relationship WHERE album_id=?;''', (key,))
        self.cursor.execute('''DELETE FROM AlbumList WHERE id=?;''', (key,))
        # check if any relationship remains
        self.cursor.execute('''SELECT path, img FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
        for path, img in self.cursor.fetchall():
            os.remove(path)
            if img != './icons/track.png':
                os.remove(img)
        self.cursor.execute('''DELETE FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
        self.db.commit()
                   
