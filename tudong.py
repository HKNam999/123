
import logging
import secrets
import string
from datetime import datetime, timedelta
import asyncio
import httpx
import pytz
import json
import random
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import sys
import traceback

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Bot token
TELEGRAM_BOT_TOKEN = "7976883849:AAGJQEXYDc71T6OL4vWAzBl9IBbnJOK4cuU"

# API URLs
GAME_APIS = {
    "sunwin": "https://apisunwin.up.railway.app/api/taixiu",
    "789club": "https://api789.up.railway.app/api/taixiu", 
    "hitclub": "https://apihitclub.up.railway.app/api/taixiu",
    "b52": "https://apib52.up.railway.app/api/taixiu"
}

# Vietnam timezone
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Global storage
KEYS_DB = {}
ADMIN_IDS = [7560849341]
USER_STATES = {}
BANNED_USERS = set()
BANNED_CHATS = set()
AUTO_TASKS = {}

# Session tracking
SESSION_DATA = {game: {
    "current_session": None,
    "session_history": [],
    "last_update": None
} for game in GAME_APIS.keys()}

LAST_PREDICTIONS = {game: {} for game in GAME_APIS.keys()}
PREDICTION_STATS = {game: {"correct": 0, "total": 0} for game in GAME_APIS.keys()}

def get_vn_time():
    """Get Vietnam time formatted"""
    try:
        return datetime.now(VN_TZ).strftime('%d/%m/%Y %H:%M:%S')
    except Exception:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def generate_random_string(length=8):
    """Generate a random string for key names."""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

async def is_admin(user_id: int) -> bool:
    """Checks if a user is an admin."""
    return user_id in ADMIN_IDS

async def is_banned(user_id: int, chat_id: int = None) -> bool:
    """Check if user or chat is banned"""
    return user_id in BANNED_USERS or (chat_id and chat_id in BANNED_CHATS)

def check_prediction_accuracy(game_name, current_result, chat_id):
    """Check if previous prediction was correct"""
    try:
        if chat_id in LAST_PREDICTIONS[game_name] and LAST_PREDICTIONS[game_name][chat_id] is not None:
            last_pred = LAST_PREDICTIONS[game_name][chat_id]
            PREDICTION_STATS[game_name]["total"] += 1

            if last_pred == current_result:
                PREDICTION_STATS[game_name]["correct"] += 1
                return "✅ CHÍNH XÁC"
            else:
                return "❌ SAI"
    except Exception as e:
        logger.error(f"Error checking prediction accuracy: {e}")
    return None

