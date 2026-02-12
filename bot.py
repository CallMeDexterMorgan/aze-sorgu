import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging
import os

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = '8253419019:AAFyrKgY_xv_5BMZ1BK5Hzr2HwFsSg_I7Ac'

# MySQL bağlantı ayarları
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # MySQL şifrənizi yazın
    'database': 'telebot_db',
    'charset': 'utf8mb4',
    'use_unicode': True
}

# SQL faylının yolu
SQL_FILE_PATH = r'C:\Users\Raul Xalilov\Downloads\Sagird.sql'

# MySQL-dən məlumatları çək
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"MySQL bağlantı xətası: {err}")
        return None

# SQL faylını oxu və bazaya əlavə et
def import_sql_file():
    try:
        if os.path.exists(SQL_FILE_PATH):
            with open(SQL_FILE_PATH, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                # Əvvəlcə database yoxdursa yarat
                cursor.execute("CREATE DATABASE IF NOT EXISTS telebot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.execute("USE telebot_db")
                
                # Table yarat
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id INT NOT NULL,
                        utis_code INT NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        first_name VARCHAR(50) NOT NULL,
                        last_name VARCHAR(50) NOT NULL,
                        birth_date DATE NOT NULL,
                        class VARCHAR(10) NOT NULL,
                        school VARCHAR(200) NOT NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                
                # SQL skriptini icra et
                for statement in sql_script.split(';'):
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except:
                            pass
                
                conn.commit()
                cursor.close()
                conn.close()
                logger.info("SQL faylı uğurla import edildi!")
                return True
        else:
            logger.error(f"SQL faylı tapılmadı: {SQL_FILE_PATH}")
            return False
    except Exception as e:
        logger.error(f"SQL import xətası: {e}")
        return False

# Start komandası
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # SQL faylını avtomatik import et
    import_sql_file()
    
    keyboard = [
        [InlineKeyboardButton("👤 Ad soyad sorğu", callback_data='search_name')],
        [InlineKeyboardButton("🔢 UTIS sorğu", callback_data='search_utis')],
        [InlineKeyboardButton("📱 Telefon sorğu", callback_data='search_phone')],
        [InlineKeyboardButton("🏫 Məktəb sorğu", callback_data='search_school')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🔍 *Sagird Sorğu Botuna Xoş Gəldiniz!*\n\n"
        "📊 *Cari Məlumatlar:*\n"
        "• SQL faylı avtomatik yükləndi\n"
        "• Baza bağlantısı quruldu\n\n"
        "🔽 *Aşağıdakı sorğu növlərindən birini seçin:*\n\n"
        "👤 Ad soyad ilə axtarış\n"
        "🔢 UTIS kodu ilə axtarış\n"
        "📱 Telefon nömrəsi ilə axtarış\n"
        "🏫 Məktəb adı ilə axtarış"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Buton callback handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    search_type = query.data
    
    # Sorğu tipini yadda saxla
    context.user_data['search_type'] = search_type
    
    messages = {
        'search_name': "👤 *Ad və Soyad daxil edin:*\nMəsələn: `Ruxsarə Abbasova` və ya `Ruxsarə`",
        'search_utis': "🔢 *UTIS kodunu daxil edin:*\nMəsələn: `2829617`",
        'search_phone': "📱 *Telefon nömrəsini daxil edin:*\nMəsələn: `+994993458060` və ya `993458060`",
        'search_school': "🏫 *Məktəb adını daxil edin:*\nMəsələn: `14 nömrəli` və ya `Nəsimi`"
    }
    
    await query.edit_message_text(
        messages.get(search_type, "Məlumat daxil edin:"),
        parse_mode='Markdown'
    )

# Mesaj handler (sorğu üçün)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'search_type' not in context.user_data:
        keyboard = [[InlineKeyboardButton("🔍 Yeni sorğu", callback_data='new_search')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ Zəhmət olmasa əvvəlcə /start edin və sorğu növü seçin!",
            reply_markup=reply_markup
        )
        return
    
    search_type = context.user_data['search_type']
    search_text = update.message.text.strip()
    
    if not search_text:
        await update.message.reply_text("❌ Zəhmət olmasa axtarış üçün məlumat daxil edin!")
        return
    
    waiting_msg = await update.message.reply_text("🔄 Axtarılır, zəhmət olmasa gözləyin...")
    
    # Sorğu növünə görə axtarış
    if search_type == 'search_name':
        results = search_by_name(search_text)
    elif search_type == 'search_utis':
        results = search_by_utis(search_text)
    elif search_type == 'search_phone':
        results = search_by_phone(search_text)
    elif search_type == 'search_school':
        results = search_by_school(search_text)
    else:
        results = []
    
    # Gözləmə mesajını sil
    await waiting_msg.delete()
    
    # Nəticələri göstər
    if results:
        result_count = len(results)
        await update.message.reply_text(f"✅ *{result_count} nəticə tapıldı*", parse_mode='Markdown')
        
        for i, student in enumerate(results[:5], 1):  # Maksimum 5 nəticə
            message = format_student_info(student, i)
            await update.message.reply_text(message, parse_mode='Markdown')
        
        if len(results) > 5:
            await update.message.reply_text(
                f"📊 *Cəmi {result_count} nəticə tapıldı.*\n"
                f"İlk 5 nəticə göstərildi.\n"
                f"Daha dəqiq axtarış üçün tam ad və ya kod daxil edin.",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(
            "❌ *Heç bir nəticə tapılmadı!*\n\n"
            "Məsləhətlər:\n"
            "• Tam ad yazmağa çalışın\n"
            "• Düzgün UTIS kodu daxil edin\n"
            "• Telefon nömrəsini +994 ilə yazın\n"
            "• Məktəb adının düzgün yazılışına diqqət edin",
            parse_mode='Markdown'
        )
    
    # Yeni sorğu üçün menyu
    await show_search_menu(update, context)

# Ad soyad ilə axtarış
def search_by_name(name):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    parts = name.split()
    
    if len(parts) >= 2:
        # Tam ad axtarışı
        query = """
            SELECT * FROM students 
            WHERE first_name LIKE %s AND last_name LIKE %s
            ORDER BY last_name, first_name
        """
        cursor.execute(query, (f'%{parts[0]}%', f'%{parts[1]}%'))
    else:
        # Tək söz axtarışı
        query = """
            SELECT * FROM students 
            WHERE first_name LIKE %s OR last_name LIKE %s
            ORDER BY last_name, first_name
        """
        cursor.execute(query, (f'%{name}%', f'%{name}%'))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# UTIS kodu ilə axtarış
def search_by_utis(utis_code):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    # Tam uyğunluq axtarışı
    if utis_code.isdigit():
        cursor.execute("SELECT * FROM students WHERE utis_code = %s", (utis_code,))
    else:
        cursor.execute("SELECT * FROM students WHERE utis_code LIKE %s", (f'%{utis_code}%',))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Telefon ilə axtarış
def search_by_phone(phone):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    # Telefon nömrəsini təmizlə
    phone_clean = phone.replace(' ', '').replace('-', '')
    
    cursor.execute("SELECT * FROM students WHERE phone LIKE %s", (f'%{phone_clean}%',))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Məktəb adı ilə axtarış
def search_by_school(school):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE school LIKE %s ORDER BY school", (f'%{school}%',))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Şagird məlumatlarını formatla
def format_student_info(student, index=1):
    return (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📋 *Nəticə {index}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *Sıra nömrəsi:* `{student['student_id']}`\n"
        f"🔢 *UTIS kodu:* `{student['utis_code']}`\n"
        f"📞 *Telefon:* `{student['phone']}`\n"
        f"👤 *Ad:* {student['first_name']}\n"
        f"👤 *Soyad:* {student['last_name']}\n"
        f"🎂 *Doğum tarixi:* {student['birth_date']}\n"
        f"📚 *Sinif:* {student['class']}\n"
        f"🏫 *Məktəb:* {student['school']}\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

# Axtarış menyusunu göstər
async def show_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🆕 Yeni sorğu", callback_data='new_search')],
        [InlineKeyboardButton("🏠 Əsas menyu", callback_data='main_menu')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            "📋 *Növbəti əməliyyat seçin:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.message.reply_text(
            "📋 *Növbəti əməliyyat seçin:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# Əsas menyunu göstər
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👤 Ad soyad sorğu", callback_data='search_name')],
        [InlineKeyboardButton("🔢 UTIS sorğu", callback_data='search_utis')],
        [InlineKeyboardButton("📱 Telefon sorğu", callback_data='search_phone')],
        [InlineKeyboardButton("🏫 Məktəb sorğu", callback_data='search_school')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            "📋 *Əsas Menyu*\nSorğu növü seçin:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.message.reply_text(
            "📋 *Əsas Menyu*\nSorğu növü seçin:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# Yeni sorğu
async def new_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    await show_main_menu(update, context)

# Kömək komandası
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🔍 *Sagird Sorğu Botu - Kömək*\n\n"
        "*📌 Əsas Əmrlər:*\n"
        "/start - Botu işə sal və SQL faylını yüklə\n"
        "/help - Bu kömək menyusunu göstər\n"
        "/menu - Əsas menyuya qayıt\n"
        "/stats - Baza statistikası\n\n"
        "*🔎 Sorğu növləri:*\n"
        "• 👤 Ad və soyad ilə axtarış\n"
        "• 🔢 UTIS kodu ilə axtarış\n"
        "• 📱 Telefon nömrəsi ilə axtarış\n"
        "• 🏫 Məktəb adı ilə axtarış\n\n"
        "*💡 Məsləhətlər:*\n"
        "• Daha dəqiq nəticə üçün tam ad yazın\n"
        "• UTIS kodunu tam daxil edin\n"
        "• Telefon nömrəsini +994 ilə yazın\n\n"
        f"📊 *SQL faylı:* `{SQL_FILE_PATH}`"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Statistik komandası
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    if not conn:
        await update.message.reply_text("❌ Baza bağlantısı qurula bilmədi!")
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT school) FROM students")
    total_schools = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    stats_text = (
        "📊 *Baza Statistikası*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Ümumi şagird sayı: `{total_students}`\n"
        f"🏫 Məktəb sayı: `{total_schools}`\n"
        f"📁 SQL faylı: `{os.path.basename(SQL_FILE_PATH)}`\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# Menu komandası
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# Ana funksiya
def main():
    # Bot application yarat
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlerları əlavə et
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^search_'))
    application.add_handler(CallbackQueryHandler(new_search, pattern='^new_search$'))
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern='^main_menu$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("🤖 Sagird Sorğu Botu işə düşdü...")
    print(f"📁 SQL faylı: {SQL_FILE_PATH}")
    print("✅ Bot hazırdır! Telegram-da @ botunuzu test edin.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
