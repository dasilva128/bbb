from pymongo import MongoClient

client = None
db = None

def init_db(mongo_uri, db_name):
    global client, db
    client = MongoClient(mongo_uri)
    db = client[db_name]
    # تنظیمات پیش‌فرض
    if not db.settings.find_one():
        default_settings = {
            'sticker': '✅',
            'file': '✅',
            'aks': '✅',
            'music': '✅',
            'film': '✅',
            'voice': '✅',
            'link': '✅',
            'forward': '✅',
            'join': '✅',
            'pm_forward': '✅',
            'pm_resani': '✅',
            'on_off': 'true',
            'channelFWD': ''
        }
        db.settings.insert_one(default_settings)

def get_setting(key):
    settings = db.settings.find_one()
    return settings.get(key, '✅')

def update_setting(key, value):
    db.settings.update_one({}, {'$set': {key: value}})

def get_user(user_id):
    return db.users.find_one({'user_id': user_id})

def update_user(user_id, data):
    db.users.update_one({'user_id': user_id}, {'$set': data}, upsert=True)