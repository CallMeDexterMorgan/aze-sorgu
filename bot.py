import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging
import os
import asyncio

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
                
                # Database yarat
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
                
                # Mövcud məlumatları təmizlə
                cursor.execute("DELETE FROM students")
                
                # SQL skriptini parse et
                lines = sql_script.strip().split('\n')
                insert_started = False
                
                for line in lines:
                    line = line.strip()
                    if 'INSERT INTO' in line.upper():
                        insert_started = True
                        continue
                    if insert_started and line.startswith('('):
                        try:
                            # Məlumatları parse et
                            line = line.rstrip(',').rstrip(';')
                            values = eval(line)
                            
                            if isinstance(values, tuple) and len(values) >= 8:
                                student_id = values[0] if values[0] != 'NULL' else 0
                                utis_code = values[1] if values[1] != 'NULL' else 0
                                phone = values[2] if values[2] != 'NULL' else ''
                                first_name = values[3] if values[3] != 'NULL' else ''
                                last_name = values[4] if values[4] != 'NULL' else ''
                                birth_date = values[5] if values[5] != 'NULL' else '2000-01-01'
                                class_name = values[6] if values[6] != 'NULL' else ''
                                school = values[7] if values[7] != 'NULL' else ''
                                
                                insert_query = """
                                    INSERT INTO students 
                                    (student_id, utis_code, phone, first_name, last_name, birth_date, class, school) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """
                                cursor.execute(insert_query, (
                                    student_id, utis_code, phone, 
                                    first_name, last_name, birth_date, 
                                    class_name, school
                                ))
                        except Exception as e:
                            logger.error(f"Xəta: {e}, Sətir: {line}")
                
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
    # SQL faylını import et
    await update.message.reply_text("🔄 SQL faylı yüklənir...")
    
    try:
        if import_sql_file():
            await update.message.reply_text("✅ SQL faylı uğurla yükləndi!")
        else:
            await update.message.reply_text("⚠️ SQL faylı yüklənərkən xəta baş verdi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xəta: {str(e)}")
    
    keyboard = [
        [InlineKeyboardButton("👤 Ad soyad sorğu", callback_data='search_name')],
        [InlineKeyboardButton("🔢 UTIS sorğu", callback_data='search_utis')],
        [InlineKeyboardButton("📱 Telefon sorğu", callback_data='search_phone')],
        [InlineKeyboardButton("🏫 Məktəb sorğu", callback_data='search_school')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🔍 *Sagird Sorğu Botuna Xoş Gəldiniz!*\n\n"
        "🔽 *Sorğu növlərindən birini seçin:*\n\n"
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
    context.user_data['search_type'] = search_type
    
    messages = {
        'search_name': "👤 *Ad və Soyad daxil edin:*\nMəsələn: `Ruxsarə Abbasova`",
        'search_utis': "🔢 *UTIS kodunu daxil edin:*\nMəsələn: `2829617`",
        'search_phone': "📱 *Telefon nömrəsini daxil edin:*\nMəsələn: `+994993458060`",
        'search_school': "🏫 *Məktəb adını daxil edin:*\nMəsələn: `Nəsimi rayonu 14 nömrəli`"
    }
    
    await query.edit_message_text(
        messages.get(search_type, "Məlumat daxil edin:"),
        parse_mode='Markdown'
    )

# Mesaj handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'search_type' not in context.user_data:
        keyboard = [[InlineKeyboardButton("🔍 Yeni sorğu", callback_data='new_search')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ Əvvəlcə /start edin və sorğu növü seçin!",
            reply_markup=reply_markup
        )
        return
    
    search_type = context.user_data['search_type']
    search_text = update.message.text.strip()
    
    if not search_text:
        await update.message.reply_text("❌ Axtarış üçün məlumat daxil edin!")
        return
    
    await update.message.reply_text("🔄 Axtarılır...")
    
    # Axtarış
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
    
    # Nəticələr
    if results:
        await update.message.reply_text(f"✅ {len(results)} nəticə tapıldı")
        
        for i, student in enumerate(results[:5], 1):
            message = format_student_info(student, i)
            await update.message.reply_text(message, parse_mode='Markdown')
        
        if len(results) > 5:
            await update.message.reply_text(f"📊 Cəmi {len(results)} nəticə. İlk 5 göstərildi.")
    else:
        await update.message.reply_text("❌ Heç bir nəticə tapılmadı!")
    
    # Yeni sorğu menyusu
    await show_search_menu(update, context)

# Axtarış funksiyaları
def search_by_name(name):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    parts = name.split()
    
    if len(parts) >= 2:
        cursor.execute(
            "SELECT * FROM students WHERE first_name LIKE %s AND last_name LIKE %s",
            (f'%{parts[0]}%', f'%{parts[1]}%')
        )
    else:
        cursor.execute(
            "SELECT * FROM students WHERE first_name LIKE %s OR last_name LIKE %s",
            (f'%{name}%', f'%{name}%')
        )
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def search_by_utis(utis_code):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE utis_code = %s", (utis_code,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def search_by_phone(phone):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE phone LIKE %s", (f'%{phone}%',))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def search_by_school(school):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE school LIKE %s", (f'%{school}%',))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def format_student_info(student, index=1):
    return (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📋 *Nəticə {index}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: `{student['student_id']}`\n"
        f"🔢 UTIS: `{student['utis_code']}`\n"
        f"📞 Telefon: `{student['phone']}`\n"
        f"👤 Ad: {student['first_name']}\n"
        f"👤 Soyad: {student['last_name']}\n"
        f"🎂 Doğum: {student['birth_date']}\n"
        f"📚 Sinif: {student['class']}\n"
        f"🏫 Məktəb: {student['school']}\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

async def show_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🆕 Yeni sorğu", callback_data='new_search')],
        [InlineKeyboardButton("🏠 Əsas menyu", callback_data='main_menu')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📋 *Növbəti əməliyyat seçin:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👤 Ad soyad sorğu", callback_data='search_name')],
        [InlineKeyboardButton("🔢 UTIS sorğu", callback_data='search_utis')],
        [InlineKeyboardButton("📱 Telefon sorğu", callback_data='search_phone')],
        [InlineKeyboardButton("🏫 Məktəb sorğu", callback_data='search_school')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query = update.callback_query
    if query:
        await query.message.reply_text(
            "📋 *Əsas Menyu*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📋 *Əsas Menyu*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def new_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await show_main_menu(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🔍 *Sagird Sorğu Botu - Kömək*\n\n"
        "/start - Botu işə sal\n"
        "/help - Kömək\n\n"
        f"📁 SQL faylı: `{os.path.basename(SQL_FILE_PATH)}`"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

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
        f"👥 Şagird sayı: `{total_students}`\n"
        f"🏫 Məktəb sayı: `{total_schools}`"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')

def main():
    """Botu işə sal"""
    try:
        # Application yarat
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Handlerları əlavə et
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CallbackQueryHandler(button_handler, pattern='^search_'))
        application.add_handler(CallbackQueryHandler(new_search, pattern='^new_search$'))
        application.add_handler(CallbackQueryHandler(show_main_menu, pattern='^main_menu$'))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        print("🤖 Bot işə düşdü!")
        print(f"📁 SQL faylı: {SQL_FILE_PATH}")
        print("✅ Bot hazırdır!")
        
        # Polling başlat
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Xəta: {e}")
        print(f"❌ Xəta: {e}")

if __name__ == '__main__':
    main()