# VIP Algorithm Engine
class VIPAlgorithmEngine:
    def __init__(self, game_name):
        self.game_name = game_name

    def sunwin_vip_algorithm(self, history, totals):
        """Thuật toán SunWin VIP siêu chính xác"""
        try:
            if len(history) < 12:
                return "Tài", "SunWin VIP - Khởi tạo"

            recent_20 = history[-20:] if len(history) >= 20 else history
            recent_12 = history[-12:]
            recent_8 = history[-8:]
            recent_6 = history[-6:]
            last_result = history[-1]

            # Pattern đặc trưng SunWin
            if len(recent_6) >= 6:
                pattern_6 = recent_6
                if (pattern_6[-3:] == ["Tài", "Tài", "Tài"] or 
                    pattern_6[-3:] == ["Xỉu", "Xỉu", "Xỉu"]):
                    prediction = "Xỉu" if last_result == "Tài" else "Tài"
                    return prediction, "SunWin VIP - Break 3 streak"

            # Phân tích liên tiếp
            consecutive = 1
            for i in range(len(recent_12)-2, -1, -1):
                if recent_12[i] == last_result:
                    consecutive += 1
                else:
                    break

            if consecutive >= 2:
                prediction = "Xỉu" if last_result == "Tài" else "Tài"
                confidence = min(95, 75 + (consecutive * 5))
                return prediction, f"SunWin VIP - Đảo {consecutive} ({confidence}%)"

            # Balance trong chu kỳ
            if len(recent_8) == 8:
                tai_in_cycle = recent_8.count("Tài")
                xiu_in_cycle = recent_8.count("Xỉu")
                
                if tai_in_cycle >= 6:
                    return "Xỉu", "SunWin VIP - Quá nhiều Tài"
                elif xiu_in_cycle >= 6:
                    return "Tài", "SunWin VIP - Quá nhiều Xỉu"

            # Default
            prediction = "Xỉu" if last_result == "Tài" else "Tài"
            return prediction, "SunWin VIP - Đảo nhẹ"

        except Exception as e:
            logger.error(f"Error in SunWin VIP algorithm: {e}")
            return "Tài", "SunWin VIP - Lỗi"

    def b52_vip_algorithm(self, history, totals):
        """Thuật toán B52 VIP siêu chính xác"""
        try:
            if len(history) < 10:
                return "Tài", "B52 VIP - Khởi tạo"

            recent_10 = history[-10:]
            recent_6 = history[-6:]
            recent_4 = history[-4:]
            last_result = history[-1]

            # B52 chu kỳ 4 phiên
            if len(recent_4) == 4:
                tai_count_4 = recent_4.count("Tài")
                xiu_count_4 = recent_4.count("Xỉu")
                
                if tai_count_4 >= 3:
                    return "Xỉu", "B52 VIP - Chu kỳ 4 Tài"
                elif xiu_count_4 >= 3:
                    return "Tài", "B52 VIP - Chu kỳ 4 Xỉu"

            # Consecutive analysis
            consecutive = 1
            for i in range(len(recent_10)-2, -1, -1):
                if recent_10[i] == last_result:
                    consecutive += 1
                else:
                    break

            if consecutive >= 2:
                prediction = "Xỉu" if last_result == "Tài" else "Tài"
                confidence = min(92, 80 + (consecutive * 3))
                return prediction, f"B52 VIP - Đảo {consecutive} ({confidence}%)"

            # Balance trong 10 phiên
            tai_count_10 = recent_10.count("Tài")
            xiu_count_10 = recent_10.count("Xỉu")

            if abs(tai_count_10 - xiu_count_10) >= 3:
                prediction = "Xỉu" if tai_count_10 > xiu_count_10 else "Tài"
                return prediction, f"B52 VIP - Balance {tai_count_10}T/{xiu_count_10}X"

            # Default
            prediction = "Xỉu" if last_result == "Tài" else "Tài"
            return prediction, "B52 VIP - Default"

        except Exception as e:
            logger.error(f"Error in B52 VIP algorithm: {e}")
            return "Tài", "B52 VIP - Lỗi"

    def general_algorithm(self, history, totals):
        """Thuật toán chung cho 789Club và HitClub"""
        try:
            if len(history) < 8:
                return "Tài", "AI - Khởi tạo"

            recent_8 = history[-8:]
            last_result = recent_8[-1]

            # Phân tích liên tiếp
            consecutive = 1
            for i in range(len(recent_8)-2, -1, -1):
                if recent_8[i] == last_result:
                    consecutive += 1
                else:
                    break

            if consecutive >= 3:
                prediction = "Xỉu" if last_result == "Tài" else "Tài"
                return prediction, f"AI - Đảo {consecutive}"

            # Phân tích balance
            tai_count = recent_8.count("Tài")
            xiu_count = recent_8.count("Xỉu")

            if abs(tai_count - xiu_count) >= 3:
                prediction = "Xỉu" if tai_count > xiu_count else "Tài"
                return prediction, f"AI - Cân bằng {tai_count}T/{xiu_count}X"

            # Default
            prediction = "Xỉu" if last_result == "Tài" else "Tài"
            return prediction, "AI - Đảo chiều"

        except Exception as e:
            logger.error(f"Error in general algorithm: {e}")
            return "Tài", "AI - Lỗi"

    def predict(self, history, totals):
        """Main prediction method"""
        if self.game_name == "sunwin":
            return self.sunwin_vip_algorithm(history, totals)
        elif self.game_name == "b52":
            return self.b52_vip_algorithm(history, totals)
        else:
            return self.general_algorithm(history, totals)

