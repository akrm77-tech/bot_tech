  # ===================================================================
# 🤖 بوت منصة الوعي التقني - النسخة الاحترافية للشرق الأوسط
# المهندس أكرم الشرعبي - 2026
# ===================================================================

import logging
import sqlite3
import json
import random
import string
from datetime import datetime, timedelta
from threading import Thread
import csv
import io
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
# ==================== الإعدادات الأساسية ====================
# Never store Telegram credentials in source control.
TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = [6677854381, 7891169650]
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@AlWa3yAlTaqni")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is required; set it as an environment variable or GitHub secret")

# ==================== قاعدة البيانات ====================
DB_NAME = "tech_awareness.db"

def init_db():
    """إنشاء قاعدة البيانات وجداولها"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # جدول المستخدمين
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            join_date TEXT,
            last_active TEXT,
            daily_subscribed INTEGER DEFAULT 1,
            points INTEGER DEFAULT 0,
            level TEXT DEFAULT 'مبتدئ'
        )
    ''')
    
    # جدول الاختبارات
    c.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            options TEXT,
            correct_answer TEXT,
            category TEXT,
            difficulty TEXT
        )
    ''')
    
    # جدول النتائج
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            quiz_id INTEGER,
            score INTEGER,
            date TEXT
        )
    ''')
    
    # جدول الإشعارات
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            date TEXT,
            sent INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

# ==================== دوال قاعدة البيانات ====================
def add_user(user_id, username, first_name, last_name):
    """إضافة مستخدم جديد أو تحديثه"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, first_name, last_name, join_date, last_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, now, now))
    conn.commit()
    conn.close()

def get_user(user_id):
    """جلب بيانات مستخدم"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    """جلب جميع المستخدمين"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    return [u[0] for u in users]

