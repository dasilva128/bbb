from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from bot.database import get_setting

def get_main_menu():
    on_off = get_setting('on_off') == 'true'
    buttons = [
        ['🔯غیر فعال کردن حالت ادمین'],
        ['⤴️پیام همگانی', '🈂فوروارد همگانی'],
        ['♓همگانی و عکس', '⏫همگانی و فایل'],
        ['🉑پاسخ سریع', '🔲مدیریت دکمه ها'],
        ['👱ادمین ها', '📫پروفایل'],
        ['❇️متن پیشفرض', '🆕متن استارت'],
        ['🔴ریست کردن', '🆙ارتقا ربات'],
        ['📮پیام به کاربر', '🔧تنظیمات'],
        ['آمار', '☎️کانتکت'],
        ['📥دانلودر', '📤آپلود داخلی'],
        ['⛔️خاموش کردن بات' if on_off else '✴️روشن کردن بات', '📣تنظیم چنل'],
        ['⚠️راهنما', '📂پشتیبان گیری'],
        ['🔒قفل ربات', '♦حساب کاربری ربات']
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

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