def rgba2hex(rgba):
    return f'{int(rgba[0]):x}{int(rgba[1]):x}{int(rgba[2]):x}{int(rgba[3]*255):x}' if any([clr > 1 for clr in rgba[:-1]]) \
    else f'{int(rgba[0]*255):x}{int(rgba[1]*255):x}{int(rgba[2]*255):x}{int(rgba[3]*255):x}'

def rgb2hex(rgb):
    return f'{int(rgb[0]):x}{int(rgb[1]):x}{int(rgb[2]):x}' if any([clr > 1 for clr in rgb]) else \
    f'{int(rgb[0]*255):x}{int(rgb[1]*255):x}{int(rgb[2]*255):x}'

def hex2rgba(hex_string):
    rgba = [int(hex_string[i:i+2],16) for i in range(0,7,2)]    
    return (*rgba,)

def hex2rgb(hex_string):
    rgb = [int(hex_string[i:i+2],16) for i in range(0,5,2)]    
    return (*rgb,)

import functools
import re
import time

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

def search_audio(data, q=''):
    # TODO implement phonetic algorithm
    result = []
    qq = ''
    for i in q:# escape re meta symbols
        qq += f'[{i}]'
        
    q_regexp = re.compile(rf'(.*){qq}(.*)', re.IGNORECASE)
    for track in data:
        if track == 'EOL':
            break
        s = q_regexp.search(track[2]+track[3])

        if s:
            result.append(track)

    return result + ['EOL']
        

import os
import sqlite3

class Meta(object):
    def __init__(self, app, dev_mode=False):
        self.dev_mode = dev_mode
        self.app = app
        self.app_path = app.app_dir
        self.db = sqlite3.connect(self.app_path + "/music_meta.db")
        self.cursor = self.db.cursor()
        #self.db.close()
        if self.dev_mode:
            self.hard_reasseble_db()
        else:
            self.start_db()
        

    def start_db(self):
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS AlbumList (
            id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name    TEXT,
            img       TEXT DEFAULT ('./icons/song.png'));
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS TrackList (
            id                 INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            path             TEXT NOT NULL,
            artist            TEXT,
            song            TEXT,
            img              TEXT DEFAULT ('./icons/player_back.png'));
        """)
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS Relationship (
        
            track_id            INTEGER NOT NULL,
            album_id          INTEGER DEFAULT NULL,
        
            FOREIGN KEY(album_id) REFERENCES AlbumList(id),
            FOREIGN KEY(track_id) REFERENCES TrackList(id));
        """)
            
        
    def reasseble_db(self):
        ''' DB bug fix case '''
        row_to_delete = []
        row_to_fix = []
        content = os.listdir(self.app_path+'/downloads/')
        self.cursor.execute("SELECT * FROM TrackList;")
        track_list = self.cursor.fetchall()[::-1]
        for track in track_list:
            if str(track[0]) +'.mp3' in content:
                if self.app_path not in track[1]:
                    row_to_fix.append(track[0])
            else:
                row_to_delete.append(track[0])

        self.cursor.execute('DELETE FROM TrackList WHERE id IN (' + ','.join(['?']*len(row_to_delete)) + ');',tuple(row_to_delete))
        self.cursor.execute('DELETE FROM Relationship WHERE track_id IN (' + ','.join(['?']*len(row_to_delete)) + ');',tuple(row_to_delete))
        for row in row_to_fix:
            self.cursor.execute('UPDATE TrackList SET path=? WHERE id=?;',(self.app_path+f'/downloads/{row}.mp3',row,))

    def hard_reasseble_db(self):
        ''' Dev purpose only '''
        self.cursor.execute("DROP TABLE TrackList;")
        self.cursor.execute("DROP TABLE AlbumList;")
        self.cursor.execute("DROP TABLE Relationship;")
        self.start_db()
        if self.dev_mode:
            content = os.listdir(self.app_path+'/downloads/')
            for e in content:
                path = self.app_path+'/downloads/' + e
                if '.mp3' not in e:
                    os.remove(path)
                    continue
                
                self.cursor.execute('''
                    INSERT INTO TrackList (artist, path, song) VALUES (?, ?, ?);''',('artist', path, 'song',))
                last_row_id = self.cursor.lastrowid
                os.rename(path,self.app_path+f'/downloads/{last_row_id}.mp3')
                self.cursor.execute(''' UPDATE TrackList SET path=? WHERE id=?;''',(self.app_path+f'/downloads/{last_row_id}.mp3',last_row_id,))
                self.cursor.execute('''INSERT INTO Relationship (track_id, album_id)
                    SELECT max(id), NULL FROM TrackList;''')
                
            self.db.commit()

    def delete_all(self):
        self.app.player.stop()
        self.cursor.execute("PRAGMA foreign_keys = OFF")
        self.cursor.execute("DROP TABLE TrackList;")
        self.cursor.execute("DROP TABLE AlbumList;")
        self.cursor.execute("DROP TABLE Relationship;")
        for e in os.listdir(self.app_path+'/downloads/'):
            try:
                os.remove(self.app_path+'/downloads/' + e)
            except (PermissionError,FileNotFoundError): # file will be overrided anyway i do not care
                pass
            
        self.start_db()
        
    def album_list(self):
        ''' Return list of albums '''
        self.cursor.execute("SELECT * FROM AlbumList;")
        return self.cursor.fetchall()[::-1] + ['EOL']

    def track_list(self, key = None):
        ''' Search for album content or outer content '''
        self.cursor.execute('''SELECT * FROM TrackList WHERE id in
            (SELECT track_id FROM Relationship WHERE album_id is ?);''', (key,)
        )
        return self.cursor.fetchall()[::-1] + ['EOL']
        
    def add_album(self, name, img=None):
        ''' Create new album '''
        if img:
            self.cursor.execute("INSERT INTO AlbumList (name, img) VALUES (?, ?);",(name, img))
        else:
            self.cursor.execute("INSERT INTO AlbumList (name) VALUES (?);",(name,))

        self.db.commit()
        return self.cursor.lastrowid

    def new_track(self, artist, song):
        ''' Function to append track data to existing meta file '''
        self.cursor.execute('''
            INSERT INTO TrackList (artist, path, song, img) VALUES (?, ?, ?, ?);''',(artist, 'temp', song, 'temp',))
        
        last_row_id = self.cursor.lastrowid
        self.cursor.execute('''INSERT INTO Relationship (track_id, album_id)
            SELECT max(id), NULL FROM TrackList;''')
        return last_row_id
    
    def add_new_track(self, path, img, key):
        self.cursor.execute(''' UPDATE TrackList SET path=?,img=? WHERE id=?;''',(path,img,key,))
        self.db.commit()
  
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
            try:
                os.remove(path)
            except (PermissionError,FileNotFoundError): # if file loaded to player
                pass
            if not (img == './icons/player_back.png' or not img):
                try:
                    os.remove(img)
                except (PermissionError,FileNotFoundError):
                    pass
    
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
            try:
                os.remove(path)
            except (PermissionError,FileNotFoundError): # if file loaded to player
                pass
            
            if not (img == './icons/player_back.png' or not img):
                try:
                    os.remove(img)
                except (PermissionError,FileNotFoundError):
                    pass
        self.cursor.execute('''DELETE FROM TrackList WHERE id IN (
            SELECT id FROM TrackList WHERE id NOT IN (SELECT track_id FROM Relationship));''')
        self.db.commit()
                   
