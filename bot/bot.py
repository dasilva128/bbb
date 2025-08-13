import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from bot.keyboards import (
    get_main_menu, get_settings_menu, get_request_buttons, get_button_management_menu,
    get_system_button_management_menu, get_remove_custom_button_menu, get_remove_system_button_menu,
    get_move_custom_button_menu, get_move_direction_menu, get_toggle_system_button_menu, get_position_menu
)
from bot.database import (
    get_setting, update_setting, get_user, add_custom_button, remove_custom_button,
    move_custom_button, add_system_button, remove_system_button, toggle_system_button,
    get_custom_buttons, get_system_buttons
)
from bot.settings import ADMIN_ID

# مراحل مکالمه برای دکمه‌های سفارشی
ADD_CUSTOM_TEXT, ADD_CUSTOM_POSITION, ADD_CUSTOM_CONTENT = range(3)
# مراحل مکالمه برای دکمه‌های سیستمی
ADD_SYSTEM_TEXT, ADD_SYSTEM_POSITION, ADD_SYSTEM_CONTENT = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id == int(ADMIN_ID):
        keyboard = get_main_menu(is_admin=True)
        await context.bot.send_message(
            chat_id=chat_id,
            text="خوش آمدید ادمین! لطفاً از منوی زیر انتخاب کنید:",
            reply_markup=keyboard
        )
    else:
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
    elif data.startswith('remove_custom_'):
        button_text = data[len('remove_custom_'):]
        remove_custom_button(button_text)
        await query.message.edit_reply_markup(reply_markup=get_remove_custom_button_menu())
        await query.answer(f"دکمه سفارشی '{button_text}' حذف شد.")
    elif data.startswith('remove_system_'):
        button_text = data[len('remove_system_'):]
        remove_system_button(button_text)
        await query.message.edit_reply_markup(reply_markup=get_remove_system_button_menu())
        await query.answer(f"دکمه سیستمی '{button_text}' حذف شد.")
    elif data.startswith('toggle_system_'):
        button_text = data[len('toggle_system_'):]
        new_status = toggle_system_button(button_text)
        await query.message.edit_reply_markup(reply_markup=get_toggle_system_button_menu())
        await query.answer(f"دکمه سیستمی '{button_text}' {'فعال' if new_status else 'غیرفعال'} شد.")
    elif data.startswith('move_select_'):
        button_text = data[len('move_select_'):]
        context.user_data['move_button_text'] = button_text
        await query.message.edit_text(
            f"جهت جابه‌جایی دکمه '{button_text}' را انتخاب کنید:",
            reply_markup=get_move_direction_menu(button_text)
        )
        await query.answer()
    elif data.startswith('move_up_'):
        button_text = data[len('move_up_'):]
        if move_custom_button(button_text, 'up'):
            await query.message.edit_reply_markup(reply_markup=get_move_custom_button_menu())
            await query.answer(f"دکمه '{button_text}' به بالا منتقل شد.")
        else:
            await query.answer("امکان جابه‌جایی به بالا وجود ندارد!")
    elif data.startswith('move_down_'):
        button_text = data[len('move_down_'):]
        if move_custom_button(button_text, 'down'):
            await query.message.edit_reply_markup(reply_markup=get_move_custom_button_menu())
            await query.answer(f"دکمه '{button_text}' به پایین منتقل شد.")
        else:
            await query.answer("امکان جابه‌جایی به پایین وجود ندارد!")
    elif data == 'back_to_management':
        await query.message.edit_text("مدیریت دکمه‌ها:", reply_markup=get_button_management_menu())
        await query.answer()
    elif data == 'back_to_system_management':
        await query.message.edit_text("مدیریت دکمه‌های سیستمی:", reply_markup=get_system_button_management_menu())
        await query.answer()
    elif data == 'back_to_move_menu':
        await query.message.edit_text("دکمه‌ای را برای جابه‌جایی انتخاب کنید:", reply_markup=get_move_custom_button_menu())
        await query.answer()
    elif data in ['position_top', 'position_bottom']:
        context.user_data['position'] = 'top' if data == 'position_top' else 'bottom'
        context.user_data['stage'] = 'content'
        content_type = context.user_data.get('content_type', 'custom')
        await query.message.edit_text(
            "لطفاً محتوای دکمه (متن، فایل، فوروارد یا آدرس RSS) را ارسال کنید:",
            reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
        )
        await query.answer()
        return ADD_CUSTOM_CONTENT if content_type == 'custom' else ADD_SYSTEM_CONTENT
    elif data == 'cancel':
        context.user_data['adding_button'] = False
        context.user_data['stage'] = None
        context.user_data['content_type'] = None
        await query.message.edit_text("عملیات لغو شد.", reply_markup=get_button_management_menu())
        await query.answer()
        return ConversationHandler.END
    elif data in ['start chat', 'end chat', 'block chat']:
        await query.answer("در حال پردازش...")
        # منطق مربوط به چت (در صورت نیاز اضافه کنید)
    else:
        await query.answer("گزینه نامعتبر!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    user_id = update.effective_user.id

    # مدیریت مکالمه برای دکمه‌های سفارشی
    if context.user_data.get('adding_button') and context.user_data.get('content_type') == 'custom':
        if context.user_data.get('stage') == 'text':
            if any(button['text'] == text for button in get_custom_buttons()):
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="دکمه‌ای با این نام وجود دارد. لطفاً نام دیگری وارد کنید:",
                    reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                )
                return ADD_CUSTOM_TEXT
            context.user_data['button_text'] = text
            context.user_data['stage'] = 'position'
            await context.bot.send_message(
                chat_id=chat_id,
                text="می‌خواهید دکمه در کجا اضافه شود؟",
                reply_markup=get_position_menu()
            )
            return ADD_CUSTOM_POSITION
        elif context.user_data.get('stage') == 'content':
            file_id = None
            file_type = None
            caption = update.message.caption
            position = context.user_data.get('position', 'bottom')
            if update.message.audio:
                file_id = update.message.audio.file_id
                file_type = 'audio'
            elif update.message.video:
                file_id = update.message.video.file_id
                file_type = 'video'
            elif update.message.document:
                file_id = update.message.document.file_id
                file_type = 'document'
            elif update.message.photo:
                file_id = update.message.photo[-1].file_id  # بالاترین کیفیت عکس
                file_type = 'photo'
            elif update.message.text:
                try:
                    response = requests.get(f"http://api.norbert-team.ir/feedkhan/?post=10&rss={text}").text
                    if response:
                        file_id = text
                        file_type = 'rss'
                    else:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text="آدرس RSS نامعتبر است. لطفاً آدرس معتبر یا محتوای دیگری ارسال کنید:",
                            reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                        )
                        return ADD_CUSTOM_CONTENT
                except:
                    file_id = text
                    file_type = 'text'
            elif update.message.forward_from or update.message.forward_from_chat:
                file_id = update.message.message_id
                file_type = 'forward'
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="لطفاً متن، فایل (صوتی، تصویری، سند، عکس)، فوروارد یا آدرس RSS معتبر ارسال کنید:",
                    reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                )
                return ADD_CUSTOM_CONTENT

            add_custom_button(context.user_data['button_text'], file_id, file_type, caption, position)
            context.user_data['adding_button'] = False
            context.user_data['stage'] = None
            context.user_data['content_type'] = None
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"دکمه سفارشی '{context.user_data['button_text']}' اضافه شد.",
                reply_markup=get_main_menu(is_admin=True)
            )
            return ConversationHandler.END

    # مدیریت مکالمه برای دکمه‌های سیستمی
    if context.user_data.get('adding_button') and context.user_data.get('content_type') == 'system':
        if context.user_data.get('stage') == 'text':
            if any(button['text'] == text for button in get_system_buttons()):
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="دکمه‌ای با این نام وجود دارد. لطفاً نام دیگری وارد کنید:",
                    reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                )
                return ADD_SYSTEM_TEXT
            context.user_data['button_text'] = text
            context.user_data['stage'] = 'position'
            await context.bot.send_message(
                chat_id=chat_id,
                text="می‌خواهید دکمه در کجا اضافه شود؟",
                reply_markup=get_position_menu()
            )
            return ADD_SYSTEM_POSITION
        elif context.user_data.get('stage') == 'content':
            file_id = None
            file_type = None
            caption = update.message.caption
            position = context.user_data.get('position', 'bottom')
            if update.message.audio:
                file_id = update.message.audio.file_id
                file_type = 'audio'
            elif update.message.video:
                file_id = update.message.video.file_id
                file_type = 'video'
            elif update.message.document:
                file_id = update.message.document.file_id
                file_type = 'document'
            elif update.message.photo:
                file_id = update.message.photo[-1].file_id
                file_type = 'photo'
            elif update.message.text:
                try:
                    response = requests.get(f"http://api.norbert-team.ir/feedkhan/?post=10&rss={text}").text
                    if response:
                        file_id = text
                        file_type = 'rss'
                    else:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text="آدرس RSS نامعتبر است. لطفاً آدرس معتبر یا محتوای دیگری ارسال کنید:",
                            reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                        )
                        return ADD_SYSTEM_CONTENT
                except:
                    file_id = text
                    file_type = 'text'
            elif update.message.forward_from or update.message.forward_from_chat:
                file_id = update.message.message_id
                file_type = 'forward'
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="لطفاً متن، فایل (صوتی، تصویری، سند، عکس)، فوروارد یا آدرس RSS معتبر ارسال کنید:",
                    reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                )
                return ADD_SYSTEM_CONTENT

            add_system_button(context.user_data['button_text'], file_id, file_type, caption, position)
            context.user_data['adding_button'] = False
            context.user_data['stage'] = None
            context.user_data['content_type'] = None
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"دکمه سیستمی '{context.user_data['button_text']}' اضافه شد.",
                reply_markup=get_main_menu(is_admin=True)
            )
            return ConversationHandler.END

    # بررسی دسترسی‌ها
    if get_setting('sticker') == '⛔️' and update.message.sticker:
        await context.bot.send_message(chat_id, "ارسال استیکر غیرمجاز است!")
        return
    if get_setting('file') == '⛔️' and update.message.document:
        await context.bot.send_message(chat_id, "ارسال فایل غیرمجاز است!")
        return
    if get_setting('aks') == '⛔️' and update.message.photo:
        await context.bot.send_message(chat_id, "ارسال عکس غیرمجاز است!")
        return
    if get_setting('music') == '⛔️' and update.message.audio:
        await context.bot.send_message(chat_id, "ارسال موزیک غیرمجاز است!")
        return
    if get_setting('film') == '⛔️' and (update.message.video or update.message.animation):
        await context.bot.send_message(chat_id, "ارسال فیلم یا گیف غیرمجاز است!")
        return
    if get_setting('voice') == '⛔️' and update.message.voice:
        await context.bot.send_message(chat_id, "ارسال وویس غیرمجاز است!")
        return

    # بررسی کلیک روی دکمه‌های سفارشی
    buttons = get_custom_buttons()
    for button in buttons:
        if text == button['text'] and button['file_id']:
            if button['file_type'] == 'audio':
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=button['file_id'],
                    caption=button.get('caption'),
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))
                )
            elif button['file_type'] == 'video':
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=button['file_id'],
                    caption=button.get('caption'),
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))
                )
            elif button['file_type'] == 'document':
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=button['file_id'],
                    caption=button.get('caption'),
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))
                )
            elif button['file_type'] == 'photo':
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=button['file_id'],
                    caption=button.get('caption'),
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))
                )
            elif button['file_type'] == 'text':
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=button['file_id'],
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))
                )
            elif button['file_type'] == 'rss':
                response = requests.get(f"http://api.norbert-team.ir/feedkhan/?post=10&rss={button['file_id']}").text
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=response or "محتوای RSS در دسترس نیست.",
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))
                )
            elif button['file_type'] == 'forward':
                await context.bot.forward_message(
                    chat_id=chat_id,
                    from_chat_id=chat_id,
                    message_id=button['file_id']
                )
            return

    # بررسی کلیک روی دکمه‌های سیستمی (فقط برای ادمین)
    if user_id == int(ADMIN_ID):
        system_buttons = get_system_buttons()
        for button in system_buttons:
            if text == button['text']:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"دکمه سیستمی '{text}' انتخاب شد. این دکمه {'فعال' if button['is_active'] else 'غیرفعال'} است.",
                    reply_markup=get_main_menu(is_admin=True)
                )
                return

    # مدیریت پیام‌های ادمین
    if user_id == int(ADMIN_ID):
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
                reply_markup=get_main_menu(is_admin=True)
            )
        elif text == '🔲مدیریت دکمه‌ها':
            await context.bot.send_message(
                chat_id=chat_id,
                text="مدیریت دکمه‌ها:",
                reply_markup=get_button_management_menu()
            )
        elif text == '⏸دکمه‌های سیستمی':
            await context.bot.send_message(
                chat_id=chat_id,
                text="مدیریت دکمه‌های سیستمی:",
                reply_markup=get_system_button_management_menu()
            )
        elif text == '⏸اضافه کردن دکمه سفارشی':
            context.user_data['adding_button'] = True
            context.user_data['stage'] = 'text'
            context.user_data['content_type'] = 'custom'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً متن دکمه جدید را وارد کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return ADD_CUSTOM_TEXT
        elif text == '⏸حذف دکمه سفارشی':
            if not get_custom_buttons():
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="هیچ دکمه سفارشی برای حذف وجود ندارد!",
                    reply_markup=get_button_management_menu()
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="دکمه‌ای را برای حذف انتخاب کنید:",
                    reply_markup=get_remove_custom_button_menu()
                )
        elif text == '⏸جابه‌جایی دکمه‌های سفارشی':
            if not get_custom_buttons():
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="هیچ دکمه سفارشی برای جابه‌جایی وجود ندارد!",
                    reply_markup=get_button_management_menu()
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="دکمه‌ای را برای جابه‌جایی انتخاب کنید:",
                    reply_markup=get_move_custom_button_menu()
                )
        elif text == '⏸اضافه کردن دکمه سیستمی':
            context.user_data['adding_button'] = True
            context.user_data['stage'] = 'text'
            context.user_data['content_type'] = 'system'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً متن دکمه سیستمی جدید را وارد کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return ADD_SYSTEM_TEXT
        elif text == '⏸حذف دکمه سیستمی':
            if not get_system_buttons():
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="هیچ دکمه سیستمی برای حذف وجود ندارد!",
                    reply_markup=get_system_button_management_menu()
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="دکمه سیستمی را برای حذف انتخاب کنید:",
                    reply_markup=get_remove_system_button_menu()
                )
        elif text == '⏸فعال/غیرفعال کردن دکمه‌های سیستمی':
            if not get_system_buttons():
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="هیچ دکمه سیستمی برای مدیریت وجود ندارد!",
                    reply_markup=get_system_button_management_menu()
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="دکمه سیستمی را برای فعال/غیرفعال کردن انتخاب کنید:",
                    reply_markup=get_toggle_system_button_menu()
                )
        elif text == '↩️لغو':
            context.user_data['adding_button'] = False
            context.user_data['stage'] = None
            context.user_data['content_type'] = None
            await context.bot.send_message(
                chat_id=chat_id,
                text="عملیات لغو شد.",
                reply_markup=get_main_menu(is_admin=True)
            )
            return ConversationHandler.END
        else:
            await context.bot.send_message(chat_id, "دستور نامعتبر! لطفاً از منو انتخاب کنید.")
    else:
        # فوروارد پیام‌های کاربر به ادمین (اگر تنظیمات اجازه دهد)
        if get_setting('pm_forward') == '✅':
            await context.bot.forward_message(
                chat_id=int(ADMIN_ID),
                from_chat_id=chat_id,
                message_id=update.message.message_id
            )
        await context.bot.send_message(chat_id, "پیام دریافت شد. لطفاً منتظر پاسخ باشید.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['adding_button'] = False
    context.user_data['stage'] = None
    context.user_data['content_type'] = None
    await update.message.reply_text("عملیات لغو شد.", reply_markup=get_main_menu(is_admin=update.effective_user.id == int(ADMIN_ID)))
    return ConversationHandler.END