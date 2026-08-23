# Bot Tech

بوت Telegram لخدمة المتعلمين وربطهم بمنصة الوعي التقني.

## المميزات

* أوامر ورسائل تفاعلية.
* أزرار وقوائم سهلة الاستخدام.
* ربط بخدمات منصة الوعي التقني.
* تشغيل مستمر واستجابة سريعة.
* حفظ رمز البوت في متغيرات البيئة.

## المتطلبات

* Python 3.7 أو أحدث.
* Git.
* Telegram Bot Token.

## التثبيت

```bash
git clone https://github.com/akrm77-tech/bot_tech.git
cd bot_tech
python3 -m venv .venv
```

تفعيل البيئة الافتراضية:

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

تثبيت المتطلبات:

```bash
python -m pip install -r requirements.txt
```

## الإعداد

ضع رمز البوت في متغير البيئة `BOT_TOKEN` بدلًا من كتابته داخل الكود.

### Linux / macOS

```bash
export BOT_TOKEN="YOUR_BOT_TOKEN"
```

### Windows PowerShell

```powershell
$env:BOT_TOKEN="YOUR_BOT_TOKEN"
```

## التشغيل

```bash
python src/main.py
```

## الاختبارات

لتشغيل الاختبارات:

```bash
python -m unittest discover -s tests -v
```

الاختبارات لا تحتاج إلى رمز البوت.

## بنية المشروع

```text
bot_tech/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── gitleaks.yml
├── src/
│   ├── main.py
│   ├── handlers/
│   └── utils/
├── tests/
├── .gitignore
├── README.md
├── SECURITY.md
├── LICENSE
└── requirements.txt
```

## الأمان

* لا تضع رمز البوت داخل ملفات المشروع.
* لا ترفع ملف `.env` إلى GitHub.
* استخدم متغيرات البيئة لحفظ البيانات الحساسة.
* إذا تم نشر رمز البوت بالخطأ، قم بإلغائه وإنشاء رمز جديد.

لمزيد من التفاصيل راجع ملف `SECURITY.md`.

## الإصدار

`1.0`

## المطور

[@akrm77-tech]
