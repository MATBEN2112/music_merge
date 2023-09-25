import functools
import re
from tempfile import NamedTemporaryFile

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

with sqlite3.connect("./Documents/music_meta.db") as db:
    cursor = db.cursor()
    
cursor.execute("PRAGMA foreign_keys = ON")

def meta_start():
    cursor.execute("""CREATE TABLE IF NOT EXISTS AlbumList (
        id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        path      TEXT GENERATED ALWAYS AS ('./downloads/'||id||'/') VIRTUAL,
        name    TEXT,
        img       TEXT DEFAULT ('./icons/song.png'));
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS TrackList (
        id                 INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        path             TEXT GENERATED ALWAYS AS ('./downloads/'||id||'.mp3') VIRTUAL,
        artist            TEXT,
        song            TEXT,
        img              TEXT DEFAULT ('./icons/track.png'));
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS Relationship (
        
        track_id            INTEGER NOT NULL,
        album_id          INTEGER DEFAULT NULL,
        
        FOREIGN KEY(album_id) REFERENCES AlbumList(id),
        FOREIGN KEY(track_id) REFERENCES TrackList(id));
        """)
    
def meta_album_list():
    cursor.execute("SELECT * FROM AlbumList;")
    return cursor.fetchall()[::-1]

def meta_track_list(key = None):
    ''' Search for album content or outer content '''
    cursor.execute('''SELECT * FROM TrackList WHERE id in
            (SELECT track_id FROM Relationship WHERE album_id is ?);''', (key,)
    )
    return cursor.fetchall()[::-1]
        
def meta_add_album(name, img=None):
    ''' Fucn to append created album data to album meta info file. Also creates meta file inside album dir '''
    if img:
        cursor.execute("INSERT INTO AlbumList (name, img) VALUES (?, ?);",(name, img))
    else:
        cursor.execute("INSERT INTO AlbumList (name) VALUES (?);",(name,))

    db.commit()
    return cursor.lastrowid

def meta_new_track(artist, song, img=None):
    ''' Function to append track data to existing meta file '''
    if img:
        cursor.execute('''
            INSERT INTO TrackList (artist, song, img) VALUES (?, ?, ?);''',(artist, song, img,))
        last_row_id = cursor.lastrowid
        cursor.execute('''INSERT INTO Relationship (track_id, album_id)
            SELECT max(id), NULL FROM TrackList;''')
        
    else:
        cursor.execute('''
            INSERT INTO TrackList (artist, song) VALUES (?, ?);''',(artist, song,))
        last_row_id = cursor.lastrowid
        cursor.execute('''INSERT INTO Relationship (track_id, album_id)
            SELECT max(id), NULL FROM TrackList;''')

    db.commit()
    return last_row_id

        
def meta_add_to_album(key_track, key_album):
    cursor.execute('''
            INSERT INTO Relationship (track_id, album_id) VALUES (?,?);
                   ''',(key_track, key_album,))
    db.commit()
    
def meta_edit_track(key, artist, song):
    cursor.execute("UPDATE TrackList SET artist=?, song=? WHERE id=?;", (artist, song, key,))
    db.commit()
        
def meta_edit_album(key, name):
    cursor.execute("UPDATE AlbumList SET name=? WHERE id=?;", (name, key,))
    db.commit()
    
def delete_meta_track(key_track, key_album=None):
    cursor.execute('''DELETE FROM Relationship WHERE track_id=? AND album_id is ?;''',
                   (key_track, key_album,))
    # check if any relationship remains
    cursor.execute('''SELECT path, img FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
    for path, img in cursor.fetchall():
        os.remove(path)
        if img != './icons/track.png':
            os.remove(img)
    
    cursor.execute('''DELETE FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
    db.commit()

def delete_meta_album(key):
    cursor.execute('''DELETE FROM Relationship WHERE album_id=?;''', (key,))
    cursor.execute('''DELETE FROM AlbumList WHERE id=?;''', (key,))
    # check if any relationship remains
    cursor.execute('''SELECT path, img FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
    for path, img in cursor.fetchall():
        os.remove(path)
        if img != './icons/track.png':
            os.remove(img)
    cursor.execute('''DELETE FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
    db.commit()
                   
