from pathlib import Path

from telegram import InputFile, Update
from telegram.ext import ContextTypes

from quotes_bot.card_renderer import render_card_bytes
from quotes_bot.config import PHOTOS_DIR
from quotes_bot.import_photos import import_photo
from quotes_bot.keyboards import card_keyboard, get_main_keyboard
from quotes_bot.models import find_person_by_name, get_first_card_for_person, list_people

AWAITING_PHOTO_KEY = "awaiting_photo_person_id"
IMAGE_DOCUMENT_MIMES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}


async def _save_photo_for_person(update: Update, person, source_path: Path) -> None:
    destination = PHOTOS_DIR / person.photo_url
    import_photo(source_path, destination)

    preview = get_first_card_for_person(person.id)
    if preview:
        await update.effective_chat.send_photo(
            photo=InputFile(render_card_bytes(preview), filename="card.jpg"),
            reply_markup=card_keyboard(preview),
        )

    await update.effective_message.reply_text(
        f"Фото для <b>{person.name}</b> обновлено ✅",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


async def _download_image_message(update: Update, destination: Path) -> bool:
    message = update.message
    if not message:
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)

    if message.photo:
        telegram_file = await message.photo[-1].get_file()
        await telegram_file.download_to_drive(destination)
        return True

    document = message.document
    if document and (document.mime_type in IMAGE_DOCUMENT_MIMES or (document.file_name or "").lower().endswith((".jpg", ".jpeg", ".png", ".webp"))):
        telegram_file = await document.get_file()
        await telegram_file.download_to_drive(destination)
        return True

    return False


def _resolve_person_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return None

    if message.caption:
        person = find_person_by_name(message.caption.strip())
        if person:
            return person

    awaiting_id = context.user_data.get(AWAITING_PHOTO_KEY)
    if awaiting_id is not None:
        for person in list_people():
            if person.id == awaiting_id:
                context.user_data.pop(AWAITING_PHOTO_KEY, None)
                return person

    return None


async def upload_person_photo_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.message
    if not message or (not message.photo and not message.document):
        return

    person = _resolve_person_from_message(update, context)
    if not person:
        if message.caption:
            names = ", ".join(item.name for item in list_people())
            await message.reply_text(
                f"Не нашёл «{message.caption.strip()}».\n\n"
                "Отправь фото с подписью — точным именем, например:\n"
                "<b>Машинка</b>\n\n"
                f"Сейчас в базе: {names}",
                parse_mode="HTML",
                reply_markup=get_main_keyboard(),
            )
        else:
            await message.reply_text(
                "Сначала напиши имя человека, например <b>Машинка</b>, "
                "а потом отправь фото.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard(),
            )
        return

    if not person.photo_url:
        await message.reply_text(
            f"У {person.name} не задан файл фото в базе.",
            reply_markup=get_main_keyboard(),
        )
        return

    temp_path = PHOTOS_DIR / "inbox" / "_upload_temp.jpg"
    if not await _download_image_message(update, temp_path):
        await message.reply_text(
            "Не удалось получить изображение. Отправь фото или файл-картинку.",
            reply_markup=get_main_keyboard(),
        )
        return

    await _save_photo_for_person(update, person, temp_path)
    temp_path.unlink(missing_ok=True)


async def prepare_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.text:
        return

    person = find_person_by_name(message.text.strip())
    if not person:
        return

    context.user_data[AWAITING_PHOTO_KEY] = person.id
    await message.reply_text(
        f"Жду фото для <b>{person.name}</b>.\n"
        "Отправь картинку следующим сообщением.",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


async def photo_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        person = find_person_by_name(" ".join(context.args))
        if person:
            context.user_data[AWAITING_PHOTO_KEY] = person.id
            await update.message.reply_text(
                f"Ок, жду фото для <b>{person.name}</b>.\n\n"
                "Отправь <b>следующим сообщением</b> картинку.\n"
                "Можно без подписи или с подписью "
                f"<b>{person.name}</b>.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard(),
            )
            return

        await update.message.reply_text(
            f"Не нашёл «{' '.join(context.args)}».\n"
            "Пример: <code>/photo Машинка</code>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
        return

    await update.message.reply_text(
        "Как обновить фото:\n"
        "1. <code>/photo Машинка</code>\n"
        "2. Отправь фото следующим сообщением\n\n"
        "Или сразу: фото + подпись <b>Машинка</b>",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )
