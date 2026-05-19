import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv
from downloader import download_media

load_dotenv()

TOKEN = os.getenv("8653850059:AAF_nTI_pYzVno8QyGSLVpTIVVDIf01Rl6s")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Salom! Men media yuklovchi botman!\n\n"
        "📥 <b>Nima qila olaman:</b>\n"
        "• YouTube video va musiqa\n"
        "• Instagram rasm, video, reels\n"
        "• TikTok video\n\n"
        "🔗 Faqat havola yuboring, qolganini men qilaman!\n\n"
        "📌 <b>Eslatma:</b> Fayl hajmi 50MB dan oshmasligi kerak.",
        parse_mode="HTML"
    )


@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "✅ <b>Qo'llab-quvvatlanadigan saytlar:</b>\n"
        "• youtube.com / youtu.be\n"
        "• instagram.com\n"
        "• tiktok.com\n\n"
        "📤 <b>Ishlatish:</b>\n"
        "Havola yuboring → Bot yuklab beradi\n\n"
        "⚠️ <b>Cheklov:</b> 50MB gacha",
        parse_mode="HTML"
    )


@dp.message(F.text)
async def link_handler(message: Message):
    text = message.text.strip()

    # URL tekshirish
    if not any(domain in text for domain in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]):
        await message.answer(
            "❌ Noto'g'ri havola!\n\n"
            "Iltimos, quyidagi saytlardan havola yuboring:\n"
            "• youtube.com\n"
            "• instagram.com\n"
            "• tiktok.com"
        )
        return

    status_msg = await message.answer("⏳ Yuklanmoqda, biroz kuting...")

    try:
        result = await download_media(text)

        if result["type"] == "video":
            await bot.delete_message(message.chat.id, status_msg.message_id)
            await message.answer_video(
                types.FSInputFile(result["path"]),
                caption=f"✅ <b>{result.get('title', 'Video')}</b>",
                parse_mode="HTML"
            )
        elif result["type"] == "audio":
            await bot.delete_message(message.chat.id, status_msg.message_id)
            await message.answer_audio(
                types.FSInputFile(result["path"]),
                title=result.get("title", "Musiqa"),
                caption="✅ Musiqa yuklandi!",
                parse_mode="HTML"
            )
        elif result["type"] == "photo":
            await bot.delete_message(message.chat.id, status_msg.message_id)
            await message.answer_photo(
                types.FSInputFile(result["path"]),
                caption="✅ Rasm yuklandi!"
            )
        elif result["type"] == "multiple_photos":
            await bot.delete_message(message.chat.id, status_msg.message_id)
            media_group = []
            for i, path in enumerate(result["paths"]):
                if i == 0:
                    media_group.append(types.InputMediaPhoto(
                        media=types.FSInputFile(path),
                        caption="✅ Rasmlar yuklandi!"
                    ))
                else:
                    media_group.append(types.InputMediaPhoto(
                        media=types.FSInputFile(path)
                    ))
            await message.answer_media_group(media_group)
        else:
            await status_msg.edit_text("❌ " + result.get("error", "Noma'lum xatolik"))

        # Faylni o'chirish
        if result["type"] in ["video", "audio", "photo"]:
            if os.path.exists(result["path"]):
                os.remove(result["path"])
        elif result["type"] == "multiple_photos":
            for path in result.get("paths", []):
                if os.path.exists(path):
                    os.remove(path)

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await status_msg.edit_text(
            "❌ Yuklab bo'lmadi!\n\n"
            "Sabablari:\n"
            "• Havola noto'g'ri\n"
            "• Fayl 50MB dan katta\n"
            "• Kontent o'chirilgan yoki yopiq\n\n"
            "Boshqa havola sinab ko'ring."
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
