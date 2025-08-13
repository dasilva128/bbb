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
    # مقداردهی اولیه دکمه‌های سفارشی (خالی)
    if not db.custom_buttons.find_one():
        db.custom_buttons.insert_one({
            'text': 'دکمه نمونه 🌟',
            'order': 1,
            'file_id': None,
            'file_type': None
        })
    # مقداردهی اولیه دکمه‌های سیستمی (خالی)
    if not db.system_buttons.find_one():
        db.system_buttons.insert_one({
            'text': 'دکمه سیستمی نمونه 🔧',
            'order': 1,
            'file_id': None,
            'file_type': None,
            'caption': None,
            'is_active': False
        })

def get_setting(key):
    settings = db.settings.find_one()
    return settings.get(key, '✅')

def update_setting(key, value):
    db.settings.update_one({}, {'$set': {key: value}})

def get_user(user_id):
    return db.users.find_one({'user_id': user_id})

def update_user(user_id, data):
    db.users.update_one({'user_id': user_id}, {'$set': data}, upsert=True)

# مدیریت دکمه‌های سفارشی
def add_custom_button(text, file_id=None, file_type=None, caption=None, position='bottom'):
    last_button = db.custom_buttons.find_one(sort=[('order', -1)])
    order = last_button['order'] + 1 if last_button else 1
    if position == 'top':
        db.custom_buttons.update_many({}, {'$inc': {'order': 1}})
        order = 1
    db.custom_buttons.insert_one({
        'text': text,
        'order': order,
        'file_id': file_id,
        'file_type': file_type,
        'caption': caption
    })

def remove_custom_button(text):
    db.custom_buttons.delete_one({'text': text})

def get_custom_buttons():
    return list(db.custom_buttons.find().sort('order', 1))

def move_custom_button(text, direction):
    button = db.custom_buttons.find_one({'text': text})
    if not button:
        return False
    current_order = button['order']
    buttons = get_custom_buttons()
    if direction == 'up' and current_order > 1:
        prev_button = db.custom_buttons.find_one({'order': current_order - 1})
        if prev_button:
            db.custom_buttons.update_one({'text': text}, {'$set': {'order': current_order - 1}})
            db.custom_buttons.update_one({'text': prev_button['text']}, {'$set': {'order': current_order}})
    elif direction == 'down' and current_order < len(buttons):
        next_button = db.custom_buttons.find_one({'order': current_order + 1})
        if next_button:
            db.custom_buttons.update_one({'text': text}, {'$set': {'order': current_order + 1}})
            db.custom_buttons.update_one({'text': next_button['text']}, {'$set': {'order': current_order}})
    return True

# مدیریت دکمه‌های سیستمی
def add_system_button(text, file_id=None, file_type=None, caption=None, position='bottom'):
    last_button = db.system_buttons.find_one(sort=[('order', -1)])
    order = last_button['order'] + 1 if last_button else 1
    if position == 'top':
        db.system_buttons.update_many({}, {'$inc': {'order': 1}})
        order = 1
    db.system_buttons.insert_one({
        'text': text,
        'order': order,
        'file_id': file_id,
        'file_type': file_type,
        'caption': caption,
        'is_active': False
    })

def remove_system_button(text):
    db.system_buttons.delete_one({'text': text})

def toggle_system_button(text):
    button = db.system_buttons.find_one({'text': text})
    if button:
        new_status = not button.get('is_active', False)
        db.system_buttons.update_one({'text': text}, {'$set': {'is_active': new_status}})
        return new_status
    return False

def get_system_buttons():
    return list(db.system_buttons.find().sort('order', 1))