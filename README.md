# Telegram Forum Topic Index Bot

Telegram forum guruhlaridagi barcha mavzularni (topics) avtomatik aniqlab,
o'zbek alifbosi bo'yicha saralangan, bosiladigan havolalar ko'rinishida
chiqarib beruvchi professional Telegram bot.

## Xususiyatlari

- 📚 Har qanday ochiq forum guruhning barcha mavzularini oladi
- 🔤 Mavzularni **o'zbek lotin alifbosi** tartibida saralaydi (A, B, D, E, F,
  G, Gʻ, H, I, J, K, L, M, N, O, Oʻ, P, Q, R, S, T, U, V, X, Y, Z, Sh, Ch)
- 🔗 Har bir mavzu nomini to'g'ridan-to'g'ri o'sha mavzuga olib boruvchi
  bosiladigan HTML havolaga aylantiradi
- 📄 100 tadan ortiq mavzu bo'lsa, avtomatik ravishda bir nechta xabarga
  bo'lib yuboradi
- ⚡ To'liq asinxron (async/await) arxitektura
- 🛡️ Barcha xatoliklarni to'g'ri ushlaydi (guruh topilmadi, forum emas,
  userbot a'zo emas, FloodWait va h.k.)

## Qanday ishlaydi

Loyiha ikkita Telegram API'dan foydalanadi:

1. **Aiogram (Bot API)** — foydalanuvchi bilan muloqot qiladi (xabar qabul
   qiladi, javob yuboradi).
2. **Telethon (MTProto, userbot)** — oddiy Bot API forum mavzularini to'liq
   o'qiy olmagani sababli, haqiqiy foydalanuvchi akkaunt (userbot) orqali
   `GetForumTopicsRequest` chaqirig'i yordamida guruhning barcha
   mavzularini oladi.

**Muhim:** Userbot (Telethon sessiyasi ochilgan akkaunt) tekshirilmoqchi
bo'lgan forum guruhga **a'zo bo'lishi shart**, aks holda bot
`❌ Userbot ushbu guruhga qo'shilmagan.` xabarini qaytaradi.

## Loyiha tuzilishi

```
forum-topic-bot/
│
├── bot.py            # Aiogram handlerlar, botning kirish nuqtasi
├── config.py         # .env dan sozlamalarni o'qish va validatsiya
├── forum.py          # Telethon orqali forum/mavzularni olish logikasi
├── sorter.py         # O'zbek alifbosi bo'yicha maxsus saralash algoritmi
├── formatter.py       # Mavzularni sahifalarga bo'lib, HTML xabar qilib formatlash
├── requirements.txt  # Python kutubxonalari
├── .env.example      # Namuna environment fayli
└── README.md         # Ushbu hujjat
```

## O'rnatish

### 1. Repozitoriyani yuklab oling

```bash
git clone <repo-url> forum-topic-bot
cd forum-topic-bot
```

### 2. Virtual muhit yarating (tavsiya etiladi)

```bash
python3 -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 3. Kutubxonalarni o'rnating

```bash
pip install -r requirements.txt
```

### 4. Telegram ma'lumotlarini oling

**Bot Token:**
1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing.
2. `/newbot` buyrug'ini yuboring va ko'rsatmalarga amal qiling.
3. Berilgan tokenni saqlab qo'ying.

**API ID va API Hash (userbot uchun):**
1. [https://my.telegram.org/apps](https://my.telegram.org/apps) manziliga
   kiring va telefon raqamingiz bilan tizimga kiring.
2. Yangi ilova yarating (App title va Short name ixtiyoriy).
3. Sizga beriladigan `api_id` va `api_hash` qiymatlarini saqlab qo'ying.

### 5. `.env` faylini sozlang

`.env.example` faylidan nusxa oling:

```bash
cp .env.example .env
```

`.env` faylini oching va o'z qiymatlaringizni kiriting:

```env
BOT_TOKEN=123456789:AAExampleBotTokenHere
API_ID=12345678
API_HASH=your_api_hash_here
SESSION_NAME=forum_userbot
```

### 6. Botni ishga tushiring

```bash
python bot.py
```

Birinchi marta ishga tushirganingizda, Telethon sizdan **telefon raqami**,
so'ngra **tasdiqlash kodi** (va agar yoqilgan bo'lsa, ikki bosqichli
parolni) so'raydi. Bu faqat bir marta sodir bo'ladi — muvaffaqiyatli login
qilingandan so'ng, sessiya `forum_userbot.session` fayliga saqlanadi va
keyingi ishga tushirishlarda qayta so'ralmaydi.

**Eslatma:** Userbot sifatida ishlatilayotgan akkaunt tekshirmoqchi
bo'lgan barcha forum guruhlarga oldindan a'zo bo'lishi kerak.

## Foydalanish

Botga quyidagi buyruqlarni yuborishingiz mumkin:

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Bot haqida umumiy ma'lumot |
| `/help` | Batafsil yordam oynasi |
| `/about` | Loyiha haqida ma'lumot |
| `/ping` | Bot ishlab turganini tekshirish |

Mavzularni olish uchun, botga forum guruhning username'ini yuboring:

```
@PythonUzForum
```

Bot javob sifatida quyidagi ko'rinishdagi xabar(lar)ni yuboradi:

```
📚 Guruh: @PythonUzForum

📊 Jami mavzular: 253

📄 Sahifa 1/3

1. Aiogram
2. Android
3. Botlar
4. Django
5. Docker
...
100. Xabarlar

Davomi keyingi xabarda...
```

Bu yerda har bir mavzu nomi — o'sha mavzuga to'g'ridan-to'g'ri olib
boruvchi bosiladigan havoladir.

## Xatolik xabarlari

| Holat | Xabar |
|-------|-------|
| Username topilmadi | `❌ Guruh topilmadi.` |
| Guruh forum emas | `❌ Ushbu guruh forum emas.` |
| Userbot guruhga a'zo emas | `❌ Userbot ushbu guruhga qo'shilmagan.` |
| Telegram FloodWait qaytardi | Bot avtomatik kutadi va davom etadi (xabar ko'rsatilmaydi) |
| Kutilmagan xatolik | `❌ Kutilmagan xatolik yuz berdi. Keyinroq qayta urinib ko'ring.` |

## O'zbek alifbosi bo'yicha saralash

`sorter.py` moduli oddiy Python `sort()` funksiyasidan foydalanmaydi,
chunki u lotin alifbosini kodpoint tartibida saralaydi va bu o'zbek tilidagi
`Gʻ`, `Oʻ`, `Sh`, `Ch` kabi harf/digraflarni noto'g'ri joylashtiradi.

Buning o'rniga, quyidagi rasmiy tartibga asoslangan maxsus algoritm
qo'llaniladi:

```
A, B, D, E, F, G, Gʻ, H, I, J, K, L, M, N, O, Oʻ, P, Q, R, S, T, U, V, X, Y, Z, Sh, Ch
```

Algoritm har bir so'zni ushbu tokenlar bo'yicha (eng uzunidan boshlab —
`Sh`, `Ch`, `Gʻ`, `Oʻ` kabi ko'p harfli birliklarni birinchi navbatda
moslashtirib) tokenlarga bo'ladi va har bir tokenga mos rank asosida sort
key yaratadi. Turli xil apostrof belgilari (`'`, `’`, `` ` ``, `ʼ`) ham
avtomatik ravishda kanonik `ʻ` belgisiga normallashtiriladi.

## Texnik talablar

- Python 3.12+
- Aiogram 3.x
- Telethon
- python-dotenv

## Litsenziya

Ushbu loyiha ochiq manba sifatida taqdim etilgan — istalgan maqsadda
o'zgartirish va foydalanish mumkin.
