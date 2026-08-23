import csv
import io
import json
import logging
import os
import random
import sqlite3
import string
from datetime import datetime, timedelta
from threading import Thread

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# ==================== الإعدادات ====================

TOKEN = os.environ.get("BOT_TOKEN", "")

ADMIN_IDS = [
    int(user_id.strip())
    for user_id in os.environ.get("ADMIN_IDS", "").split(",")
    if user_id.strip().isdigit()
]

CHANNEL_ID = os.environ.get("CHANNEL_ID", "")

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is required. Set it as an environment variable."
    )

DB_NAME = "tech_awareness.db"


# ==================== قاعدة البيانات ====================

def init_db():
    """إنشاء قاعدة البيانات والجداول."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
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
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            options TEXT,
            correct_answer TEXT,
            category TEXT,
            difficulty TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            quiz_id INTEGER,
            score INTEGER,
            date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            date TEXT,
            sent INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# ==================== المستخدمون ====================

def add_user(user_id, username, first_name, last_name):
    """إضافة مستخدم أو تحديث بياناته."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT OR REPLACE INTO users
        (user_id, username, first_name, last_name, join_date, last_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        username,
        first_name,
        last_name,
        now,
        now,
    ))

    conn.commit()
    conn.close()


def get_user(user_id):
    """جلب بيانات مستخدم."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    )

    user = cursor.fetchone()
    conn.close()

    return user


def get_all_users():
    """جلب أرقام جميع المستخدمين."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    conn.close()

    return [user[0] for user in users]


def update_points(user_id, points):
    """تحديث نقاط المستخدم."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET points = points + ? WHERE user_id = ?",
        (points, user_id),
    )

    conn.commit()
    conn.close()


# ==================== الأمر الرئيسي ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت."""
    user = update.effective_user

    if not user:
        return

    add_user(
        user.id,
        user.username,
        user.first_name,
        user.last_name,
    )

    welcome_text = """
👋 **أهلاً بك في بوت منصة الوعي التقني**

📚 **الخدمات المتاحة:**

• مجالات تقنية مختلفة
• اختبارات تفاعلية
• معلومات وأخبار تقنية
• نصائح يومية

اختر الخدمة التي تريدها من القائمة:
"""

    keyboard = [
        [
            InlineKeyboardButton(
                "📚 المجالات",
                callback_data="categories",
            )
        ],
        [
            InlineKeyboardButton(
                "📝 اختبار تفاعلي",
                callback_data="quiz",
            )
        ],
        [
            InlineKeyboardButton(
                "📰 آخر الأخبار",
                callback_data="news",
            )
        ],
        [
            InlineKeyboardButton(
                "📞 تواصل",
                callback_data="contact",
            )
        ],
    ]

    if CHANNEL_ID:
        keyboard.insert(
            3,
            [
                InlineKeyboardButton(
                    "👥 المجتمع",
                    url=CHANNEL_ID,
                )
            ],
        )

    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==================== الأزرار ====================

async def handle_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """معالجة الأزرار."""
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
        if quiz_id.isdigit():
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


# ==================== المجالات ====================

async def show_categories(query):
    """عرض المجالات."""
    categories_text = """
📚 **المجالات التعليمية**

اختر المجال الذي تريد التعرف عليه:
"""

    keyboard = [
        [
            InlineKeyboardButton(
                "🛡️ الأمن السيبراني",
                callback_data="cat_cyber",
            )
        ],
        [
            InlineKeyboardButton(
                "🌐 الشبكات",
                callback_data="cat_networks",
            )
        ],
        [
            InlineKeyboardButton(
                "💻 البرمجة",
                callback_data="cat_programming",
            )
        ],
        [
            InlineKeyboardButton(
                "🤖 الذكاء الاصطناعي",
                callback_data="cat_ai",
            )
        ],
        [
            InlineKeyboardButton(
                "🔹 تقنية المعلومات",
                callback_data="cat_it",
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 رجوع",
                callback_data="main_menu",
            )
        ],
    ]

    await query.edit_message_text(
        categories_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==================== التواصل ====================

async def contact_admin(query):
    """عرض معلومات التواصل العامة."""
    contact_text = """
📞 **التواصل**

للاستفسارات والملاحظات، استخدم وسائل التواصل المتاحة في المنصة.

يمكن تحديث معلومات التواصل من إعدادات المشروع دون تعديل الكود.
"""

    await query.edit_message_text(
        contact_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 رجوع",
                    callback_data="main_menu",
                )
            ]
        ]),
    )


async def show_contact(query):
    """عرض صفحة التواصل."""
    await contact_admin(query)


# ==================== التشغيل ====================

def run_bot():
    """تشغيل البوت."""
    init_db()

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(handle_callback)
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    print("بدء تشغيل البوت...")
    run_bot()
