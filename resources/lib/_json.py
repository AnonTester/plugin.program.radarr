import os
import io
import json
import xbmc, xbmcvfs, xbmcaddon

addonID = "plugin.program.radarr"
addon = xbmcaddon.Addon(id=addonID)
dir_userdata = xbmc.translatePath(addon.getAddonInfo('profile'))
dir_db = os.path.join(dir_userdata, 'db')
dir_movies = os.path.join(dir_db, 'movies')
#dir_seasons = os.path.join(dir_movie, 'seasons')
#dir_episodes = os.path.join(dir_movie, 'episodes')
#file_movie = os.path.join(dir_db, 'movie.json')

log_msg = addonID + ' - _json_lib -'


def read_json(db_file):
    xbmc.log(log_msg + '!READ JSON!', 1)
    xbmc.log(log_msg + 'File: '+db_file, 1)
    if xbmcvfs.exists(db_file):
        xbmc.log(log_msg+'File Exists', 1)
        with open(db_file) as f:
            try:
                data = json.load(f)
                f.close()
            except ValueError:
                data = {}
    else:
        xbmc.log(log_msg + 'File Does Not Exist', 1)
        data = {}
    return data


def write_json(db_file, data):
    data_old = ''
    if check_file(db_file): # check if there is new data
        try:
            data_old = read_json(db_file)
        except:
            data_old = ''
    if data_old != data:
        xbmc.log(log_msg + '!WRITE JSON!', 1)
        xbmc.log(log_msg + 'File: ' + db_file, 1)
        db_file_dir = os.path.dirname(db_file)  # get path from filepath
        check_dir(db_file_dir)  # check if folder exists
        with io.open(db_file, 'w', encoding='utf-8') as f:
            f.write(str(json.dumps(data, ensure_ascii=False)))
            f.close()
    else:
        #xbmc.log('SKIPSKIP')
        pass


def get_appended_path(dir, item):
    return os.path.join(dir, item)

def check_dir(dir):
    if not xbmcvfs.exists(dir):
        xbmcvfs.mkdir(dir)

def check_dir_userdata():
    if not xbmcvfs.exists(dir_userdata):
        xbmcvfs.mkdir(dir_userdata)

def check_dir_db():
    check_dir_userdata()
    if not xbmcvfs.exists(dir_db):
        xbmcvfs.mkdir(dir_db)

def check_dir_episodes():
    check_dir_userdata()
    check_dir_db()
    if not xbmcvfs.exists(dir_episodes):
        xbmcvfs.mkdir(dir_episodes)

def check_file(file_db):
    if xbmcvfs.exists(file_db):
        return True
