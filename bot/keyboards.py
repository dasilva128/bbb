from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from bot.database import get_setting, get_custom_buttons, get_system_buttons

def get_main_menu(is_admin=False):
    on_off = get_setting('on_off') == 'true'
    # دکمه‌های سفارشی
    custom_buttons = [[{'text': button['text']}] for button in get_custom_buttons()]
    # دکمه‌های ثابت
    fixed_buttons = [
        ['🔯غیر فعال کردن حالت ادمین'],
        ['⤴️پیام همگانی', '🈂فوروارد همگانی'],
        ['♓همگانی و عکس', '⏫همگانی و فایل'],
        ['🔲مدیریت دکمه ها'],
        ['👱ادمین ها'],
        ['❇️متن پیشفرض', '🆕متن استارت'],
        ['🔴ریست کردن'],
        ['📮پیام به کاربر', '🔧تنظیمات'],
        ['آمار'],
        ['📤آپلود داخلی'],
        ['⛔️خاموش کردن بات' if on_off else '✴️روشن کردن بات', '📣تنظیم چنل'],
        ['⚠️راهنما', '📂پشتیبان گیری'],
        ['🔒قفل ربات', '♦حساب کاربری ربات']
    ]
    # اضافه کردن دکمه‌های سیستمی فقط برای ادمین
    if is_admin:
        system_buttons = [[{'text': button['text']}] for button in get_system_buttons()]
        return ReplyKeyboardMarkup(system_buttons + custom_buttons + fixed_buttons, resize_keyboard=True)
    return ReplyKeyboardMarkup(custom_buttons + fixed_buttons, resize_keyboard=True)

def get_settings_menu():
    settings = {
        'sticker': get_setting('sticker'),
        'file': get_setting('file'),
        'aks': get_setting('aks'),
        'music': get_setting('music'),
        'film': get_setting('film'),
        'voice': get_setting('voice'),
        'link': get_setting('link'),
        'forward': get_setting('forward'),
        'join': get_setting('join'),
        'pm_forward': get_setting('pm_forward'),
        'pm_resani': get_setting('pm_resani')
    }
    buttons = [
        [InlineKeyboardButton(f"دسترسی استیکر {settings['sticker']}", callback_data="sticker")],
        [InlineKeyboardButton(f"دسترسی فایل {settings['file']}", callback_data="file")],
        [InlineKeyboardButton(f"دسترسی عکس {settings['aks']}", callback_data="aks")],
        [InlineKeyboardButton(f"دسترسی موزیک {settings['music']}", callback_data="music")],
        [InlineKeyboardButton(f"دسترسی فیلم {settings['film']}", callback_data="film")],
        [InlineKeyboardButton(f"دسترسی وویس {settings['voice']}", callback_data="voice")],
        [InlineKeyboardButton(f"دسترسی لینک {settings['link']}", callback_data="link")],
        [InlineKeyboardButton(f"دسترسی فوروارد {settings['forward']}", callback_data="forward")],
        [InlineKeyboardButton(f"دعوت به گروه {settings['join']}", callback_data="join")],
        [InlineKeyboardButton(f"فوروارد پیام‌ها {settings['pm_forward']}", callback_data="pm_forward")],
        [InlineKeyboardButton(f"پیام‌رسانی {settings['pm_resani']}", callback_data="pm_resani")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_request_buttons():
    buttons = [
        [InlineKeyboardButton("✅ قبول", callback_data="start chat"),
         InlineKeyboardButton("❎ رد", callback_data="end chat")],
        [InlineKeyboardButton("🚫 بلاک", callback_data="block chat")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_button_management_menu():
    buttons = [
        ['↩️منوی اصلی'],
        ['⏸دکمه‌های سیستمی'],
        ['⏸اضافه کردن دکمه سفارشی', '⏸حذف دکمه سفارشی'],
        ['⏸جابه‌جایی دکمه‌های سفارشی']
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_system_button_management_menu():
    buttons = [
        ['↩️منوی اصلی'],
        ['⏸اضافه کردن دکمه سیستمی', '⏸حذف دکمه سیستمی'],
        ['⏸فعال/غیرفعال کردن دکمه‌های سیستمی']
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_remove_custom_button_menu():
    buttons = [[InlineKeyboardButton(button['text'], callback_data=f"remove_custom_{button['text']}")] for button in get_custom_buttons()]
    buttons.append([InlineKeyboardButton("↩️بازگشت", callback_data="back_to_management")])
    return InlineKeyboardMarkup(buttons)

def get_remove_system_button_menu():
    buttons = [[InlineKeyboardButton(button['text'], callback_data=f"remove_system_{button['text']}")] for button in get_system_buttons()]
    buttons.append([InlineKeyboardButton("↩️بازگشت", callback_data="back_to_system_management")])
    return InlineKeyboardMarkup(buttons)

def get_move_custom_button_menu():
    buttons = [
        [InlineKeyboardButton(button['text'], callback_data=f"move_select_{button['text']}")]
        for button in get_custom_buttons()
    ]
    buttons.append([InlineKeyboardButton("↩️بازگشت", callback_data="back_to_management")])
    return InlineKeyboardMarkup(buttons)

def get_move_direction_menu(button_text):
    buttons = [
        [InlineKeyboardButton("🔼بالا", callback_data=f"move_up_{button_text}"),
         InlineKeyboardButton("🔽پایین", callback_data=f"move_down_{button_text}")],
        [InlineKeyboardButton("↩️بازگشت", callback_data="back_to_move_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_toggle_system_button_menu():
    buttons = [
        [InlineKeyboardButton(
            f"{button['text']} {'✅' if button.get('is_active', False) else '⛔️'}",
            callback_data=f"toggle_system_{button['text']}"
        )] for button in get_system_buttons()
    ]
    buttons.append([InlineKeyboardButton("↩️بازگشت", callback_data="back_to_system_management")])
    return InlineKeyboardMarkup(buttons)

def get_position_menu():
    buttons = [
        [InlineKeyboardButton("🔼بالا", callback_data="position_top"),
         InlineKeyboardButton("🔽پایین", callback_data="position_bottom")],
        [InlineKeyboardButton("↩️لغو", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(buttons)