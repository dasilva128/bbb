import json
import zipfile
from io import BytesIO
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.keyboards import (
    get_main_menu, get_settings_menu, get_request_buttons, get_button_management_menu,
    get_system_button_management_menu, get_remove_custom_button_menu, get_remove_system_button_menu,
    get_move_custom_button_menu, get_move_direction_menu, get_toggle_system_button_menu, get_position_menu
)
from bot.database import (
    get_setting, update_setting, get_user, update_user, add_custom_button, remove_custom_button,
    move_custom_button, add_system_button, remove_system_button, toggle_system_button,
    get_custom_buttons, get_system_buttons
)
from bot.settings import ADMIN_ID

# مراحل مکالمه
ADD_CUSTOM_TEXT, ADD_CUSTOM_POSITION, ADD_CUSTOM_CONTENT = range(3)
ADD_SYSTEM_TEXT, ADD_SYSTEM_POSITION, ADD_SYSTEM_CONTENT = range(3, 6)
SEND_MESSAGE_TO_USER, SEND_MESSAGE_CONTENT = range(6, 8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    update_user(user_id, {'user_id': user_id})

    if user_id == int(ADMIN_ID):
        keyboard, inline_keyboard = get_main_menu(is_admin=True)
        await context.bot.send_message(
            chat_id=chat_id,
            text="خوش آمدید ادمین! لطفاً از منوی زیر انتخاب کنید:",
            reply_markup=keyboard,
            reply_to_message_id=update.message.message_id
        )
        if inline_keyboard:
            await context.bot.send_message(
                chat_id=chat_id,
                text="گزینه‌های مدیریتی:",
                reply_markup=inline_keyboard
            )
    else:
        channel_id = get_setting('channelFWD')
        if channel_id:
            try:
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
            except:
                await context.bot.send_message(chat_id=chat_id, text="خطا در بررسی عضویت کانال!")
                return
        keyboard, inline_keyboard = get_main_menu(is_admin=False)
        await context.bot.send_message(
            chat_id=chat_id,
            text="خوش آمدید! برای شروع گپ، گزینه‌ای را انتخاب کنید:",
            reply_markup=keyboard
        )
        if inline_keyboard:
            await context.bot.send_message(
                chat_id=chat_id,
                text="گزینه‌های بیشتر:",
                reply_markup=inline_keyboard
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
    elif data == 'settings':
        await query.message.edit_text("تنظیمات بات:", reply_markup=get_settings_menu())
        await query.answer()
    elif data == 'button_management':
        await query.message.edit_text("مدیریت دکمه‌ها:", reply_markup=get_button_management_menu())
        await query.answer()
    elif data == 'send_message_to_user':
        context.user_data['stage'] = 'send_message_to_user'
        await query.message.edit_text(
            "لطفاً آیدی کاربر یا پیام فوروارد را ارسال کنید:",
            reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
        )
        await query.answer()
        return SEND_MESSAGE_TO_USER
    elif data == 'backup':
        await backup_data(chat_id, context)
        await query.answer("بکاپ‌گیری انجام شد.")
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
            "لطفاً محتوای دکمه (متن، فایل، عکس، صوت، ویدئو یا فوروارد) را ارسال کنید:",
            reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
        )
        await query.answer()
        return ADD_CUSTOM_CONTENT if content_type == 'custom' else ADD_SYSTEM_CONTENT
    elif data == 'cancel':
        context.user_data.clear()
        await query.message.edit_text("عملیات لغو شد.", reply_markup=get_button_management_menu())
        await query.answer()
        return ConversationHandler.END
    elif data in ['start chat', 'end chat', 'block chat']:
        await query.answer("در حال پردازش...")
        # منطق چت در صورت نیاز
    else:
        await query.answer("گزینه نامعتبر!")

async def backup_data(chat_id, context):
    backup_data = {
        'settings': list(db.settings.find()),
        'custom_buttons': list(db.custom_buttons.find()),
        'system_buttons': list(db.system_buttons.find()),
        'users': list(db.users.find())
    }
    json_data = json.dumps(backup_data, ensure_ascii=False).encode('utf-8')
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('backup.json', json_data)
    zip_buffer.seek(0)
    await context.bot.send_document(
        chat_id=chat_id,
        document=zip_buffer,
        filename='backup.zip',
        reply_markup=get_main_menu(is_admin=True)[0]
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    user_id = update.effective_user.id
    update_user(user_id, {'user_id': user_id})

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
                file_id = update.message.photo[-1].file_id
                file_type = 'photo'
            elif update.message.text:
                file_id = text
                file_type = 'text'
            elif update.message.forward_from or update.message.forward_from_chat:
                file_id = update.message.message_id
                file_type = 'forward'
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="لطفاً متن، فایل، عکس، صوت، ویدئو یا فوروارد ارسال کنید:",
                    reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                )
                return ADD_CUSTOM_CONTENT

            add_custom_button(context.user_data['button_text'], file_id, file_type, caption, position)
            context.user_data.clear()
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"دکمه سفارشی '{context.user_data['button_text']}' اضافه شد.",
                reply_markup=get_main_menu(is_admin=True)[0]
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
                file_id = text
                file_type = 'text'
            elif update.message.forward_from or update.message.forward_from_chat:
                file_id = update.message.message_id
                file_type = 'forward'
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="لطفاً متن، فایل، عکس، صوت، ویدئو یا فوروارد ارسال کنید:",
                    reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                )
                return ADD_SYSTEM_CONTENT

            add_system_button(context.user_data['button_text'], file_id, file_type, caption, position)
            context.user_data.clear()
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"دکمه سیستمی '{context.user_data['button_text']}' اضافه شد.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
            return ConversationHandler.END

    # مدیریت ارسال پیام به کاربر خاص
    if context.user_data.get('stage') == 'send_message_to_user':
        try:
            context.user_data['target_user_id'] = int(text)
            context.user_data['stage'] = 'send_message_content'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً پیام (متن، فایل، عکس، صوت، ویدئو یا فوروارد) را ارسال کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_CONTENT
        except ValueError:
            await context.bot.send_message(
                chat_id=chat_id,
                text="آیدی کاربر نامعتبر است. لطفاً یک آیدی عددی معتبر وارد کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_TO_USER
    elif context.user_data.get('stage') == 'send_message_content':
        target_user_id = context.user_data.get('target_user_id')
        try:
            if update.message.text:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=update.message.text,
                    reply_markup=get_main_menu(is_admin=False)[0]
                )
            elif update.message.photo:
                await context.bot.send_photo(
                    chat_id=target_user_id,
                    photo=update.message.photo[-1].file_id,
                    caption=update.message.caption,
                    reply_markup=get_main_menu(is_admin=False)[0]
                )
            elif update.message.audio:
                await context.bot.send_audio(
                    chat_id=target_user_id,
                    audio=update.message.audio.file_id,
                    caption=update.message.caption,
                    reply_markup=get_main_menu(is_admin=False)[0]
                )
            elif update.message.video:
                await context.bot.send_video(
                    chat_id=target_user_id,
                    video=update.message.video.file_id,
                    caption=update.message.caption,
                    reply_markup=get_main_menu(is_admin=False)[0]
                )
            elif update.message.document:
                await context.bot.send_document(
                    chat_id=target_user_id,
                    document=update.message.document.file_id,
                    caption=update.message.caption,
                    reply_markup=get_main_menu(is_admin=False)[0]
                )
            elif update.message.forward_from or update.message.forward_from_chat:
                await context.bot.forward_message(
                    chat_id=target_user_id,
                    from_chat_id=chat_id,
                    message_id=update.message.message_id
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="لطفاً متن، فایل، عکس، صوت، ویدئو یا فوروارد ارسال کنید:",
                    reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
                )
                return SEND_MESSAGE_CONTENT
            context.user_data.clear()
            await context.bot.send_message(
                chat_id=chat_id,
                text="پیام با موفقیت ارسال شد.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
            return ConversationHandler.END
        except Exception as e:
            context.user_data.clear()
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"خطا در ارسال پیام: {str(e)}",
                reply_markup=get_main_menu(is_admin=True)[0]
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
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))[0]
                )
            elif button['file_type'] == 'video':
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=button['file_id'],
                    caption=button.get('caption'),
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))[0]
                )
            elif button['file_type'] == 'document':
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=button['file_id'],
                    caption=button.get('caption'),
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))[0]
                )
            elif button['file_type'] == 'photo':
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=button['file_id'],
                    caption=button.get('caption'),
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))[0]
                )
            elif button['file_type'] == 'text':
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=button['file_id'],
                    reply_markup=get_main_menu(is_admin=user_id == int(ADMIN_ID))[0]
                )
            elif button['file_type'] == 'forward':
                await context.bot.forward_message(
                    chat_id=chat_id,
                    from_chat_id=chat_id,
                    message_id=button['file_id']
                )
            return

    # بررسی کلیک روی دکمه‌های سیستمی
    if user_id == int(ADMIN_ID):
        system_buttons = get_system_buttons()
        for button in system_buttons:
            if text == button['text'] and button.get('is_active', False):
                if button['file_type'] == 'audio':
                    await context.bot.send_audio(
                        chat_id=chat_id,
                        audio=button['file_id'],
                        caption=button.get('caption'),
                        reply_markup=get_main_menu(is_admin=True)[0]
                    )
                elif button['file_type'] == 'video':
                    await context.bot.send_video(
                        chat_id=chat_id,
                        video=button['file_id'],
                        caption=button.get('caption'),
                        reply_markup=get_main_menu(is_admin=True)[0]
                    )
                elif button['file_type'] == 'document':
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=button['file_id'],
                        caption=button.get('caption'),
                        reply_markup=get_main_menu(is_admin=True)[0]
                    )
                elif button['file_type'] == 'photo':
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=button['file_id'],
                        caption=button.get('caption'),
                        reply_markup=get_main_menu(is_admin=True)[0]
                    )
                elif button['file_type'] == 'text':
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=button['file_id'],
                        reply_markup=get_main_menu(is_admin=True)[0]
                    )
                elif button['file_type'] == 'forward':
                    await context.bot.forward_message(
                        chat_id=chat_id,
                        from_chat_id=chat_id,
                        message_id=button['file_id']
                    )
                return
            elif text == button['text']:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"دکمه سیستمی '{text}' غیرفعال است.",
                    reply_markup=get_main_menu(is_admin=True)[0]
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
                reply_markup=get_main_menu(is_admin=True)[0]
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
        elif text == '⤴️پیام همگانی':
            context.user_data['stage'] = 'broadcast_message'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً پیام همگانی (متن، فایل، عکس، صوت یا ویدئو) را ارسال کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_CONTENT
        elif text == '🈂فوروارد همگانی':
            context.user_data['stage'] = 'broadcast_forward'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً پیام را فوروارد کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_CONTENT
        elif text == '♓همگانی و عکس':
            context.user_data['stage'] = 'broadcast_photo'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً عکس را ارسال کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_CONTENT
        elif text == '⏫همگانی و فایل':
            context.user_data['stage'] = 'broadcast_file'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً فایل را ارسال کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_CONTENT
        elif text == '👱ادمین‌ها':
            await context.bot.send_message(
                chat_id=chat_id,
                text="مدیریت ادمین‌ها هنوز پیاده‌سازی نشده است.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == '❇️متن پیشفرض':
            context.user_data['stage'] = 'set_default_text'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً متن پیش‌فرض جدید را وارد کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_CONTENT
        elif text == '🆕متن استارت':
            context.user_data['stage'] = 'set_start_text'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً متن استارت جدید را وارد کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_CONTENT
        elif text == '🔴ریست کردن':
            await context.bot.send_message(
                chat_id=chat_id,
                text="ریست کردن بات هنوز پیاده‌سازی نشده است.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == '📮پیام به کاربر':
            context.user_data['stage'] = 'send_message_to_user'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً آیدی کاربر را وارد کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_TO_USER
        elif text == '📤آپلود داخلی':
            await context.bot.send_message(
                chat_id=chat_id,
                text="آپلود داخلی هنوز پیاده‌سازی نشده است.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == 'آمار':
            users_count = db.users.count_documents({})
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"تعداد کاربران: {users_count}",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == '⛔️خاموش کردن بات':
            update_setting('on_off', 'false')
            await context.bot.send_message(
                chat_id=chat_id,
                text="بات خاموش شد.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == '✴️روشن کردن بات':
            update_setting('on_off', 'true')
            await context.bot.send_message(
                chat_id=chat_id,
                text="بات روشن شد.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == '📣تنظیم چنل':
            context.user_data['stage'] = 'set_channel'
            await context.bot.send_message(
                chat_id=chat_id,
                text="لطفاً آیدی کانال (مثال: @ChannelID) را وارد کنید:",
                reply_markup=ReplyKeyboardMarkup([['↩️لغو']], resize_keyboard=True)
            )
            return SEND_MESSAGE_CONTENT
        elif text == '⚠️راهنما':
            await context.bot.send_message(
                chat_id=chat_id,
                text="راهنما: از منوهای موجود برای مدیریت بات استفاده کنید.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == '📂پشتیبان‌گیری':
            await backup_data(chat_id, context)
        elif text == '🔒قفل ربات':
            await context.bot.send_message(
                chat_id=chat_id,
                text="قفل ربات هنوز پیاده‌سازی نشده است.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == '♦حساب کاربری ربات':
            await context.bot.send_message(
                chat_id=chat_id,
                text="حساب کاربری ربات هنوز پیاده‌سازی نشده است.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
        elif text == '↩️لغو':
            context.user_data.clear()
            await context.bot.send_message(
                chat_id=chat_id,
                text="عملیات لغو شد.",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
            return ConversationHandler.END
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="گزینه انتخاب‌شده معتبر نیست. لطفاً از منوی زیر انتخاب کنید:",
                reply_markup=get_main_menu(is_admin=True)[0]
            )
    else:
        if get_setting('pm_forward') == '✅':
            await context.bot.forward_message(
                chat_id=int(ADMIN_ID),
                from_chat_id=chat_id,
                message_id=update.message.message_id
            )
        if get_setting('pm_resani') == '✅':
            await context.bot.send_message(
                chat_id=chat_id,
                text=get_setting('default_text') or "پیام دریافت شد. لطفاً منتظر پاسخ باشید.",
                reply_markup=get_main_menu(is_admin=False)[0]
            )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "عملیات لغو شد.",
        reply_markup=get_main_menu(is_admin=update.effective_user.id == int(ADMIN_ID))[0]
    )
    return ConversationHandler.END