def update_points(user_id, points):
    """تحديث نقاط المستخدم"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (points, user_id))
    conn.commit()
    conn.close()

# ==================== دوال البوت الأساسية ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت"""
    user = update.effective_user
    add_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_text = f"""
👋 **أهلاً بك في بوت منصة الوعي التقني**  
المهندس أكرم الشرعبي  

🎯 **مهمتنا:** بناء مجتمع رقمي واعٍ وآمن في الشرق الأوسط

📚 **ماذا نقدم لك؟**
• دورات في الأمن السيبراني والهكر الأخلاقي
• شرح الشبكات والبرمجة
• اختبارات تفاعلية لقياس مستواك
• إشعارات يومية بمعلومات تقنية جديدة

🔹 **ابدأ رحلتك الآن بالضغط على الأزرار أدناه**
    """
    
    keyboard = [
        [InlineKeyboardButton("📚 المجالات", callback_data="categories")],
        [InlineKeyboardButton("📝 اختبار تفاعلي", callback_data="quiz")],
        [InlineKeyboardButton("📰 آخر الأخبار", callback_data="news")],
        [InlineKeyboardButton("👥 انضم للمجموعة", url="https://t.me/AlWa3yAlTaqni")],
        [InlineKeyboardButton("📞 تواصل مع المدير", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار التفاعلية"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "categories":
        await show_categories(query)
    elif data.startswith("cat_"):
        category = data.replace("cat_", "")
        await show_category_details(query, category)
    elif data == "quiz":
        await start_quiz(query)
    elif data.startswith("quiz_"):
        quiz_id = data.replace("quiz_", "")
        await show_quiz_question(query, int(quiz_id))
    elif data == "news":
        await show_news(query)
    elif data == "contact":
        await show_contact(query)
    elif data == "daily":
        await send_daily_tip(query)
    elif data.startswith("ans_"):
        await check_answer(query, data)
    elif data == "next_quiz":
        await next_question(query)
    elif data == "admin_panel":
        await admin_panel(query)
    elif data == "stats":
        await show_stats(query)
    elif data == "broadcast":
        await broadcast_menu(query)
    elif data == "export":
        await export_data(query)

# ==================== دوال المجالات ====================
async def show_categories(query):
    """عرض المجالات التعليمية"""
    categories_text = """
📚 **مجالاتنا التعليمية**

اختر المجال الذي تريد التعرف عليه:
    """
    
    keyboard = [
        [InlineKeyboardButton("🛡️ الأمن السيبراني", callback_data="cat_cyber")],
        [InlineKeyboardButton("🌐 الشبكات", callback_data="cat_networks")],
        [InlineKeyboardButton("💻 البرمجة", callback_data="cat_programming")],
        [InlineKeyboardButton("🤖 الذكاء الاصطناعي", callback_data="cat_ai")],
        [InlineKeyboardButton("🔹 تقنية المعلومات", callback_data="cat_it")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        categories_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def show_category_details(query, category):
    """عرض تفاصيل مجال معين"""
    details = {
        "cyber": {
            "title": "🛡️ الأمن السيبراني والهكر الأخلاقي",
            "desc": """
**ماذا ستتعلم؟**
• أساسيات الأمن السيبراني
• أنواع الهجمات وكيفية الحماية منها
• الهكر الأخلاقي وأدواته
• حماية الشبكات والبيانات
• تحليل الثغرات الأمنية

🎯 **المستوى:** مبتدئ إلى متقدم
⏱️ **المدة:** 8 أسابيع
🏆 **الشهادة:** معتمدة من المنصة
            """
        },
        "networks": {
            "title": "🌐 الشبكات",
            "desc": """
**ماذا ستتعلم؟**
• أساسيات الشبكات (OSI, TCP/IP)
• بروتوكولات الشبكة
• تصميم الشبكات وإدارتها
• أمن الشبكات
• شبكات الواي فاي والإنترنت

🎯 **المستوى:** مبتدئ إلى متوسط
⏱️ **المدة:** 6 أسابيع
🏆 **الشهادة:** معتمدة من المنصة
            """
        },
        "programming": {
            "title": "💻 البرمجة",
            "desc": """
**ماذا ستتعلم؟**
• أساسيات البرمجة (Python, JavaScript)
• بناء تطبيقات ويب
• تطوير تطبيقات الهواتف
• قواعد البيانات
• مشاريع عملية

🎯 **المستوى:** مبتدئ
⏱️ **المدة:** 10 أسابيع
🏆 **الشهادة:** معتمدة من المنصة
            """
        },
        "ai": {
            "title": "🤖 الذكاء الاصطناعي",
            "desc": """
**ماذا ستتعلم؟**
• أساسيات الذكاء الاصطناعي
• تعلم الآلة (Machine Learning)
• معالجة اللغة الطبيعية (NLP)
• الرؤية الحاسوبية (Computer Vision)
• تطبيقات الذكاء الاصطناعي

🎯 **المستوى:** متوسط إلى متقدم
⏱️ **المدة:** 12 أسبوعاً
🏆 **الشهادة:** معتمدة من المنصة
            """
        },
        "it": {
            "title": "🔹 تقنية المعلومات",
            "desc": """
**ماذا ستتعلم؟**
• أساسيات الحاسوب
• أنظمة التشغيل
• إدارة الخوادم
• خدمات السحابة (Cloud)
• الدعم الفني وحل المشكلات

🎯 **المستوى:** مبتدئ
⏱️ **المدة:** 4 أسابيع
🏆 **الشهادة:** معتمدة من المنصة
            """
        }
    }
    
    cat_data = details.get(category)
    if not cat_data:
        await query.edit_message_text("❌ مجال غير موجود!")
        return
    
    keyboard = [
        [InlineKeyboardButton("📝 ابدأ الاختبار", callback_data=f"quiz_cat_{category}")],
        [InlineKeyboardButton("📚 العودة للمجالات", callback_data="categories")],
        [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"**{cat_data['title']}**\n\n{cat_data['desc']}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

# ==================== دوال الاختبارات ====================
async def start_quiz(query):
    """بدء اختبار تفاعلي"""
    keyboard = [
        [InlineKeyboardButton("🔹 اختبار الأمن السيبراني", callback_data="quiz_cyber")],
        [InlineKeyboardButton("🔹 اختبار الشبكات", callback_data="quiz_networks")],
        [InlineKeyboardButton("🔹 اختبار البرمجة", callback_data="quiz_programming")],
        [InlineKeyboardButton("🔹 اختبار الذكاء الاصطناعي", callback_data="quiz_ai")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🧠 **اختر اختبارك:**\nكل اختبار يحتوي على 10 أسئلة متنوعة.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def show_quiz_question(query, quiz_id):
    """عرض سؤال اختبار"""
    # محاكاة أسئلة (في الحقيقية ستجلب من قاعدة البيانات)
    questions = {
        1: {
            "question": "ما هو التهديد الأمني الذي يعتمد على خداع المستخدمين للحصول على معلوماتهم؟",
            "options": ["فيروس", "هندسة اجتماعية", "اختراق", "برمجيات خبيثة"],
            "correct": 1  # مؤشر 0-based
        },
        2: {
            "question": "ما البروتوكول المستخدم لنقل الملفات عبر الإنترنت؟",
            "options": ["HTTP", "FTP", "SMTP", "POP3"],
            "correct": 1
        },
        # سيتم إضافة المزيد في قاعدة البيانات
    }
    
    q = questions.get(quiz_id, questions[1])
    
    keyboard = []
    for i, option in enumerate(q["options"]):
        keyboard.append([InlineKeyboardButton(f"{i+1}. {option}", callback_data=f"ans_{quiz_id}_{i}")])
    
    keyboard.append([InlineKeyboardButton("🔙 إنهاء الاختبار", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"❓ **السؤال {quiz_id}:**\n{q['question']}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def check_answer(query, data):
    """التحقق من الإجابة"""
    _, quiz_id, answer_index = data.split("_")
    quiz_id = int(quiz_id)
    answer_index = int(answer_index)
    
    # محاكاة التصحيح
    correct = random.choice([True, False])  # سيتم ربطه بقاعدة البيانات
    
    if correct:
        update_points(query.from_user.id, 10)
        response = "✅ **إجابة صحيحة!** +10 نقاط"
    else:
        response = "❌ **إجابة خاطئة!** حاول مرة أخرى."
    
    keyboard = [[InlineKeyboardButton("▶️ السؤال التالي", callback_data="next_quiz")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{response}\n\nالسؤال الحالي: {quiz_id}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

# ==================== دوال الإشعارات والأخبار ====================
async def show_news(query):
    """عرض آخر الأخبار"""
    news_text = """
📰 **آخر الأخبار من المنصة**

🚀 **إعلان هام:**
نطلق قريباً دورة مكثفة في الأمن السيبراني لمدة 8 أسابيع مع مدربين محترفين.

📅 **فعاليات قادمة:**
• 15 يوليو: ورشة عمل عن الذكاء الاصطناعي
• 20 يوليو: مسابقة البرمجة الأولى
• 1 أغسطس: مؤتمر الأمن السيبراني السنوي

📢 **انضم الآن ولا تفوت الفرصة!**
    """
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        news_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def send_daily_tip(query):
    """إرسال نصيحة يومية"""
    tips = [
        "🔐 استخدم كلمات مرور قوية (أكثر من 12 حرفاً، تحتوي على أرقام ورموز).",
        "📱 قم بتحديث تطبيقاتك باستمرار لتجنب الثغرات الأمنية.",
        "🌐 لا تثق في روابط مختصرة مجهولة المصدر.",
        "🛡️ فعّل التحقق بخطوتين في حساباتك المهمة.",
        "💻 قم بعمل نسخ احتياطية لبياناتك بانتظام."
    ]
    
    tip = random.choice(tips)
    await query.edit_message_text(
        f"💡 **نصيحة اليوم:**\n\n{tip}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 اشتراك يومي", callback_data="daily_sub")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ])
    )

# ==================== دوال المدير (Admin) ====================
async def admin_panel(query):
    """لوحة تحكم المدير"""
    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("❌ غير مصرح لك بالدخول إلى لوحة التحكم.")
        return
    
    stats = get_all_users()
    total_users = len(stats)
    
    panel_text = f"""
👑 **لوحة تحكم المدير**

📊 **الإحصائيات:**
• عدد المستخدمين: {total_users}
• النشاط اليومي: قيد التحديث
• عدد الاختبارات: 15

🔧 **أدوات التحكم:**
• إرسال رسائل جماعية
• تصدير بيانات المستخدمين
• إدارة المحتوى
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("📨 إرسال للجميع", callback_data="broadcast")],
        [InlineKeyboardButton("📤 تصدير البيانات", callback_data="export")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        panel_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def show_stats(query):
    """عرض الإحصائيات"""
    users = get_all_users()
    total = len(users)
    
    # إحصائيات إضافية (محاكاة)
    stats_text = f"""
📊 **إحصائيات المنصة**

👥 **المستخدمون:** {total}
✅ **نشطاء اليوم:** {random.randint(30, 100)}
📝 **اختبارات منجزة:** {random.randint(100, 500)}
🏆 **مجموع النقاط:** {random.randint(1000, 5000)}
🌟 **أعلى مستوى:** متقدم

📈 **معدل النمو الأسبوعي:** +15%
    """
    
    await query.edit_message_text(
        stats_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
        ])
    )

async def broadcast_menu(query):
    """قائمة إرسال رسائل جماعية"""
    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("❌ غير مصرح لك.")
        return
    
    await query.edit_message_text(
        "📨 **إرسال رسالة جماعية**\n\n"
        "أرسل الرسالة التي تريد نشرها لجميع المستخدمين.\n"
        "يمكنك استخدام النص العادي أو المنسق (HTML/Markdown).",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data="admin_panel")]
        ])
    )
    # سيتم استقبال الرسالة في handler منفصل

async def export_data(query):
    """تصدير بيانات المستخدمين"""
    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("❌ غير مصرح لك.")
        return
    
    # تصدير بصيغة CSV
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['user_id', 'username', 'first_name', 'last_name', 'phone', 'join_date', 'points', 'level'])
    writer.writerows(data)
    
    # إرسال الملف
    output.seek(0)
    await query.message.reply_document(
        document=output.getvalue().encode('utf-8'),
        filename="users_data.csv"
    )
    
    await query.edit_message_text("✅ تم تصدير البيانات بنجاح!")

# ==================== رسائل يومية تلقائية ====================
async def daily_notification(context: ContextTypes.DEFAULT_TYPE):
    """إرسال إشعار يومي للمستخدمين"""
    users = get_all_users()
    message = f"""
🌅 **صباح الخير!**

💡 **نصيحة اليوم:** {random.choice(["استخدم كلمات مرور قوية", "حدّث تطبيقاتك", "احذر من التصيد الإلكتروني"])}

📚 **تذكير:** هناك دروس جديدة في منصة الوعي التقني.
🔗 تابعنا: {CHANNEL_ID}

كن جزءاً من المجتمع الرقمي الواعي! 🚀
    """
    
    for user_id in users[:50]:  # حد أقصى 50 رسالة في الدقيقة
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logging.error(f"فشل إرسال الإشعار لـ {user_id}: {e}")

# ==================== دوال مساعدة ====================
async def contact_admin(query):
    """التواصل مع المدير"""
    contact_text = """
📞 **تواصل مع المدير**

يمكنك التواصل مع المهندس أكرم الشرعبي عبر:

📧 **البريد الإلكتروني:** techawareness@gmail.com
📱 **تليجرام:** @Akram_Alsharabi
🌐 **الموقع:** www.techawareness.com

نحن هنا لمساعدتك! 💪
    """
    
    await query.edit_message_text(
        contact_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ])
    )

async def show_contact(query):
    """عرض معلومات التواصل"""
    await contact_admin(query)

# ==================== القائمة الرئيسية ====================
async def main_menu(query):
    """العودة للقائمة الرئيسية"""
    await start(query.message, None)

# ==================== بدء البوت ====================
def run_bot():
    """تشغيل البوت"""
    # تهيئة قاعدة البيانات
    init_db()
    
    # إعداد التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("stats", show_stats))
    
    # معالجات الأزرار
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # معالجات الرسائل (للبث الإذاعي)
    async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id in ADMIN_IDS:
            message = update.message.text
            users = get_all_users()
            count = 0
            for user_id in users:
                try:
                    await context.bot.send_message(chat_id=user_id, text=message)
                    count += 1
                except:
                    pass
            await update.message.reply_text(f"✅ تم إرسال الرسالة إلى {count} مستخدم.")
    
    application.add_handler(MessageHandler(filters.TEXT & filters.Chat(ADMIN_IDS), handle_broadcast))
    
    # جدولة الإشعارات اليومية (كل يوم الساعة 9 صباحاً)
    job_queue = application.job_queue
    job_queue.run_daily(
        daily_notification,
        time=datetime.strptime("09:00", "%H:%M").time()
    )
    
    # تشغيل البوت
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# ==================== تشغيل الكود ====================
if __name__ == "__main__":
    print("🚀 بدء تشغيل بوت الوعي التقني...")
    print("🤖 البوت يعمل الآن!")
    print(f"👑 المديرين: {ADMIN_IDS}")
    run_bot()
