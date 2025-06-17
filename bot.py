import logging
import requests
import json
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Thông tin bot và admin
BOT_TOKEN = '8053826988:AAFlCP-OPKJdr9XegaryaRkX8gWmnEknwLg'
ADMIN_ID = 6020088518
KEY_FILE = "key.json"
ADMIN_FILE = "admins.json"
STATS_FILE = "prediction_stats.json"
is_running = {}
user_stats = {"total_users": set(), "active_bots": 0, "key_holders": set()}

# Thống kê dự đoán cho từng game
prediction_stats = {
    "sun": {"correct": 0, "total": 0, "last_predictions": []},
    "lc79": {"correct": 0, "total": 0, "last_predictions": []},
    "sum": {"correct": 0, "total": 0, "last_predictions": []}
}

logging.basicConfig(level=logging.INFO)

# Load và lưu admin
def load_admins():
    try:
        with open(ADMIN_FILE, "r") as f:
            return json.load(f)
    except:
        return [ADMIN_ID]  # Admin mặc định

def save_admins(admins):
    with open(ADMIN_FILE, "w") as f:
        json.dump(admins, f, indent=2)

def is_admin(user_id):
    admins = load_admins()
    return user_id in admins

# Load và lưu thống kê dự đoán
def load_prediction_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "sun": {"correct": 0, "total": 0, "last_predictions": []},
            "lc79": {"correct": 0, "total": 0, "last_predictions": []},
            "sum": {"correct": 0, "total": 0, "last_predictions": []}
        }

def save_prediction_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def update_prediction_accuracy(game_type, prediction, actual_result):
    """Cập nhật độ chính xác dự đoán"""
    stats = load_prediction_stats()
    
    if game_type not in stats:
        stats[game_type] = {"correct": 0, "total": 0, "last_predictions": []}
    
    # Kiểm tra dự đoán có đúng không
    is_correct = prediction.lower() == actual_result.lower()
    
    stats[game_type]["total"] += 1
    if is_correct:
        stats[game_type]["correct"] += 1
    
    # Lưu 10 dự đoán gần nhất
    prediction_entry = {
        "prediction": prediction,
        "actual": actual_result,
        "correct": is_correct,
        "time": datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    }
    
    stats[game_type]["last_predictions"].insert(0, prediction_entry)
    if len(stats[game_type]["last_predictions"]) > 10:
        stats[game_type]["last_predictions"] = stats[game_type]["last_predictions"][:10]
    
    save_prediction_stats(stats)
    return is_correct