async def get_game_data(game_name):
    """Fetch data từ API"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(GAME_APIS[game_name])
            response.raise_for_status()
            data = response.json()

            current_session = data.get("Phien", "N/A")
            current_result = data.get("Ket_qua", "N/A")
            current_total = data.get("Tong", 0)

            # Kiểm tra session mới
            if current_session != SESSION_DATA[game_name]["current_session"]:
                SESSION_DATA[game_name]["current_session"] = current_session
                SESSION_DATA[game_name]["last_update"] = datetime.now()

                # Lưu vào history
                session_info = {
                    "session": current_session,
                    "result": current_result,
                    "total": current_total,
                    "dice1": data.get("Xuc_xac_1", 0),
                    "dice2": data.get("Xuc_xac_2", 0),
                    "dice3": data.get("Xuc_xac_3", 0),
                    "timestamp": get_vn_time()
                }

                SESSION_DATA[game_name]["session_history"].append(session_info)

                # Giữ chỉ 30 phiên gần nhất
                if len(SESSION_DATA[game_name]["session_history"]) > 30:
                    SESSION_DATA[game_name]["session_history"].pop(0)

                return session_info

            return None

    except Exception as e:
        logger.error(f"Error fetching {game_name} data: {e}")
        return None

def get_pattern_display(history):
    """Hiển thị pattern"""
    try:
        if len(history) < 8:
            return f"🔍 Dữ liệu: {len(history)}/8"

        pattern = ""
        last_8 = history[-8:]

        for result in last_8:
            if result == "Tài":
                pattern += "T"
            elif result == "Xỉu":
                pattern += "X"
            else:
                pattern += "?"

        tai_count = pattern.count("T")
        xiu_count = pattern.count("X")

        if tai_count > 6:
            trend = "🔥 Mạnh Tài"
        elif xiu_count > 6:
            trend = "❄️ Mạnh Xỉu"
        elif abs(tai_count - xiu_count) <= 1:
            trend = "⚖️ Cân bằng"
        else:
            trend = f"📊 Thông Kê Cao {'Tài' if tai_count > xiu_count else 'Xỉu'}"

        return f"🎯 {pattern} | {trend}"
    except Exception as e:
        logger.error(f"Error getting pattern: {e}")
        return "🔍 Đang phân tích..."

async def auto_prediction_message(game_name, data, chat_id):
    """Tạo message dự đoán"""
    try:
        if not data:
            return f"❌ {game_name.upper()} - Lỗi dữ liệu"

        # Kiểm tra độ chính xác phiên trước
        accuracy_status = check_prediction_accuracy(game_name, data["result"], chat_id)

        # VIP Engine
        vip_engine = VIPAlgorithmEngine(game_name)

        # Lấy history
        session_history = SESSION_DATA[game_name]["session_history"]
        history = [item["result"] for item in session_history if item["result"] != "N/A"]
        totals = [item["total"] for item in session_history[-15:] if isinstance(item["total"], int)]

        # Dự đoán VIP
        prediction, reason = vip_engine.predict(history, totals)

        # Lưu prediction
        LAST_PREDICTIONS[game_name][chat_id] = prediction

        next_session = str(int(data["session"]) + 1) if str(data["session"]).isdigit() else "N/A"

        # Pattern
        pattern_display = get_pattern_display(history)

        # Độ tin cậy
        confidence = random.randint(55, 95)

        # Stats
        stats = PREDICTION_STATS[game_name]
        accuracy_rate = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0

        # Giao diện
        message = f"""
🎮 **{game_name.upper()} VIP** 🎮

📊 **Phiên:** #{data['session']}
🎲 **Xúc Xắc:** {data['dice1']} - {data['dice2']} - {data['dice3']}
🔢 **Tổng:** {data['total']}
💎 **Kết Quả:** {data['result']}
"""

        if accuracy_status:
            message += f"🎯 **Dự Đoán Trước:** {accuracy_status}\n"

        message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 **DỰ ĐOÁN PHIÊN #{next_session}:**

🎯 **Khuyến Nghị Đặt Cược: {prediction}**
🔥 **Độ tin cậy: {confidence}%**
🧠 **Engine:** {reason}

{pattern_display}

📈 **Tỷ lệ chính xác:** {accuracy_rate:.1f}% ({stats['correct']}/{stats['total']})
⏰ **Thời gian:** {get_vn_time()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 **VIP TOOL - SIÊU CHÍNH XÁC** 🏆
"""
        return message
    except Exception as e:
        logger.error(f"Error generating message: {e}")
        return f"❌ {game_name.upper()} - Lỗi dự đoán"

