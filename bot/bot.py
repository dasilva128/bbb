from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.keyboards import get_main_menu, get_settings_menu, get_request_buttons
from bot.database import get_setting, update_setting, get_user
from bot.settings import ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id == int(ADMIN_ID):
        keyboard = get_main_menu()
        await context.bot.send_message(
            chat_id=chat_id,
            text="خوش آمدید ادمین! لطفاً از منوی زیر انتخاب کنید:",
            reply_markup=keyboard
        )
    else:
        # بررسی عضویت در کانال اجباری
        channel_id = get_setting('channelFWD')
        if channel_id:
            member = await context.bot.get_chat_member(channel_id, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"لطفاً ابتدا در کانال {channel_id} عضو شوید!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("عضویت", url=f"https://t.me/{channel_id.lstrip('@')}")]
                    ])
                )
                return
        await context.bot.send_message(
            chat_id=chat_id,
            text="خوش آمدید! برای شروع گپ، گزینه‌ای را انتخاب کنید:",
            reply_markup=get_request_buttons()
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_chat.id

    settings_map = {
        'sticker': 'دسترسی استیکر',
        'file': 'دسترسی فایل',
        'aks': 'دسترسی عکس',
        'music': 'دسترسی موزیک',
        'film': 'دسترسی فیلم',
        'voice': 'دسترسی وویس',
        'link': 'دسترسی لینک',
        'forward': 'دسترسی فوروارد',
        'join': 'دعوت به گروه',
        'pm_forward': 'فوروارد پیام‌ها',
        'pm_resani': 'پیام‌رسانی'
    }

    if data in settings_map:
        current_status = get_setting(data)
        new_status = '✅' if current_status == '⛔️' else '⛔️'
        update_setting(data, new_status)
        await query.message.edit_reply_markup(reply_markup=get_settings_menu())
        await query.answer(f"{settings_map[data]} به {new_status} تغییر کرد.")
    elif data in ['start chat', 'end chat', 'block chat']:
        # مدیریت درخواست‌های چت
        await query.answer("در حال پردازش...")
        # منطق مربوط به چت (در صورت نیاز اضافه کنید)
    else:
        await query.answer("گزینه نامعتبر!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    # بررسی دسترسی‌ها
    if get_setting('sticker') == '⛔️' and update.message.sticker:
        await context.bot.send_message(chat_id, "ارسال استیکر غیرمجاز است!")
        return
    if get_setting('file') == '⛔️' and update.message.document:
        await context.bot.send_message(chat_id, "ارسال فایل غیرمجاز است!")
        return
    # سایر دسترسی‌ها...

    # مدیریت پیام‌های ادمین
    if update.effective_user.id == int(ADMIN_ID):
        if text == '🔧تنظیمات':
            await context.bot.send_message(
                chat_id=chat_id,
                text="تنظیمات بات:",
                reply_markup=get_settings_menu()
            )
        elif text == '↩️منوی اصلی':
            await context.bot.send_message(
                chat_id=chat_id,
                text="منوی اصلی:",
                reply_markup=get_main_menu()
            )
        # سایر دستورات ادمین...
    else:
        # منطق برای کاربران عادی
        await context.bot.send_message(chat_id, "پیام دریافت شد. لطفاً منتظر پاسخ باشید.")