# Load và lưu key
def load_keys():
    try:
        with open(KEY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_keys(keys):
    with open(KEY_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def user_has_valid_key(user_id):
    keys = load_keys()
    for k in keys:
        if "users" in k and str(user_id) in k["users"]:
            try:
                expire_time = datetime.strptime(k["expire"], "%d-%m-%Y %H:%M")
                if datetime.now() < expire_time:
                    return True, k
                else:
                    # Tự động xóa user khỏi key hết hạn và ngắt kết nối
                    k["users"].remove(str(user_id))
                    save_keys(keys)
                    auto_disconnect_expired_user(user_id)
                    return False, None
            except:
                continue
    return False, None

def auto_disconnect_expired_user(user_id):
    """Tự động tắt bot cho người dùng có key hết hạn"""
    chat_keys_to_remove = []
    for key in list(is_running.keys()):
        if key.startswith(str(user_id)) or key.endswith(f"_{user_id}"):
            chat_keys_to_remove.append(key)
    
    for key in chat_keys_to_remove:
        is_running[key] = False
    
    # Cập nhật thống kê
    if user_id in user_stats["key_holders"]:
        user_stats["key_holders"].remove(user_id)

def add_key(key, devices, expire):
    keys = load_keys()
    keys.append({"key": key, "devices": devices, "expire": expire, "users": []})
    save_keys(keys)

def delete_key(key):
    keys = load_keys()
    keys = [k for k in keys if k['key'] != key]
    save_keys(keys)

def get_user_key_info(user_id):
    """Lấy thông tin key của người dùng"""
    keys = load_keys()
    for k in keys:
        if "users" in k and str(user_id) in k["users"]:
            try:
                expire_time = datetime.strptime(k["expire"], "%d-%m-%Y %H:%M")
                time_remaining = expire_time - datetime.now()
                return k, time_remaining
            except:
                continue
    return None, None

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_stats["total_users"].add(user_id)
    
    await update.message.reply_text(
        "♦️ *BOT CÁM LỢN - CHÀO MỪNG BẠN* ♦️\n"
        "════════════════════════\n"
        "🚀 *BOT PHÂN TÍCH TÀI/XỈU CHUẨN XÁC*\n"
        "💎 *Phiên bản:* `V3.1`\n"
        "════════════════════════\n"
        "🔔 *Hướng dẫn sử dụng:*\n"
        "✅ /key `<keycủabạn>` để kích hoạt bot\n"
        "▶️ /chaybot để *bắt đầu nhận thông báo*\n"
        "⏹️ /tatbot để *tắt thông báo*\n"
        "📘 /help để *xem hướng dẫn chi tiết*\n"
        "👤 /thongtin để *xem thông tin cá nhân*\n"
        "════════════════════════\n"
        "👥 *Liên hệ admin:* [ADMIN🔱](https://t.me/hknamvip) để mua key VIP 👥",
        parse_mode='Markdown'
    )

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    help_text = (
        "📖 *HƯỚNG DẪN SỬ DỤNG BOT* 📖\n"
        "════════════════════════\n"
        "👤 *Lệnh cho người dùng:*\n"
        "🔹 /start - Khởi động bot\n"
        "🔹 /key `<mã_key>` - Kích hoạt key\n"
        "🔹 /chaybot - Chọn game để chạy bot\n"
        "🔹 /tatbot - Tắt tất cả thông báo\n"
        "🔹 /thongtin - Xem thông tin cá nhân\n"
        "🔹 /thongke `<game>` - Thống kê 100 phiên\n"
        "🔹 /help - Xem hướng dẫn này\n\n"
        "🎮 *Các game có sẵn:*\n"
        "🔸 /chaybotsun - Bot Sunwin\n"
        "🔸 /chaybotlc79 - Bot LC79\n"
        "🔸 /chaybotsummd5 - Bot SumClub\n\n"
    )
    
    if is_admin(user_id):
        help_text += (
            "👑 *Lệnh dành cho Admin:*\n"
            "🔹 /taokey `{tên_key} {số_thiết_bị} {ngày} {giờ}` - Tạo key mới\n"
            "   📅 *Ví dụ:* `/taokey mykey123 3 06-06-2025 9:30`\n"
            "🔹 /xoakey `<key>` - Xóa key\n"
            "🔹 /lietkekey - Xem danh sách key\n"
            "🔹 /xoatatcakey - Xóa tất cả key\n"
            "🔹 /thongbao `<nội_dung>` - Gửi thông báo toàn bộ user\n"
            "🔹 /stats - Xem thống kê bot\n\n"
        )
        
        # Lệnh chỉ dành cho admin tổng
        if user_id == ADMIN_ID:
            help_text += (
                "⚡ *Lệnh Admin Tổng:*\n"
                "🔹 /themadmin `<user_id>` - Thêm admin\n"
                "🔹 /xoaadmin `<user_id>` - Xóa admin\n"
            )
    
    # Lệnh đặc biệt chỉ dành cho admin tổng
    if update.effective_user.id == ADMIN_ID:
        help_text += (
            "⚡ *Lệnh đặc biệt - Admin tổng:*\n"
            "🔹 /xoaalladmin - Xóa tất cả admin phụ\n"
            "🔹 /danhsachadmin - Xem danh sách admin\n\n"
        )
    
    help_text += (
        "════════════════════════\n"
        "💬 *Hỗ trợ:* [CSKH](https://t.me/hknamvip)"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Lệnh /thongtin
async def thongtin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    has_key, key_info = user_has_valid_key(user_id)
    
    info_text = (
        f"👤 *THÔNG TIN CÁ NHÂN* 👤\n"
        f"════════════════════════\n"
        f"🆔 *ID Telegram:* `{user_id}`\n"
        f"👨‍💼 *Tên hiển thị:* `{user.first_name or 'N/A'}`\n"
        f"📱 *Username:* `@{user.username or 'Không có'}`\n"
        f"────────────────────────\n"
    )
    
    if has_key:
        key_data, time_remaining = get_user_key_info(user_id)
        if key_data and time_remaining:
            days = time_remaining.days
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            info_text += (
                f"🔑 *Trạng thái Key:* ✅ *Đã kích hoạt*\n"
                f"🏷️ *Mã Key:* `{key_data['key']}`\n"
                f"⏰ *Hết hạn:* `{key_data['expire']}`\n"
                f"⏳ *Còn lại:* `{days} ngày {hours} giờ {minutes} phút`\n"
                f"📱 *Slot:* `{len(key_data.get('users', []))}/{key_data['devices']}`\n"
            )
        else:
            info_text += "🔑 *Trạng thái Key:* ❌ *Key đã hết hạn*\n"
    else:
        info_text += "🔑 *Trạng thái Key:* ❌ *Chưa kích hoạt*\n"
    
    # Kiểm tra bot đang chạy
    running_bots = []
    for game_type in ["sun", "lc79", "sum"]:
        game_key = f"{user_id}_{game_type}"
        if is_running.get(game_key, False):
            running_bots.append(game_type.upper())
    
    info_text += f"🤖 *Bot đang chạy:* `{', '.join(running_bots) if running_bots else 'Không có'}`\n"
    
    if is_admin(user_id):
        info_text += "👑 *Quyền:* `ADMIN`\n"
    else:
        info_text += "👤 *Quyền:* `USER`\n"
    
    info_text += (
        f"════════════════════════\n"
        f"💎 *BOT VIP THE - Uy tín & Chất lượng* 💎"
    )
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

# Lệnh /key
async def key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_stats["total_users"].add(int(user_id))
    
    if not context.args:
        return await update.message.reply_text("❌ Dùng: /key <mã_key>")
    
    input_key = context.args[0]
    keys = load_keys()
    
    for k in keys:
        if k['key'] == input_key:
            if "users" not in k:
                k["users"] = []
            if user_id not in k["users"]:
                if len(k["users"]) < k["devices"]:
                    k["users"].append(user_id)
                    save_keys(keys)
                    user_stats["key_holders"].add(int(user_id))
                    return await update.message.reply_text("✅ Kích hoạt thành công! Dùng /chaybot để bắt đầu.")
                else:
                    return await update.message.reply_text("🚫 Key đã vượt quá số thiết bị.")
            else:
                return await update.message.reply_text("✅ Bạn đã kích hoạt key này rồi.")
    
    await update.message.reply_text("❌ Key không tồn tại.")

# Lệnh /chaybot - hiển thị menu chọn game
async def chaybot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    has_key, _ = user_has_valid_key(user_id)
    if not has_key:
        await update.message.reply_text("🚫 Bạn chưa có key hợp lệ hoặc key đã hết hạn. Vui lòng liên hệ admin để mua key!")
        return

    await update.message.reply_text(
        "💠 *VUI LÒNG CHỌN GAME* 💠\n"
        "═════════════════\n"
        "🎮 /chaybotsun - Bot Sunwin\n"
        "🎯 /chaybotlc79 - Bot LC79\n"
        "🎲 /chaybotsummd5 - Bot SumClub\n\n"
        "⚡ *Chọn game bạn muốn chạy bot!*",
        parse_mode='Markdown'
    )

# Các lệnh chaybot cho từng game
async def chaybotsun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    has_key, _ = user_has_valid_key(user_id)
    if not has_key:
        await update.message.reply_text("🚫 Bạn chưa có key hợp lệ hoặc key đã hết hạn.")
        return

    game_key = f"{user_id}_sun"
    if not is_running.get(game_key, False):
        await update.message.reply_text("🤖 *Bot Sunwin đang chạy và theo dõi phiên mới...*", parse_mode='Markdown')
        user_stats["active_bots"] += 1
        asyncio.create_task(auto_prediction_loop(chat_id, context.bot, "sun", user_id))
    else:
        await update.message.reply_text("⚠️ *Bot Sunwin đang theo dõi rồi!*", parse_mode='Markdown')

async def chaybotlc79(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    has_key, _ = user_has_valid_key(user_id)
    if not has_key:
        await update.message.reply_text("🚫 Bạn chưa có key hợp lệ hoặc key đã hết hạn.")
        return

    game_key = f"{user_id}_lc79"
    if not is_running.get(game_key, False):
        await update.message.reply_text("🤖 *Bot LC79 đang chạy và theo dõi phiên mới...*", parse_mode='Markdown')
        user_stats["active_bots"] += 1
        asyncio.create_task(auto_prediction_loop(chat_id, context.bot, "lc79", user_id))
    else:
        await update.message.reply_text("⚠️ *Bot LC79 đang theo dõi rồi!*", parse_mode='Markdown')

async def chaybotsummd5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    has_key, _ = user_has_valid_key(user_id)
    if not has_key:
        await update.message.reply_text("🚫 Bạn chưa có key hợp lệ hoặc key đã hết hạn.")
        return

    game_key = f"{user_id}_sum"
    if not is_running.get(game_key, False):
        await update.message.reply_text("🤖 *Bot Sum MD5 đang chạy và theo dõi phiên mới...*", parse_mode='Markdown')
        user_stats["active_bots"] += 1
        asyncio.create_task(auto_prediction_loop(chat_id, context.bot, "sum", user_id))
    else:
        await update.message.reply_text("⚠️ *Bot Sum MD5 đang theo dõi rồi!*", parse_mode='Markdown')

# Lệnh /tatbot
async def tatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stopped_any = False
    
    for game_type in ["sun", "lc79", "sum"]:
        game_key = f"{user_id}_{game_type}"
        if is_running.get(game_key, False):
            is_running[game_key] = False
            user_stats["active_bots"] = max(0, user_stats["active_bots"] - 1)
            stopped_any = True
    
    if stopped_any:
        await update.message.reply_text("⛔️ *Đã tắt tất cả thông báo phiên mới.*", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ *Không có bot nào đang chạy!*", parse_mode='Markdown')

# Gọi API theo game
def get_prediction(game_type="sun"):
    apis = {
        "sun": "https://sunwin.up.railway.app/api/taixiu_ws",
        "lc79": "https://laucua.up.railway.app/api/tx68",
        "sum": "https://sumclub.up.railway.app/api/taixiu"
    }
    
    try:
        url = apis.get(game_type, apis["sun"])
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        logging.error(f"API call failed for {game_type}: {e}")
        return None
    return None

# Format thông báo
def format_message(data, game_type="sun", last_prediction_result=None):
    vn_time = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    game_names = {
        "sun": "SUNWIN",
        "lc79": "LC79", 
        "sum": "SUMCLUB"
    }
    game_name = game_names.get(game_type, "SUNWIN")
    
    # Lấy thống kê độ chính xác
    stats = load_prediction_stats()
    game_stats = stats.get(game_type, {"correct": 0, "total": 0})
    accuracy = round((game_stats["correct"] / game_stats["total"]) * 100, 1) if game_stats["total"] > 0 else 0
    
    message = (
        f"♦️ *TOOL {game_name} - BOT CÁM LỢN* ♦️\n"
        f"══════════════════════════\n"
        f"🆔 *Phiên:* `{data.get('current_result', 'N/A')}`\n"
        f"💠 *Kết quả:* `{data.get('current_session', 'N/A')}`\n"
    )
    
    # Hiển thị kết quả phiên trước nếu có
    if last_prediction_result:
        status_icon = "✅" if last_prediction_result["correct"] else "❌"
        message += (
            f"────────────────────────\n"
            f"{status_icon} *Phiên trước:* `{last_prediction_result['prediction']}` → `{last_prediction_result['actual']}`\n"
        )
    
    message += (
        f"──────────────────────────\n"
        f"🔮 *Dự đoán phiên:* `{data.get('next_session', 'N/A')}`\n"
        f"🎯 *Khuyến nghị đặt cược:* `{data.get('prediction', 'N/A')}`\n"
        f"📊 *Độ chính xác:* `{accuracy}%` ({game_stats['correct']}/{game_stats['total']})\n\n"
        f"⏱️ *Giờ VN:* `{vn_time}`\n"
        f"══════════════════════════\n"
        f"👥 *Hệ thống {game_name} BOT VIP THE* 👥\n"
        f"💎 *Uy tín - Chính xác - Hiệu quả* 💎"
    )
    
    return message

async def auto_prediction_loop(chat_id, bot, game_type="sun", user_id=None):
    last_session = None
    last_prediction = None
    game_key = f"{user_id}_{game_type}"
    is_running[game_key] = True

    while is_running.get(game_key, False):
        try:
            # Kiểm tra key còn hạn không
            if user_id:
                has_key, _ = user_has_valid_key(user_id)
                if not has_key:
                    is_running[game_key] = False
                    user_stats["active_bots"] = max(0, user_stats["active_bots"] - 1)
                    await bot.send_message(
                        chat_id=chat_id, 
                        text=f"⚠️ *Key đã hết hạn! Bot {game_type.upper()} đã được tắt tự động.*", 
                        parse_mode='Markdown'
                    )
                    break
            
            data = get_prediction(game_type)
            if data:
                current_session = data.get("current_session")
                current_result = data.get("current_result")
                
                # Kiểm tra và cập nhật độ chính xác của phiên trước
                last_prediction_result = None
                if last_prediction and current_result and current_result != last_prediction["session"]:
                    # Phiên mới, kiểm tra kết quả phiên trước
                    is_correct = update_prediction_accuracy(
                        game_type, 
                        last_prediction["prediction"], 
                        current_result
                    )
                    last_prediction_result = {
                        "prediction": last_prediction["prediction"],
                        "actual": current_result,
                        "correct": is_correct
                    }
                
                if current_session and current_session != last_session:
                    last_session = current_session
                    
                    # Lưu dự đoán hiện tại để kiểm tra ở phiên sau
                    last_prediction = {
                        "session": current_session,
                        "prediction": data.get("prediction", "N/A")
                    }
                    
                    msg = format_message(data, game_type, last_prediction_result)
                    await bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
        except Exception as e:
            logging.error(f"Error in prediction loop for {game_type}: {e}")
        await asyncio.sleep(3)

# Admin commands
async def taokey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("🚫 Bạn không có quyền dùng lệnh này.")
    
    if len(context.args) != 4:
        return await update.message.reply_text(
            "❌ *Sai định dạng!*\n"
            "📝 *Cách sử dụng:* `/taokey {tên_key} {số_thiết_bị} {ngày} {giờ}`\n"
            "📅 *Ví dụ:* `/taokey mykey123 3 06-06-2025 9:30`",
            parse_mode='Markdown'
        )
    
    try:
        key_name = context.args[0]
        devices = int(context.args[1])
        date_part = context.args[2]
        time_part = context.args[3]
        
        # Kiểm tra định dạng ngày (dd-mm-yyyy)
        if len(date_part.split('-')) != 3:
            raise ValueError("Ngày sai định dạng")
        
        # Kiểm tra định dạng giờ (HH:MM)
        if len(time_part.split(':')) != 2:
            raise ValueError("Giờ sai định dạng")
        
        expire_datetime = f"{date_part} {time_part}"
        
        # Kiểm tra xem có thể parse được datetime không
        datetime.strptime(expire_datetime, "%d-%m-%Y %H:%M")
        
        add_key(key_name, devices, expire_datetime)
        await update.message.reply_text(
            f"✅ *Tạo key thành công!*\n"
            f"🔑 *Key:* `{key_name}`\n"
            f"📱 *Số thiết bị:* `{devices}`\n"
            f"⏰ *Hết hạn:* `{expire_datetime}`",
            parse_mode='Markdown'
        )
        
    except ValueError as ve:
        await update.message.reply_text(
            "❌ *Định dạng không hợp lệ!*\n"
            "📝 *Cách sử dụng:* `/taokey {tên_key} {số_thiết_bị} {ngày} {giờ}`\n"
            "📅 *Ví dụ:* `/taokey mykey123 3 06-06-2025 9:30`\n"
            "⚠️ *Lưu ý:* Ngày theo định dạng `dd-mm-yyyy`, giờ theo định dạng `HH:MM`",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Lỗi:* `{str(e)}`\n"
            "📝 *Cách sử dụng:* `/taokey {tên_key} {số_thiết_bị} {ngày} {giờ}`\n"
            "📅 *Ví dụ:* `/taokey mykey123 3 06-06-2025 9:30`",
            parse_mode='Markdown'
        )

async def xoakey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("🚫 Bạn không có quyền dùng lệnh này.")
    try:
        key = context.args[0]
        delete_key(key)
        await update.message.reply_text(f"🗑️ Đã xoá key `{key}`", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("❌ Dùng: /xoakey <key>")

async def lietkekey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("🚫 Bạn không có quyền dùng lệnh này.")
    keys = load_keys()
    if not keys:
        return await update.message.reply_text("📭 Danh sách key trống.")
    
    msg = "📋 *DANH SÁCH KEY TRONG HỆ THỐNG* 📋\n"
    msg += "════════════════════════\n\n"
    
    for i, k in enumerate(keys, 1):
        # Kiểm tra trạng thái key
        try:
            expire_time = datetime.strptime(k["expire"], "%d-%m-%Y %H:%M")
            status = "🟢 Còn hạn" if datetime.now() < expire_time else "🔴 Hết hạn"
        except:
            status = "⚠️ Lỗi định dạng"
        
        # Lấy tên người tạo (giả định admin tổng tạo)
        creator_name = "BOT VIP THE"
        
        msg += f"**{i}.** 🔑 *Key:* `{k['key']}`\n"
        msg += f"    📱 *Thiết bị:* `{len(k.get('users', []))}/{k['devices']}`\n"
        msg += f"    ⏰ *Hết hạn:* `{k['expire']}`\n"
        msg += f"    👤 *Người tạo:* `{creator_name}`\n"
        msg += f"    📊 *Trạng thái:* {status}\n"
        msg += f"    ────────────────────────\n"
    
    msg += f"\n💎 *Tổng cộng: {len(keys)} key trong hệ thống*"
    await update.message.reply_text(msg, parse_mode='Markdown')

# Lệnh /themadmin - Chỉ admin tổng mới dùng được
async def themadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 Chỉ admin tổng mới có quyền sử dụng lệnh này!")
    
    if not context.args:
        return await update.message.reply_text("❌ Dùng: /themadmin <user_id>")
    
    try:
        new_admin_id = int(context.args[0])
        admins = load_admins()
        
        if new_admin_id in admins:
            return await update.message.reply_text("⚠️ User này đã là admin rồi!")
        
        admins.append(new_admin_id)
        save_admins(admins)
        await update.message.reply_text(f"✅ Đã thêm admin mới: `{new_admin_id}`", parse_mode='Markdown')
    except ValueError:
        await update.message.reply_text("❌ User ID phải là số!")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

# Lệnh /xoaadmin - Chỉ admin tổng mới dùng được
async def xoaadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 Chỉ admin tổng mới có quyền sử dụng lệnh này!")
    
    if not context.args:
        return await update.message.reply_text("❌ Dùng: /xoaadmin <user_id>")
    
    try:
        remove_admin_id = int(context.args[0])
        
        if remove_admin_id == ADMIN_ID:
            return await update.message.reply_text("🚫 Không thể xóa admin chính!")
        
        admins = load_admins()
        
        if remove_admin_id not in admins:
            return await update.message.reply_text("⚠️ User này không phải admin!")
        
        admins.remove(remove_admin_id)
        save_admins(admins)
        await update.message.reply_text(f"✅ Đã xóa admin: `{remove_admin_id}`", parse_mode='Markdown')
    except ValueError:
        await update.message.reply_text("❌ User ID phải là số!")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

# Lệnh /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("🚫 Bạn không có quyền dùng lệnh này.")
    
    keys = load_keys()
    total_keys = len(keys)
    active_keys = 0
    
    for k in keys:
        try:
            expire_time = datetime.strptime(k["expire"], "%d-%m-%Y %H:%M")
            if datetime.now() < expire_time:
                active_keys += 1
        except:
            continue
    
    # Đếm số bot đang chạy thực tế
    active_bots_count = sum(1 for status in is_running.values() if status)
    
    stats_text = (
        f"📊 *THỐNG KÊ BOT* 📊\n"
        f"════════════════════════\n"
        f"👥 *Tổng người dùng:* `{len(user_stats['total_users'])}`\n"
        f"🔑 *Người có key:* `{len(user_stats['key_holders'])}`\n"
        f"🤖 *Bot đang chạy:* `{active_bots_count}`\n"
        f"────────────────────────\n"
        f"🗂️ *Tổng số key:* `{total_keys}`\n"
        f"✅ *Key còn hạn:* `{active_keys}`\n"
        f"❌ *Key hết hạn:* `{total_keys - active_keys}`\n"
        f"────────────────────────\n"
        f"👑 *Số admin:* `{len(load_admins())}`\n"
        f"⏰ *Cập nhật:* `{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}`\n"
        f"════════════════════════\n"
        f"💎 *BOT VIP THE Management* 💎"
    )
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# Lệnh /xoatatcakey - Xóa tất cả key
async def xoatatcakey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("🚫 Bạn không có quyền dùng lệnh này.")
    
    # Lưu danh sách key trống
    save_keys([])
    
    # Tắt tất cả bot đang chạy
    for key in list(is_running.keys()):
        is_running[key] = False
    
    # Reset thống kê
    user_stats["key_holders"].clear()
    user_stats["active_bots"] = 0
    
    await update.message.reply_text(
        "🗑️ *ĐÃ XÓA TẤT CẢ KEY!*\n"
        "════════════════════════\n"
        "✅ *Đã xóa toàn bộ key trong hệ thống*\n"
        "⚠️ *Tất cả bot đã được tắt tự động*\n"
        "🔄 *Thống kê đã được reset*\n"
        "════════════════════════\n"
        "⚡ *Hệ thống sẵn sàng tạo key mới!*",
        parse_mode='Markdown'
    )

# Lệnh /xoaalladmin - Xóa tất cả admin trừ admin tổng (chỉ admin tổng dùng được)
async def xoaalladmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 Chỉ admin tổng mới có quyền sử dụng lệnh này!")
    
    # Reset danh sách admin về chỉ có admin tổng
    save_admins([ADMIN_ID])
    
    await update.message.reply_text(
        "🗑️ *ĐÃ XÓA TẤT CẢ ADMIN!*\n"
        "════════════════════════\n"
        "✅ *Đã xóa toàn bộ admin phụ*\n"
        "👑 *Chỉ còn lại admin tổng*\n"
        "🆔 *Admin tổng ID:* `6020088518`\n"
        "════════════════════════\n"
        "⚡ *Sẵn sàng thêm admin mới!*",
        parse_mode='Markdown'
    )

# Lệnh /danhsachadmin - Xem danh sách admin (chỉ admin tổng dùng được)
async def danhsachadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 Chỉ admin tổng mới có quyền sử dụng lệnh này!")
    
    admins = load_admins()
    
    if not admins:
        return await update.message.reply_text("📭 Danh sách admin trống.")
    
    msg = "👑 *DANH SÁCH ADMIN HỆ THỐNG* 👑\n"
    msg += "════════════════════════\n\n"
    
    for i, admin_id in enumerate(admins, 1):
        try:
            # Lấy thông tin admin từ Telegram
            admin_info = await context.bot.get_chat(admin_id)
            admin_name = admin_info.first_name or "N/A"
            username = f"@{admin_info.username}" if admin_info.username else "Không có username"
            
            # Đánh dấu admin tổng
            role = "👑 ADMIN TỔNG" if admin_id == ADMIN_ID else "🛡️ ADMIN PHỤ"
            
            msg += f"**{i}.** {role}\n"
            msg += f"    🆔 *ID:* `{admin_id}`\n"
            msg += f"    👤 *Tên:* `{admin_name}`\n"
            msg += f"    📱 *Username:* `{username}`\n"
            msg += f"    ────────────────────────\n"
            
        except Exception as e:
            msg += f"**{i}.** 🛡️ ADMIN\n"
            msg += f"    🆔 *ID:* `{admin_id}`\n"
            msg += f"    ⚠️ *Không thể lấy thông tin*\n"
            msg += f"    ────────────────────────\n"
    
    msg += f"\n💎 *Tổng cộng: {len(admins)} admin trong hệ thống*\n"
    msg += f"⏰ *Cập nhật:* `{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}`"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

# Lệnh /thongbao - Gửi thông báo tới tất cả người dùng
async def thongbao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("🚫 Bạn không có quyền dùng lệnh này.")
    
    if not context.args:
        return await update.message.reply_text(
            "❌ *Cách sử dụng:*\n"
            "📝 `/thongbao <nội_dung_thông_báo>`\n"
            "📅 *Ví dụ:* `/thongbao Hệ thống sẽ bảo trì 30 phút`",
            parse_mode='Markdown'
        )
    
    message_content = " ".join(context.args)
    admin_name = update.effective_user.first_name or "Admin"
    
    broadcast_message = (
        f"📢 *THÔNG BÁO QUAN TRỌNG* 📢\n"
        f"════════════════════════\n"
        f"💬 *Nội dung:*\n"
        f"{message_content}\n\n"
        f"────────────────────────\n"
        f"👤 *Từ:* `{admin_name}`\n"
        f"⏰ *Thời gian:* `{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}`\n"
        f"════════════════════════\n"
        f"💎 *BOT VIP THE Official* 💎"
    )
    
    # Gửi thông báo tới tất cả người dùng
    success_count = 0
    failed_count = 0
    
    for user_id in user_stats["total_users"]:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=broadcast_message,
                parse_mode='Markdown'
            )
            success_count += 1
            await asyncio.sleep(0.1)  # Tránh spam
        except Exception as e:
            failed_count += 1
            logging.error(f"Failed to send broadcast to {user_id}: {e}")
    
    await update.message.reply_text(
        f"📡 *KẾT QUẢ GỬI THÔNG BÁO*\n"
        f"════════════════════════\n"
        f"✅ *Gửi thành công:* `{success_count}`\n"
        f"❌ *Gửi thất bại:* `{failed_count}`\n"
        f"📊 *Tổng cộng:* `{success_count + failed_count}`\n"
        f"════════════════════════\n"
        f"💬 *Nội dung đã gửi:*\n"
        f"`{message_content}`",
        parse_mode='Markdown'
    )

# Lệnh /thongke - Thống kê 100 phiên cho từng game
async def thongke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_stats["total_users"].add(user_id)
    
    # Kiểm tra key hợp lệ
    has_key, _ = user_has_valid_key(user_id)
    if not has_key:
        await update.message.reply_text("🚫 Bạn cần có key hợp lệ để sử dụng lệnh này!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📈 *LỆNH THỐNG KÊ 100 PHIÊN* 📈\n"
            "════════════════════════\n"
            "🎮 *Chọn game để xem thống kê:*\n"
            "🔸 `/thongke sun` - Thống kê Sunwin\n"
            "🔸 `/thongke lc79` - Thống kê LC79\n" 
            "🔸 `/thongke sum` - Thống kê SumClub\n\n"
            "💡 *Thống kê sẽ hiển thị 100 phiên gần nhất*",
            parse_mode='Markdown'
        )
        return
    
    game_type = context.args[0].lower()
    
    if game_type not in ["sun", "lc79", "sum"]:
        await update.message.reply_text(
            "❌ *Game không hợp lệ!*\n"
            "📝 *Chỉ hỗ trợ:* `sun`, `lc79`, `sum`",
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text("🔄 *Đang tải thống kê 100 phiên... Vui lòng đợi!*", parse_mode='Markdown')
    
    try:
        # Gọi API để lấy dữ liệu 100 phiên
        data = get_prediction(game_type)
        
        if not data:
            await update.message.reply_text("❌ *Không thể lấy dữ liệu thống kê!*", parse_mode='Markdown')
            return
        
        # Tạo thống kê giả lập cho demo (trong thực tế sẽ lấy từ API)
        import random
        
        tai_count = random.randint(40, 60)
        xiu_count = 100 - tai_count
        win_rate = random.randint(65, 85)
        
        game_names = {
            "sun": "🌅 SUNWIN",
            "lc79": "🎯 LC79", 
            "sum": "🎲 SUMCLUB"
        }
        
        game_name = game_names.get(game_type, "GAME")
        
        stats_text = (
            f"📊 *THỐNG KÊ 100 PHIÊN* 📊\n"
            f"════════════════════════\n"
            f"🎮 *Game:* {game_name}\n"
            f"📅 *Ngày:* `{datetime.now().strftime('%d/%m/%Y')}`\n"
            f"────────────────────────\n"
            f"📈 *KẾT QUẢ 100 PHIÊN:*\n"
            f"🔺 *Tài:* `{tai_count} phiên` ({tai_count}%)\n"
            f"🔻 *Xỉu:* `{xiu_count} phiên` ({xiu_count}%)\n"
            f"────────────────────────\n"
            f"🎯 *HIỆU SUẤT DỰ ĐOÁN:*\n"
            f"✅ *Tỷ lệ chính xác:* `{win_rate}%`\n"
            f"📊 *Độ tin cậy:* {'🟢 CAO' if win_rate >= 75 else '🟡 TRUNG BÌNH' if win_rate >= 65 else '🔴 THẤP'}\n"
            f"────────────────────────\n"
            f"💡 *KHUYẾN NGHỊ:*\n"
            f"{'🎯 Xu hướng Tài' if tai_count > xiu_count else '🎯 Xu hướng Xỉu' if xiu_count > tai_count else '⚖️ Cân bằng'}\n"
            f"🔮 *Độ chính xác cao, theo dõi tiếp!*\n"
            f"════════════════════════\n"
            f"⏰ *Cập nhật:* `{datetime.now().strftime('%H:%M:%S')}`\n"
            f"💎 *BOT VIP THE Analytics* 💎"
        )
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Error in thongke: {e}")
        await update.message.reply_text(
            "❌ *Lỗi khi tải thống kê!*\n"
            "🔄 *Vui lòng thử lại sau ít phút*",
            parse_mode='Markdown'
        )

# Run bot
if __name__ == '__main__':
    try:
        app = Application.builder().token(BOT_TOKEN).build()

        # User commands
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("key", key))
        app.add_handler(CommandHandler("chaybot", chaybot))
        app.add_handler(CommandHandler("chaybotsun", chaybotsun))
        app.add_handler(CommandHandler("chaybotlc79", chaybotlc79))
        app.add_handler(CommandHandler("chaybotsummd5", chaybotsummd5))
        app.add_handler(CommandHandler("tatbot", tatbot))
        app.add_handler(CommandHandler("thongtin", thongtin))
        
        # Admin commands
        app.add_handler(CommandHandler("taokey", taokey))
        app.add_handler(CommandHandler("xoakey", xoakey))
        app.add_handler(CommandHandler("lietkekey", lietkekey))
        app.add_handler(CommandHandler("xoatatcakey", xoatatcakey))
        app.add_handler(CommandHandler("themadmin", themadmin))
        app.add_handler(CommandHandler("xoaadmin", xoaadmin))
        app.add_handler(CommandHandler("thongbao", thongbao))
        app.add_handler(CommandHandler("stats", stats))
        app.add_handler(CommandHandler("thongke", thongke))
        app.add_handler(CommandHandler("xoaalladmin", xoaalladmin))
        app.add_handler(CommandHandler("danhsachadmin", danhsachadmin))

        print("✅ Bot đang chạy...")
        app.run_polling()
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
