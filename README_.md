# 📥 Telegram Media Downloader Bot

YouTube, Instagram va TikTok dan video, musiqa va rasm yuklovchi Telegram bot.

---

## 🚀 Railway.app ga Deploy qilish (BEPUL, 24/7)

### 1-qadam: GitHub ga yuklash
1. [github.com](https://github.com) ga kiring
2. **New repository** bosing
3. Nom bering: `telegram-media-bot`
4. **Create repository** bosing
5. Barcha fayllarni yuklang

### 2-qadam: Railway ga ulash
1. [railway.app](https://railway.app) ga kiring
2. GitHub bilan ro'yxatdan o'ting
3. **New Project** → **Deploy from GitHub repo**
4. O'zingizning `telegram-media-bot` repo ni tanlang

### 3-qadam: Token qo'shish
1. Railway dashboard → **Variables** bo'limi
2. **Add Variable** bosing:
   - Key: `BOT_TOKEN`
   - Value: `sizning_tokeningiz`
3. **Save** bosing

### 4-qadam: Deploy
- Railway avtomatik deploy qiladi
- **Logs** bo'limida `Started polling` ko'rsangiz — bot ishlayapti! ✅

---

## 💻 Lokal ishga tushirish (test uchun)

```bash
# 1. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 2. .env faylini tahrirlang
# BOT_TOKEN=sizning_tokeningiz

# 3. Botni ishga tushirish
python bot.py
```

---

## 📋 Fayllar
- `bot.py` — Asosiy bot fayli
- `downloader.py` — Yuklovchi modul
- `requirements.txt` — Kerakli kutubxonalar
- `.env` — Token saqlash (GitHubga yuklamang!)
- `Procfile` — Railway uchun

---

## ⚠️ Muhim
- `.env` faylini hech qachon GitHubga yuklamang!
- Railway da token **Variables** orqali qo'shiladi
- Fayl limiti: 50MB