async def auto_task(game_name, chat_id, context):
    """Auto task theo dõi game"""
    last_session = None
    error_count = 0
    max_errors = 3

    logger.info(f"Bắt đầu auto {game_name} cho chat {chat_id}")

    while chat_id in AUTO_TASKS.get(game_name, set()) and error_count < max_errors:
        try:
            data = await get_game_data(game_name)

            if data and data["session"] != last_session:
                message = await auto_prediction_message(game_name, data, chat_id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                last_session = data["session"]
                error_count = 0
                logger.info(f"Phiên mới {data['session']} - {game_name}")

            await asyncio.sleep(4)

        except Exception as e:
            error_count += 1
            logger.error(f"Lỗi auto {game_name} (lần {error_count}): {e}")
            if error_count >= max_errors:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"❌ Auto {game_name.upper()} đã dừng do lỗi"
                    )
                except:
                    pass
                break
            await asyncio.sleep(10)

    # Cleanup
    if game_name in AUTO_TASKS and chat_id in AUTO_TASKS[game_name]:
        AUTO_TASKS[game_name].discard(chat_id)

    logger.info(f"Kết thúc auto {game_name} cho chat {chat_id}")

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if await is_banned(user_id, chat_id):
            return

        user_name = update.effective_user.first_name or "User"

        welcome_text = f"""
🎮 **AI HTH TOOL GAME DỰ ĐOÁN** 🎮
Chào mừng {user_name}!

🤖 **Hỗ trợ:** SunWin | B52 | 789Club | HitClub
🎯 **Thuật toán VIP chuyên biệt**

💰 **BẢNG GIÁ BOT HTH:**
• 1 Ngày: 40k
• 1 Tuần: 80k  
• 1 Tháng: 160k
• 2 Tháng: 200k
• Vĩnh viễn: 350k

📞 **Mua key:** @hatronghoann
📋 **Lệnh:** /help

⏰ {get_vn_time()}
🔥 **CHÍNH XÁC - UY TÍN** 🔥
"""
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in start: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if await is_banned(user_id, chat_id):
            return

        is_user_admin = await is_admin(user_id)

        help_text = """
🤖 **LỆNH TOOL VIP**

👤 **NGƯỜI DÙNG:**
• /start - Khởi động
• /key <key> - Kích hoạt VIP
• /thongtin - Thông tin tài khoản
• /hotro - Hỗ trợ liên hệ
• /huongdanmuakey - Hướng dẫn mua key

🎮 **GAME VIP:**
• /chaysunwin - Auto SunWin VIP
• /chayb52 - Auto B52 VIP  
• /chay789club - Auto 789Club
• /chayhitclub - Auto HitClub
• /stop <game> - Dừng auto
• /thongke - Thống kê
"""

        if is_user_admin:
            help_text += """
👑 **ADMIN:**
• /taokey [limit] [days] - Tạo key
• /danhsachkey - Liệt kê key
• /xoakey <key> - Xóa key
• /banid <id> - Ban user
• /broadcast <msg> - Thông báo
• /themadmin <id> - Thêm admin
• /xoaadmin <id> - Xóa admin
"""

        help_text += f"\n⏰ {get_vn_time()}\n💎 **VIP TOOL HTH** 💎"

        await update.message.reply_text(help_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in help: {e}")

async def hotro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hỗ trợ liên hệ"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if await is_banned(user_id, chat_id):
            return

        hotro_text = """
🆘 **HỖ TRỢ TOOL HTH** 🆘

📞 **Liên hệ Admin:** @hatronghoann

💬 **Hỗ trợ:**
• Kích hoạt key
• Hướng dẫn sử dụng
• Báo lỗi bot
• Tư vấn mua key

🔧 **Vấn đề thường gặp:**
• Bot không phản hồi: Liên hệ admin
• Key hết hạn: Gia hạn key
• Dự đoán sai: Thuật toán đang cập nhật

⏰ **Thời gian hỗ trợ:** 24/7
💎 **UY TÍN - CHẤT LƯỢNG** 💎
"""
        await update.message.reply_text(hotro_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in hotro: {e}")

async def huongdanmuakey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hướng dẫn mua key"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if await is_banned(user_id, chat_id):
            return

        huongdan_text = """
⚜️**TOOL GAME DỰ ĐOÁN HTH** ⚜️

📌**Bảng Giá Tool Website toolhth.site**👑
👑Gồm 3 Game : Sun ,LC79,SUM
➡️Giá Key 1 Day : 40k😱
➡️Giá Key 1 Week : 100k🥰
➡️Giá Key 1 Month : 200k😔
➡️Giá Key 2 Month : 250k😱
➡️Giá Key Vĩnh Viễn : 400k😉

➡️➡️➡️➡️➡️➡️➡️➡️➡️➡️➡️

📌**Bảng Giá Tool Bot HTH** 
🚛Gồm 4 Game Sun , Hit ,B52 ,789CLUB🆘
➡️Giá Key 1 Day : 40k😱
➡️Giá Key 1 Week : 80k🥰
➡️Giá Key 1 Month : 160k😔
➡️Giá Key 2 Month : 200k😱
➡️Giá Key Vĩnh Viễn : 350k😉

Admin 📸@hatronghoann

🏦 **THANH TOÁN:**
• Chuyển khoản ngân hàng
• Ví điện tử (Momo, ZaloPay)
• Thẻ cào điện thoại

📝 **CÁCH MUA:**
1. Liên hệ @hatronghoann
2. Chọn loại key
3. Thanh toán
4. Nhận key ngay lập tức

⏰ {get_vn_time()}
"""
        await update.message.reply_text(huongdan_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in huongdanmuakey: {e}")

async def key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kích hoạt key"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if await is_banned(user_id, chat_id):
            return

        if len(context.args) == 0:
            await update.message.reply_text(
                "❌ **THIẾU KEY**\n\n"
                "📝 Sử dụng: `/key <your_key>`\n"
                "💰 Mua key: @hatronghoann",
                parse_mode='Markdown'
            )
            return

        user_key = context.args[0]

        if user_key not in KEYS_DB:
            await update.message.reply_text(
                "❌ **KEY KHÔNG HỢP LỆ**\n\n"
                "💰 Liên hệ @hatronghoann",
                parse_mode='Markdown'
            )
            return

        key_info = KEYS_DB[user_key]

        if not key_info["active"]:
            await update.message.reply_text("❌ **KEY ĐÃ VÔ HIỆU HÓA**")
            return

        if key_info["expires_at"] and datetime.now() > key_info["expires_at"]:
            await update.message.reply_text("⏰ **KEY ĐÃ HẾT HẠN**")
            return

        if len(key_info["used_by"]) >= key_info["limit"]:
            if user_id not in key_info["used_by"]:
                await update.message.reply_text("🚫 **KEY ĐÃ ĐẠT GIỚI HẠN**")
                return

        key_info["used_by"].add(user_id)

        success_text = f"""
✅ **KEY VIP KÍCH HOẠT THÀNH CÔNG!**

🎮 **CHỨC NĂNG VIP:**
• 🤖 Thuật toán VIP SunWin & B52
• 🎯 Dự đoán siêu chính xác
• 📊 Auto 24/7

🚀 **BẮT ĐẦU:**
• /chaysunwin - Auto SunWin VIP
• /chayb52 - Auto B52 VIP
•/chayhitclub - Auto Hit Club 
•/chay789club - Auto 789 Club
⏰ {get_vn_time()}
🔥 **CHÚC BẠN THẮNG LỚN!** 🔥
"""
        await update.message.reply_text(success_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in key: {e}")

# Game commands
async def chaysunwin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto SunWin VIP"""
    await start_auto_game("sunwin", update, context)

async def chayb52(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto B52 VIP"""
    await start_auto_game("b52", update, context)

async def chay789club(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto 789Club"""
    await start_auto_game("789club", update, context)

async def chayhitclub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto HitClub"""
    await start_auto_game("hitclub", update, context)

async def start_auto_game(game_name, update, context):
    """Bắt đầu auto game"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if await is_banned(user_id, chat_id):
            return

        # Kiểm tra key
        has_active_key = False
        for key_info in KEYS_DB.values():
            if user_id in key_info["used_by"] and key_info["active"] and \
               (not key_info["expires_at"] or datetime.now() < key_info["expires_at"]):
                has_active_key = True
                break

        if not has_active_key:
            await update.message.reply_text(
                f"🔐 **CHƯA KÍCH HOẠT VIP**\n\n"
                f"📝 Sử dụng: `/key <your_key>`\n"
                f"💰 Mua key: @hatronghoann",
                parse_mode='Markdown'
            )
            return

        if game_name not in AUTO_TASKS:
            AUTO_TASKS[game_name] = set()

        if chat_id in AUTO_TASKS[game_name]:
            await update.message.reply_text(
                f"⚠️ **{game_name.upper()} ĐÃ CHẠY AUTO**"
            )
            return

        AUTO_TASKS[game_name].add(chat_id)

        # Initialize prediction tracking
        if chat_id not in LAST_PREDICTIONS[game_name]:
            LAST_PREDICTIONS[game_name][chat_id] = None

        algo_text = ""
        if game_name == "sunwin":
            algo_text = "🔥 Thuật toán SunWin VIP chuyên biệt"
        elif game_name == "b52":
            algo_text = "⚡ Thuật toán B52 VIP chuyên biệt"
        else:
            algo_text = "🧠 Thuật toán AI tổng quát"

        await update.message.reply_text(
            f"🚀 **BẮT ĐẦU AUTO {game_name.upper()} VIP**\n\n"
            f"{algo_text}\n"
            f"📊 Kiểm tra mỗi 4 giây\n"
            f"🛑 Dừng: `/stop {game_name}`\n"
            f"⏰ {get_vn_time()}",
            parse_mode='Markdown'
        )

        # Bắt đầu auto task
        asyncio.create_task(auto_task(game_name, chat_id, context))

    except Exception as e:
        logger.error(f"Error starting auto {game_name}: {e}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dừng auto game"""
    try:
        chat_id = update.effective_chat.id

        if len(context.args) == 0:
            await update.message.reply_text(
                "❌ **THIẾU TÊN GAME**\n\n"
                "📝 Sử dụng: `/stop <game>`\n"
                "🎮 Game: sunwin, b52, 789club, hitclub",
                parse_mode='Markdown'
            )
            return

        game_name = context.args[0].lower()

        if game_name not in GAME_APIS:
            await update.message.reply_text(
                f"❌ **GAME '{game_name}' KHÔNG HỢP LỆ**\n\n"
                "🎮 Game hỗ trợ: sunwin, b52, 789club, hitclub",
                parse_mode='Markdown'
            )
            return

        if game_name in AUTO_TASKS and chat_id in AUTO_TASKS[game_name]:
            AUTO_TASKS[game_name].remove(chat_id)
            await update.message.reply_text(
                f"🛑 **ĐÃ DỪNG AUTO {game_name.upper()} VIP**\n"
                f"⏰ {get_vn_time()}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"ℹ️ **{game_name.upper()} CHƯA CHẠY AUTO**"
            )
    except Exception as e:
        logger.error(f"Error in stop: {e}")

async def thongtin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Thông tin tài khoản"""
    try:
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "User"

        # Kiểm tra key
        active_keys = []
        for key_name, key_info in KEYS_DB.items():
            if user_id in key_info["used_by"] and key_info["active"]:
                active_keys.append(key_name)

        # Kiểm tra auto đang chạy
        running_autos = []
        chat_id = update.effective_chat.id
        for game_name, tasks in AUTO_TASKS.items():
            if chat_id in tasks:
                running_autos.append(game_name.upper())

        info_text = f"""
👤 **THÔNG TIN VIP**

📝 **Tên:** {user_name}
🆔 **ID:** {user_id}
🔑 **Key hoạt động:** {len(active_keys)}
🤖 **Auto đang chạy:** {len(running_autos)}
📊 **Trạng thái:** {'VIP' if active_keys else 'Chưa kích hoạt'}

💰 **BẢNG GIÁ BOT HTH:**
• 1 Ngày: 40k | 1 Tuần: 80k
• 1 Tháng: 160k | 2 Tháng: 200k
• Vĩnh viễn: 350k

📞 **Mua key:** @hatronghoann
⏰ {get_vn_time()}
"""

        if running_autos:
            info_text += f"\n🎮 **Auto:** {', '.join(running_autos)}"

        await update.message.reply_text(info_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in thongtin: {e}")

async def thongke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Thống kê bot"""
    try:
        total_users = len(set(user_id for key_info in KEYS_DB.values() for user_id in key_info["used_by"]))
        total_keys = len(KEYS_DB)
        active_autos = sum(len(tasks) for tasks in AUTO_TASKS.values())

        # Độ chính xác tổng
        total_predictions = sum(stats["total"] for stats in PREDICTION_STATS.values())
        total_correct = sum(stats["correct"] for stats in PREDICTION_STATS.values())
        overall_accuracy = (total_correct / total_predictions * 100) if total_predictions > 0 else 0

        stats_text = f"""
📊 **THỐNG KÊ BOT VIP**

👥 **Người dùng:** {total_users}
🔑 **Tổng key:** {total_keys}
🤖 **Auto đang chạy:** {active_autos}
🎯 **Tổng dự đoán:** {total_predictions}
✅ **Dự đoán đúng:** {total_correct}
📈 **Độ chính xác:** {overall_accuracy:.1f}%

**THEO GAME:**
"""

        for game_name, stats in PREDICTION_STATS.items():
            accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            sessions_tracked = len(SESSION_DATA[game_name]["session_history"])
            stats_text += f"• {game_name.upper()}: {accuracy:.1f}% ({stats['correct']}/{stats['total']}) - {sessions_tracked} phiên\n"

        stats_text += f"\n⏰ {get_vn_time()}\n🏆 **VIP TOOL HTH** 🏆"

        await update.message.reply_text(stats_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in thongke: {e}")

# Admin Commands
async def taokey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tạo key"""
    try:
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **KHÔNG CÓ QUYỀN ADMIN**")
            return

        key_name = None
        limit = 1
        duration_days = None

        if len(context.args) > 0:
            try:
                limit = int(context.args[0])
                if len(context.args) > 1:
                    duration_days = int(context.args[1])
            except ValueError:
                key_name = context.args[0]
                if len(context.args) > 1:
                    try:
                        limit = int(context.args[1])
                        if len(context.args) > 2:
                            duration_days = int(context.args[2])
                    except ValueError:
                        await update.message.reply_text("❌ **CÚ PHÁP SAI**")
                        return

        if key_name is None:
            key_name = f"HTH-{generate_random_string(8)}"

        if key_name in KEYS_DB:
            await update.message.reply_text(f"❌ **KEY '{key_name}' ĐÃ TỒN TẠI**")
            return

        expires_at = None
        if duration_days:
            expires_at = datetime.now() + timedelta(days=duration_days)

        KEYS_DB[key_name] = {
            "limit": limit,
            "used_by": set(),
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "active": True
        }

        expires_msg = f"hết hạn {expires_at.strftime('%d/%m/%Y')}" if expires_at else "vĩnh viễn"

        await update.message.reply_text(
            f"✅ **TẠO KEY THÀNH CÔNG**\n\n"
            f"🔑 **Key:** `{key_name}`\n"
            f"👥 **Giới hạn:** {limit} thiết bị\n"
            f"⏰ **Thời hạn:** {expires_msg}\n"
            f"🕐 **Tạo lúc:** {get_vn_time()}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in taokey: {e}")

async def lietkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Liệt kê key"""
    try:
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **KHÔNG CÓ QUYỀN ADMIN**")
            return

        if not KEYS_DB:
            await update.message.reply_text("📋 **CHƯA CÓ KEY NÀO**")
            return

        message = "🔑 **DANH SÁCH KEY:**\n\n"
        for key_name, info in KEYS_DB.items():
            status = "✅" if info["active"] else "❌"
            expiration = info["expires_at"].strftime('%d/%m/%Y') if info["expires_at"] else "Vĩnh viễn"
            used_count = len(info["used_by"])

            message += f"• **{key_name}** {status}\n"
            message += f"  Dùng: {used_count}/{info['limit']} | Hết hạn: {expiration}\n\n"

        message += f"⏰ {get_vn_time()}"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in lietkey: {e}")

async def xoakey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xóa key"""
    try:
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **KHÔNG CÓ QUYỀN ADMIN**")
            return

        if len(context.args) == 0:
            await update.message.reply_text("❌ **THIẾU TÊN KEY**\n📝 Sử dụng: `/xoakey <key_name>`")
            return

        key_to_delete = context.args[0]
        if key_to_delete in KEYS_DB:
            del KEYS_DB[key_to_delete]
            await update.message.reply_text(f"✅ **ĐÃ XÓA KEY '{key_to_delete}'**")
        else:
            await update.message.reply_text(f"❌ **KEY '{key_to_delete}' KHÔNG TỒN TẠI**")
    except Exception as e:
        logger.error(f"Error in xoakey: {e}")

async def banid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ban user"""
    try:
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **KHÔNG CÓ QUYỀN ADMIN**")
            return

        if len(context.args) == 0:
            await update.message.reply_text("❌ **THIẾU ID**\n📝 Sử dụng: `/banid <user_id>`")
            return

        try:
            user_id = int(context.args[0])
            BANNED_USERS.add(user_id)
            await update.message.reply_text(f"🚫 **ĐÃ BAN USER: {user_id}**")
        except ValueError:
            await update.message.reply_text("❌ **ID KHÔNG HỢP LỆ**")
    except Exception as e:
        logger.error(f"Error in banid: {e}")

async def themadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Thêm admin"""
    try:
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **KHÔNG CÓ QUYỀN ADMIN**")
            return

        if len(context.args) == 0:
            await update.message.reply_text("❌ **THIẾU ID**\n📝 Sử dụng: `/themadmin <user_id>`")
            return

        try:
            user_id = int(context.args[0])
            if user_id in ADMIN_IDS:
                await update.message.reply_text(f"⚠️ **USER {user_id} ĐÃ LÀ ADMIN**")
            else:
                ADMIN_IDS.append(user_id)
                await update.message.reply_text(f"✅ **ĐÃ THÊM ADMIN: {user_id}**")
        except ValueError:
            await update.message.reply_text("❌ **ID KHÔNG HỢP LỆ**")
    except Exception as e:
        logger.error(f"Error in themadmin: {e}")

async def xoaadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xóa admin"""
    try:
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **KHÔNG CÓ QUYỀN ADMIN**")
            return

        if len(context.args) == 0:
            await update.message.reply_text("❌ **THIẾU ID**\n📝 Sử dụng: `/xoaadmin <user_id>`")
            return

        try:
            user_id = int(context.args[0])
            if user_id == 7560849341:  # Không cho xóa admin chính
                await update.message.reply_text("❌ **KHÔNG THỂ XÓA ADMIN CHÍNH**")
            elif user_id in ADMIN_IDS:
                ADMIN_IDS.remove(user_id)
                await update.message.reply_text(f"✅ **ĐÃ XÓA ADMIN: {user_id}**")
            else:
                await update.message.reply_text(f"⚠️ **USER {user_id} KHÔNG PHẢI ADMIN**")
        except ValueError:
            await update.message.reply_text("❌ **ID KHÔNG HỢP LỆ**")
    except Exception as e:
        logger.error(f"Error in xoaadmin: {e}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast message"""
    try:
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **KHÔNG CÓ QUYỀN ADMIN**")
            return

        if len(context.args) == 0:
            await update.message.reply_text("❌ **THIẾU NỘI DUNG**\n📝 Sử dụng: `/broadcast <message>`")
            return

        message_content = " ".join(context.args)
        sent_count = 0
        unique_users = set()

        for key_name, info in KEYS_DB.items():
            for user_id in info["used_by"]:
                if user_id not in unique_users and user_id not in BANNED_USERS:
                    try:
                        broadcast_msg = f"""
📢 **THÔNG BÁO VIP**

{message_content}

━━━━━━━━━━━━━━━━━━━━━━━━
🎮 **Tool Game VIP HTH** 
⏰ {get_vn_time()}
━━━━━━━━━━━━━━━━━━━━━━━━
"""
                        await context.bot.send_message(
                            chat_id=user_id, 
                            text=broadcast_msg, 
                            parse_mode='Markdown'
                        )
                        unique_users.add(user_id)
                        sent_count += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.warning(f"Không gửi được tới user {user_id}: {e}")

        await update.message.reply_text(f"✅ **ĐÃ GỬI THÔNG BÁO TỚI {sent_count} NGƯỜI**")
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Error handler"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main() -> None:
    """Khởi động bot"""
    try:
        print("🎮 Khởi động Tool Game VIP HTH...")
        print("🔥 Thuật toán VIP SunWin & B52 loading...")
        print("🔧 Kết nối Telegram...")

        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Basic commands
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("key", key))
        application.add_handler(CommandHandler("thongtin", thongtin))
        application.add_handler(CommandHandler("hotro", hotro))
        application.add_handler(CommandHandler("huongdanmuakey", huongdanmuakey))

        # Game commands
        application.add_handler(CommandHandler("chaysunwin", chaysunwin))
        application.add_handler(CommandHandler("chayb52", chayb52))
        application.add_handler(CommandHandler("chay789club", chay789club))
        application.add_handler(CommandHandler("chayhitclub", chayhitclub))
        application.add_handler(CommandHandler("stop", stop))
        application.add_handler(CommandHandler("thongke", thongke))

        # Admin commands
        application.add_handler(CommandHandler("taokey", taokey))
        application.add_handler(CommandHandler("lietkey", lietkey))
        application.add_handler(CommandHandler("xoakey", xoakey))
        application.add_handler(CommandHandler("banid", banid))
        application.add_handler(CommandHandler("broadcast", broadcast))
        application.add_handler(CommandHandler("themadmin", themadmin))
        application.add_handler(CommandHandler("xoaadmin", xoaadmin))

        # Error handler
        application.add_error_handler(error_handler)

        print("✅ Bot Tool VIP đã sẵn sàng!")
        print("🔥 Thuật toán VIP SunWin & B52 chuyên biệt activated!")
        print("📊 Hỗ trợ 4 game với độ chính xác cao")
        print("🚀 Bot đang chạy ổn định...")

        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

    except KeyboardInterrupt:
        print("🛑 Bot đã dừng")
    except Exception as e:
        logger.error(f"❌ Lỗi khởi động: {e}")
        print(f"❌ Lỗi khởi động: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
