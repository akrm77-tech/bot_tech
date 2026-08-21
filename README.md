# 🤖 بوت منصة الوعي التقني (Bot Tech)

بوت تفاعلي متقدم مخصص لخدمة المتعلمين والربط بمنصة الوعي التقني بأسلوب سلس وسريع.

## 📁 هيكلية المشروع
- `src/`: يحتوي على الكود المصدري الرئيسي (`main.py`).
- `docs/`: ملفات التوثيق والشرح.
- `assets/`: الأصول والوسائط المستخدمة.

## ⚙️ التثبيت والتشغيل
1. استنسخ المستودع:
   ```bash
   git clone https://github.com/akrm77-tech/bot_tech.git
   ```
2. تثبيت التبعيات:
   ```bash
   pip install -r requirements.txt
   ```
3. عرّف إعدادات التشغيل خارج الكود:
   ```bash
   export BOT_TOKEN='ضع_رمز_البوت_في_بيئة_آمنة'
   export CHANNEL_ID='@AlWa3yAlTaqni'
   ```
4. تشغيل البوت:
   ```bash
   python src/main.py
   ```

> لا تضع رمز Telegram داخل `src/main.py` أو README أو سجل التشغيل. إذا كان الرمز قد ظهر سابقاً في Git، ألغِه من BotFather وأنشئ رمزاً جديداً قبل النشر.

## الاختبار والتحقق

```bash
python -m unittest discover -s tests -v
```

الاختبارات لا تتصل بـ Telegram ولا تحتاج إلى `BOT_TOKEN`.

---
المهندس أكرم الشرعبي © 2026
