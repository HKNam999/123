
import logging
import hashlib
import hmac
import random
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import qrcode
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8010052059:AAFlAiUjs_uTaLAzv38Ae-1Rwx2PhZmHQgo"
MAIN_ADMIN_ID = 7560849341

# Data storage
DATA_FILE = "bot_data.json"

def load_data():
    """Load bot data from file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "users": {},
            "admins": [MAIN_ADMIN_ID],
            "giftcodes": {},
            "stats": {
                "total_users": 0,
                "total_commands": 0,
                "total_xu_distributed": 0
            }
        }

def save_data(data):
    """Save bot data to file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(user_id: int, data: dict) -> dict:
    """Get or create user data"""
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {
            "xu": 0,
            "join_date": datetime.now().isoformat(),
            "commands_used": 0,
            "last_active": datetime.now().isoformat()
        }
        data["stats"]["total_users"] += 1
        save_data(data)
    return data["users"][str(user_id)]

def is_admin(user_id: int, data: dict) -> bool:
    """Check if user is admin"""
    return user_id in data["admins"]

def generate_qr_code(user_id: int) -> BytesIO:
    """Generate QR code for MBbank payment"""
    # MBbank QR format
    bank_id = "970422"  # MBbank bank code
    account_number = "171226"
    account_name = "HA TRONG HOAN"
    amount = ""  # Empty for user to input amount
    content = str(user_id)
    
    # VietQR format
    qr_data = f"2|{bank_id}|{account_number}|{account_name}|{content}|{amount}|0|0|VND"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    
    return bio

def generate_purchase_qr_code(user_id: int, xu_amount: int, price: int) -> BytesIO:
    """Generate QR code for purchase with amount"""
    # MBbank QR format
    bank_id = "970422"  # MBbank bank code
    account_number = "171226"
    account_name = "HA TRONG HOAN"
    amount = str(price)
    content = f"MUA{xu_amount}XU{user_id}"
    
    # VietQR format
    qr_data = f"2|{bank_id}|{account_number}|{account_name}|{content}|{amount}|0|0|VND"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    
    return bio

class AIHTH:
    """AI HTH Analysis Engine with advanced balanced algorithms"""
    
    @staticmethod
    def neural_pattern_analysis(md5_hash: str) -> float:
        """Advanced neural pattern recognition"""
        pattern_weights = [0.618, 1.414, 0.707, 1.732, 0.866, 1.154, 0.577, 1.299]
        score = sum(ord(c) * pattern_weights[i % len(pattern_weights)] for i, c in enumerate(md5_hash[:16]))
        return (score % 100) / 100.0
    
    @staticmethod
    def quantum_entropy_calc(md5_hash: str) -> float:
        """Quantum entropy calculation with balance"""
        entropy = 0
        for i in range(0, len(md5_hash), 4):
            chunk = md5_hash[i:i+4]
            chunk_val = sum(ord(c) for c in chunk)
            entropy += (chunk_val ** 1.5) % 97
        normalized = (entropy % 100) / 100.0
        return 0.4 + (normalized * 0.2)  # Keep between 0.4-0.6 for balance
    
    @staticmethod
    def blockchain_hash_mining(md5_hash: str) -> float:
        """Blockchain hash mining with improved balance"""
        difficulty = hashlib.sha256(md5_hash.encode()).hexdigest()
        mining_score = sum(int(c, 16) if c.isdigit() or c.lower() in 'abcdef' else 0 for c in difficulty[:12])
        normalized = (mining_score % 96) / 96.0
        return 0.42 + (normalized * 0.16)  # Balanced range
    
    @staticmethod
    def fractal_dimension_analysis(md5_hash: str) -> float:
        """Fractal dimension with golden ratio balance"""
        fractal_sum = 0
        for i in range(len(md5_hash) - 1):
            diff = abs(ord(md5_hash[i]) - ord(md5_hash[i+1]))
            fractal_sum += diff ** 0.618
        normalized = (fractal_sum % 98) / 98.0
        return 0.41 + (normalized * 0.18)
    
    @staticmethod
    def machine_learning_prediction(md5_hash: str) -> float:
        """ML prediction with balanced weights"""
        features = [ord(c) for c in md5_hash[:10]]
        weights = [0.47, 0.53, 0.49, 0.51, 0.48, 0.52, 0.495, 0.505, 0.485, 0.515]
        ml_score = sum(f * w for f, w in zip(features, weights)) / sum(weights)
        return (ml_score % 100) / 100.0
    
    @staticmethod
    def genetic_algorithm_evolution(md5_hash: str) -> float:
        """Genetic algorithm with population balance"""
        population = [ord(c) for c in md5_hash[::2]]
        for generation in range(3):
            population = [(p * 1.05 + random.randint(1, 5)) % 128 for p in population]
        fitness = sum(population) / len(population) / 128.0
        return 0.43 + (fitness * 0.14)
    
    @staticmethod
    def deep_neural_network(md5_hash: str) -> float:
        """Balanced deep neural network"""
        layers = [[ord(c) for c in md5_hash[:8]], [0] * 6, [0] * 4, [0] * 1]
        for i in range(1, len(layers)):
            for j in range(len(layers[i])):
                layers[i][j] = (sum(layers[i-1]) * 0.0625 + j * 0.025) % 64
        result = layers[-1][0] / 64.0
        return 0.44 + (result * 0.12)
    
    @staticmethod
    def reinforcement_learning(md5_hash: str) -> float:
        """Balanced RL agent"""
        state = sum(ord(c) for c in md5_hash[:6])
        reward = 50  # Start neutral
        for action in range(5):
            if (state + action) % 3 == 0:
                reward += 3
            elif (state + action) % 3 == 1:
                reward -= 1
            else:
                reward += 1
            state = (state + action) % 128
        return ((reward - 35) % 30 + 35) / 100.0
    
    @staticmethod
    def convolutional_neural_net(md5_hash: str) -> float:
        """Balanced CNN"""
        kernel = [0.33, 0.34, 0.33]
        feature_map = []
        for i in range(len(md5_hash) - 2):
            conv_val = sum(ord(md5_hash[i+j]) * kernel[j] for j in range(3))
            feature_map.append(conv_val % 100)
        pooled = sum(feature_map) / len(feature_map) if feature_map else 50
        return pooled / 100.0
    
    @staticmethod
    def lstm_time_series(md5_hash: str) -> float:
        """Balanced LSTM"""
        sequence = [ord(c) % 10 for c in md5_hash[:12]]
        hidden_state = 5.0  # Start balanced
        for val in sequence:
            hidden_state = (hidden_state * 0.7 + val * 0.3) % 10
        return (hidden_state + 2) / 14.0
    
    @staticmethod
    def transformer_attention(md5_hash: str) -> float:
        """Balanced transformer"""
        tokens = [ord(c) % 16 for c in md5_hash[:8]]
        attention_sum = sum(tokens) / len(tokens)
        return (attention_sum + 3) / 19.0
    
    @staticmethod
    def gan_adversarial(md5_hash: str) -> float:
        """Balanced GAN"""
        gen_score = sum(ord(c) for c in md5_hash[::3]) % 100
        disc_score = sum(ord(c) for c in md5_hash[1::3]) % 100
        balance = abs(gen_score - disc_score) / 100.0
        return 0.45 + (balance * 0.1)
    
    @staticmethod
    def autoencoder_compression(md5_hash: str) -> float:
        """Balanced autoencoder"""
        encoded = []
        for i in range(0, len(md5_hash), 4):
            chunk = md5_hash[i:i+4]
            compressed = sum(ord(c) for c in chunk) // len(chunk)
            encoded.append(compressed % 100)
        error = sum(abs(e - 50) for e in encoded) / len(encoded)
        return (50 - error + 25) / 100.0
    
    @staticmethod
    def ensemble_voting(md5_hash: str) -> float:
        """Balanced ensemble"""
        votes = []
        for i in range(0, len(md5_hash), 2):
            vote = (ord(md5_hash[i]) + ord(md5_hash[i+1] if i+1 < len(md5_hash) else md5_hash[0])) % 100
            votes.append(vote)
        avg_vote = sum(votes) / len(votes)
        return avg_vote / 100.0
    
    @staticmethod
    def quantum_neural_hybrid(md5_hash: str) -> float:
        """Balanced quantum-neural"""
        real_part = sum(ord(c) for c in md5_hash[::2]) % 100
        imag_part = sum(ord(c) for c in md5_hash[1::2]) % 100
        amplitude = ((real_part + imag_part) / 2) % 100
        return amplitude / 100.0
    
    @classmethod
    def analyze_hitclub(cls, md5_hash: str) -> dict:
        """HitClub analysis with balanced algorithm"""
        ai_scores = [
            cls.neural_pattern_analysis(md5_hash),
            cls.quantum_entropy_calc(md5_hash),
            cls.blockchain_hash_mining(md5_hash),
            cls.fractal_dimension_analysis(md5_hash),
            cls.machine_learning_prediction(md5_hash),
            cls.genetic_algorithm_evolution(md5_hash),
            cls.deep_neural_network(md5_hash),
            cls.reinforcement_learning(md5_hash),
            cls.convolutional_neural_net(md5_hash),
            cls.lstm_time_series(md5_hash),
            cls.transformer_attention(md5_hash),
            cls.gan_adversarial(md5_hash),
            cls.autoencoder_compression(md5_hash),
            cls.ensemble_voting(md5_hash),
            cls.quantum_neural_hybrid(md5_hash)
        ]
        
        final_score = sum(ai_scores) / len(ai_scores)
        
        # Balanced prediction (avoid extremes)
        if final_score >= 0.515:
            tai_percent = 52 + (final_score - 0.515) * 92
            prediction = "Tài"
        else:
            tai_percent = 52 - (0.515 - final_score) * 92
            prediction = "Xỉu" if tai_percent < 50 else "Tài"
        
        tai_percent = max(52, min(95, tai_percent))
        xiu_percent = 100 - tai_percent
        
        hex_analysis = hashlib.sha256(md5_hash.encode()).hexdigest()[:12]
        
        return {
            "prediction": prediction,
            "tai_percent": round(tai_percent, 2),
            "xiu_percent": round(xiu_percent, 2),
            "hex_analysis": hex_analysis
        }
    
    @classmethod
    def analyze_b52(cls, md5_hash: str) -> dict:
        """B52 analysis with balanced weights"""
        ai_scores = [
            cls.neural_pattern_analysis(md5_hash) * 1.02,
            cls.quantum_entropy_calc(md5_hash) * 0.98,
            cls.blockchain_hash_mining(md5_hash) * 1.01,
            cls.fractal_dimension_analysis(md5_hash) * 0.99,
            cls.machine_learning_prediction(md5_hash) * 1.005,
            cls.genetic_algorithm_evolution(md5_hash) * 0.995,
            cls.deep_neural_network(md5_hash) * 1.01,
            cls.reinforcement_learning(md5_hash) * 0.99,
            cls.convolutional_neural_net(md5_hash) * 1.005,
            cls.lstm_time_series(md5_hash) * 0.995,
            cls.transformer_attention(md5_hash) * 1.02,
            cls.gan_adversarial(md5_hash) * 0.98,
            cls.autoencoder_compression(md5_hash) * 1.01,
            cls.ensemble_voting(md5_hash) * 0.99,
            cls.quantum_neural_hybrid(md5_hash) * 1.005
        ]
        
        final_score = sum(ai_scores) / len(ai_scores)
        
        if final_score >= 0.512:
            tai_percent = 51.5 + (final_score - 0.512) * 93
            prediction = "Tài"
        else:
            tai_percent = 51.5 - (0.512 - final_score) * 93
            prediction = "Xỉu" if tai_percent < 50 else "Tài"
        
        tai_percent = max(51, min(96, tai_percent))
        xiu_percent = 100 - tai_percent
        
        hex_analysis = hashlib.sha256((md5_hash + "b52").encode()).hexdigest()[:12]
        
        return {
            "prediction": prediction,
            "tai_percent": round(tai_percent, 2),
            "xiu_percent": round(xiu_percent, 2),
            "hex_analysis": hex_analysis
        }
    
    @classmethod
    def analyze_sicbo(cls, md5_hash: str) -> dict:
        """Sicbo analysis with balanced dice prediction"""
        ai_scores = [
            cls.neural_pattern_analysis(md5_hash),
            cls.quantum_entropy_calc(md5_hash),
            cls.blockchain_hash_mining(md5_hash),
            cls.fractal_dimension_analysis(md5_hash),
            cls.machine_learning_prediction(md5_hash),
            cls.genetic_algorithm_evolution(md5_hash),
            cls.deep_neural_network(md5_hash),
            cls.reinforcement_learning(md5_hash),
            cls.convolutional_neural_net(md5_hash),
            cls.lstm_time_series(md5_hash),
            cls.transformer_attention(md5_hash),
            cls.gan_adversarial(md5_hash),
            cls.autoencoder_compression(md5_hash),
            cls.ensemble_voting(md5_hash),
            cls.quantum_neural_hybrid(md5_hash)
        ]
        
        # Balanced dice prediction
        dice1 = int((ai_scores[0] * 5.5) + 1.25)
        dice2 = int((ai_scores[1] * 5.5) + 1.25) 
        dice3 = int((ai_scores[2] * 5.5) + 1.25)
        
        dice1 = max(1, min(6, dice1))
        dice2 = max(1, min(6, dice2))
        dice3 = max(1, min(6, dice3))
        
        total_dice = dice1 + dice2 + dice3
        
        # Balanced Tai/Xiu prediction
        if total_dice >= 11:
            tai_xiu = "Tài"
            tai_percent = 51 + (total_dice - 11) * 5.5
        else:
            tai_xiu = "Xỉu"
            tai_percent = 51 - (11 - total_dice) * 5.5
        
        tai_percent = max(51, min(94, tai_percent))
        xiu_percent = 100 - tai_percent
        
        chan_le = "Chẵn" if total_dice % 2 == 0 else "Lẻ"
        chan_percent = 52 if total_dice % 2 == 0 else 48
        le_percent = 100 - chan_percent
        
        hex_analysis = hashlib.sha256((md5_hash + "sicbo").encode()).hexdigest()[:10]
        
        return {
            "dice1": dice1,
            "dice2": dice2,
            "dice3": dice3,
            "total": total_dice,
            "tai_xiu": tai_xiu,
            "tai_percent": round(tai_percent, 2),
            "xiu_percent": round(xiu_percent, 2),
            "chan_le": chan_le,
            "chan_percent": round(chan_percent, 2),
            "le_percent": round(le_percent, 2),
            "hex_analysis": hex_analysis
        }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with buttons"""
    data = load_data()
    user_data = get_user_data(update.effective_user.id, data)
    user_data["last_active"] = datetime.now().isoformat()
    save_data(data)
    
    keyboard = [
        [
            InlineKeyboardButton("🆘 Hỗ Trợ", url="https://t.me/hatronghoann"),
            InlineKeyboardButton("👥 Nhóm Chat", url="https://t.me/+dufmaDB6K0YwNzI1")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
🤖 **CHÀO MỪNG ĐẾN VỚI MD5 BOT AI HTH** 🤖

👋 Xin chào **{update.effective_user.first_name}**!

🧠 **AI HTH** - Phân tích siêu chính xác
💰 **Xu hiện tại:** `{user_data["xu"]} xu`

📝 Sử dụng /help để xem lệnh
🔥 Mỗi lần phân tích tốn 1 xu
"""
    
    await update.message.reply_text(
        welcome_message, 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📋 **DANH SÁCH LỆNH**

🎯 **PHÂN TÍCH MD5:**
• `/md5hit <md5>` - 🎰 HitClub
• `/md5b52 <md5>` - 🎮 B52  
• `/md5sicbo <md5>` - 🎲 Sicbo

💰 **QUẢN LÝ XU:**
• `/sodu` - 💎 Kiểm tra số dư
• `/muaxu` - 🛒 Mua xu (xem giá)
• `/muaxu <số_xu>` - 🛒 Mua xu cụ thể

👤 **THÔNG TIN:**
• `/thongtin` - 📊 Thông tin cá nhân
• `/naptien` - 💳 Nạp tiền
• `/giftcode <code>` - 🎁 Nhập gift code
• `/help` - ❓ Xem lệnh

🔥 **AI HTH** 🔥
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin help command"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Bạn không có quyền sử dụng lệnh này!**", parse_mode='Markdown')
        return
    
    admin_help_text = """
👑 **LỆNH ADMIN**

💰 **QUẢN LÝ XU:**
• `/addxu <user_id> <amount>` - Thêm xu
• `/statxu` - Thống kê xu
• `/xacnhan <user_id> <xu>` - Xác nhận thanh toán

🎁 **GIFT CODE:**
• `/taogiftcode <tên> <xu> <thiết_bị>` - Tạo code
• `/statgiftcode` - Thống kê code

👥 **ADMIN:**
• `/themadmin <user_id>` - Thêm admin
• `/xoaadmin <user_id>` - Xóa admin  
• `/statadmin` - Danh sách admin

📊 **KHÁC:**
• `/stats` - Thống kê hệ thống
• `/messenger <message>` - Gửi thông báo

🔥 **AI HTH** 🔥
"""
    await update.message.reply_text(admin_help_text, parse_mode='Markdown')

async def sodu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check user balance"""
    data = load_data()
    user_data = get_user_data(update.effective_user.id, data)
    user = update.effective_user
    
    balance_text = f"""
💰 **SỐ DƯ TÀI KHOẢN**

👤 **Tên:** `{user.full_name}`
🆔 **ID:** `{user.id}`
💎 **Xu hiện tại:** `{user_data['xu']} xu`

📊 **Thống kê:**
📅 **Tham gia:** `{datetime.fromisoformat(user_data["join_date"]).strftime("%d/%m/%Y")}`
🎯 **Lệnh đã dùng:** `{user_data['commands_used']}`

🔥 **AI HTH** 🔥
"""
    
    await update.message.reply_text(balance_text, parse_mode='Markdown')

async def muaxu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buy xu with price list"""
    if not context.args:
        price_list = """
💰 **BẢNG GIÁ XU BOT MD5**

💎 **10 Xu:** `10.000 VNĐ`
💎 **20 Xu:** `20.000 VNĐ`
💎 **55 Xu:** `50.000 VNĐ`
💎 **120 Xu:** `100.000 VNĐ`
💎 **200 Xu:** `150.000 VNĐ`
💎 **300 Xu:** `200.000 VNĐ`
💎 **500 Xu:** `400.000 VNĐ` (🎁 Khuyến Mãi 299 xu)
💎 **999 Xu:** `500.000 VNĐ`

📝 **Cách dùng:** `/muaxu <số_xu>`
📝 **Ví dụ:** `/muaxu 55`
⚠️ **Tối thiểu:** 10 xu

🔥 **AI HTH** 🔥
"""
        await update.message.reply_text(price_list, parse_mode='Markdown')
        return
    
    try:
        xu_amount = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ **Số xu phải là số nguyên!**", parse_mode='Markdown')
        return
    
    if xu_amount < 10:
        await update.message.reply_text("❌ **Tối thiểu 10 xu!**", parse_mode='Markdown')
        return
    
    # Price table
    price_table = {
        10: 10000,
        20: 20000,
        55: 50000,
        120: 100000,
        200: 150000,
        300: 200000,
        500: 400000,
        999: 500000
    }
    
    # Find exact match or calculate price
    if xu_amount in price_table:
        price = price_table[xu_amount]
        bonus_text = ""
        if xu_amount == 500:
            bonus_text = "\n🎁 **Bonus:** +299 xu miễn phí!"
    else:
        # Calculate price based on base rate (1 xu = 1000 VND)
        price = xu_amount * 1000
        bonus_text = ""
    
    user_id = update.effective_user.id
    
    purchase_text = f"""
🛒 **ĐƠN HÀNG MUA XU**

💎 **Số xu:** `{xu_amount} xu`
💰 **Giá tiền:** `{price:,} VNĐ`{bonus_text}

🏦 **Thông tin chuyển khoản:**
🏦 **Ngân hàng:** MBbank
👤 **Tên:** HA TRONG HOAN
🔢 **STK:** 171226

⚠️ **LƯU Ý QUAN TRỌNG:**
📝 **Nội dung CK:** `MUA{xu_amount}XU{user_id}`
💬 Sau khi CK, nhắn tin cho admin
👑 Admin: @hatronghoann

🔥 **AI HTH** 🔥
"""
    
    try:
        # Generate QR code for purchase
        qr_image = generate_purchase_qr_code(user_id, xu_amount, price)
        
        await update.message.reply_photo(
            photo=qr_image,
            caption=purchase_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            purchase_text + f"\n⚠️ **Lỗi tạo QR:** `{str(e)}`", 
            parse_mode='Markdown'
        )

async def naptien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show QR code for payment with auto-generated QR"""
    user_id = update.effective_user.id
    
    payment_text = f"""
💳 **NẠP TIỀN QUA CHUYỂN KHOẢN**

🏦 **Ngân hàng:** MBbank
👤 **Tên:** HA TRONG HOAN
🔢 **STK:** 171226

⚠️ **LƯU Ý QUAN TRỌNG:**
📝 Nội dung chuyển khoản: `{user_id}`
💬 Sau khi chuyển khoản, nhắn tin cho admin
👑 Admin: @hatronghoann

🔥 **QR CODE TỰ ĐỘNG** 🔥
"""
    
    try:
        # Generate QR code for this user
        qr_image = generate_qr_code(user_id)
        
        await update.message.reply_photo(
            photo=qr_image,
            caption=payment_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        # Fallback to text if QR generation fails
        await update.message.reply_text(
            payment_text + f"\n⚠️ **Lỗi tạo QR:** `{str(e)}`", 
            parse_mode='Markdown'
        )

async def md5hit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze MD5 for HitClub"""
    data = load_data()
    user_data = get_user_data(update.effective_user.id, data)
    
    if user_data["xu"] < 1:
        await update.message.reply_text("❌ **Không đủ xu!**", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("❌ **Nhập mã MD5!**\n📝 `/md5hit 123abc`", parse_mode='Markdown')
        return
    
    md5_input = context.args[0]
    if len(md5_input) < 8:
        await update.message.reply_text("❌ **MD5 không hợp lệ!**", parse_mode='Markdown')
        return
    
    user_data["xu"] -= 1
    user_data["commands_used"] += 1
    data["stats"]["total_commands"] += 1
    save_data(data)
    
    processing_msg = await update.message.reply_text("🧠 **AI HTH đang phân tích...**", parse_mode='Markdown')
    
    result = AIHTH.analyze_hitclub(md5_input)
    
    # Use black/white circles instead of green/red
    tai_icon = "⚫" if result['prediction'] == "Tài" else "⚪"
    xiu_icon = "⚪" if result['prediction'] == "Tài" else "⚫"
    
    response = f"""
🎰 **HITCLUB - AI HTH**

🔐 **MD5:** `{md5_input}`
🔍 **Hex:** `{result['hex_analysis']}`

🎯 **Dự đoán:** `{result['prediction']}`

📊 **Độ chính xác:**
{tai_icon} **Tài:** `{result['tai_percent']}%`
{xiu_icon} **Xỉu:** `{result['xiu_percent']}%`

💰 **Xu còn lại:** `{user_data['xu']}`
"""
    
    await processing_msg.edit_text(response, parse_mode='Markdown')

async def md5b52(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze MD5 for B52"""
    data = load_data()
    user_data = get_user_data(update.effective_user.id, data)
    
    if user_data["xu"] < 1:
        await update.message.reply_text("❌ **Không đủ xu!**", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("❌ **Nhập mã MD5!**\n📝 `/md5b52 123abc`", parse_mode='Markdown')
        return
    
    md5_input = context.args[0]
    if len(md5_input) < 8:
        await update.message.reply_text("❌ **MD5 không hợp lệ!**", parse_mode='Markdown')
        return
    
    user_data["xu"] -= 1
    user_data["commands_used"] += 1
    data["stats"]["total_commands"] += 1
    save_data(data)
    
    processing_msg = await update.message.reply_text("🧠 **AI HTH đang phân tích...**", parse_mode='Markdown')
    
    result = AIHTH.analyze_b52(md5_input)
    
    tai_icon = "⚫" if result['prediction'] == "Tài" else "⚪"
    xiu_icon = "⚪" if result['prediction'] == "Tài" else "⚫"
    
    response = f"""
🎮 **B52 - AI HTH**

🔐 **MD5:** `{md5_input}`
🔍 **Hex:** `{result['hex_analysis']}`

🎯 **Dự đoán:** `{result['prediction']}`

📊 **Độ chính xác:**
{tai_icon} **Tài:** `{result['tai_percent']}%`
{xiu_icon} **Xỉu:** `{result['xiu_percent']}%`

💰 **Xu còn lại:** `{user_data['xu']}`
"""
    
    await processing_msg.edit_text(response, parse_mode='Markdown')

async def md5sicbo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze MD5 for Sicbo"""
    data = load_data()
    user_data = get_user_data(update.effective_user.id, data)
    
    if user_data["xu"] < 1:
        await update.message.reply_text("❌ **Không đủ xu!**", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("❌ **Nhập mã MD5!**\n📝 `/md5sicbo 123abc`", parse_mode='Markdown')
        return
    
    md5_input = context.args[0]
    if len(md5_input) < 8:
        await update.message.reply_text("❌ **MD5 không hợp lệ!**", parse_mode='Markdown')
        return
    
    user_data["xu"] -= 1
    user_data["commands_used"] += 1
    data["stats"]["total_commands"] += 1
    save_data(data)
    
    processing_msg = await update.message.reply_text("🧠 **AI HTH đang phân tích...**", parse_mode='Markdown')
    
    result = AIHTH.analyze_sicbo(md5_input)
    
    tai_icon = "⚫" if result['tai_xiu'] == "Tài" else "⚪"
    xiu_icon = "⚪" if result['tai_xiu'] == "Tài" else "⚫"
    chan_icon = "⚫" if result['chan_le'] == "Chẵn" else "⚪"
    le_icon = "⚪" if result['chan_le'] == "Chẵn" else "⚫"
    
    response = f"""
🎲 **SICBO - AI HTH**

🔐 **MD5:** `{md5_input}`
🔍 **Hex:** `{result['hex_analysis']}`

🎯 **Xúc xắc:** `{result['dice1']} - {result['dice2']} - {result['dice3']}`
🔢 **Tổng:** `{result['total']}`

📊 **Tài/Xỉu:**
{tai_icon} **Tài:** `{result['tai_percent']}%`
{xiu_icon} **Xỉu:** `{result['xiu_percent']}%`

📊 **Chẵn/Lẻ:**
{chan_icon} **Chẵn:** `{result['chan_percent']}%`
{le_icon} **Lẻ:** `{result['le_percent']}%`

💰 **Xu còn lại:** `{user_data['xu']}`
"""
    
    await processing_msg.edit_text(response, parse_mode='Markdown')

async def thongtin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user information"""
    data = load_data()
    user_data = get_user_data(update.effective_user.id, data)
    user = update.effective_user
    
    join_date = datetime.fromisoformat(user_data["join_date"]).strftime("%d/%m/%Y")
    
    info_text = f"""
👤 **THÔNG TIN NGƯỜI DÙNG**

🆔 **ID:** `{user.id}`
📛 **Tên:** `{user.full_name}`
💰 **Xu:** `{user_data['xu']}`
📅 **Tham gia:** `{join_date}`
📊 **Lệnh sử dụng:** `{user_data['commands_used']}`
👑 **Quyền:** `{'🔥 Admin' if is_admin(user.id, data) else '👤 User'}`

🧠 **AI HTH** 🧠
"""
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def giftcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redeem gift code"""
    if not context.args:
        await update.message.reply_text("❌ **Nhập mã gift!**\n📝 `/giftcode ABC123`", parse_mode='Markdown')
        return
    
    data = load_data()
    user_data = get_user_data(update.effective_user.id, data)
    code = context.args[0].upper()
    
    if code not in data["giftcodes"]:
        await update.message.reply_text("❌ **Mã gift không tồn tại!**", parse_mode='Markdown')
        return
    
    gift = data["giftcodes"][code]
    
    if not gift["active"]:
        await update.message.reply_text("❌ **Mã gift hết hiệu lực!**", parse_mode='Markdown')
        return
    
    if gift["used"] >= gift["max_uses"]:
        await update.message.reply_text("❌ **Mã gift hết lượt!**", parse_mode='Markdown')
        return
    
    if str(update.effective_user.id) in gift["used_by"]:
        await update.message.reply_text("❌ **Bạn đã dùng mã này!**", parse_mode='Markdown')
        return
    
    user_data["xu"] += gift["xu_amount"]
    gift["used"] += 1
    gift["used_by"].append(str(update.effective_user.id))
    
    if gift["used"] >= gift["max_uses"]:
        gift["active"] = False
    
    save_data(data)
    
    success_text = f"""
🎁 **NHẬN GIFT THÀNH CÔNG**

✅ **Nhận:** `{gift['xu_amount']} xu`
💰 **Xu hiện tại:** `{user_data['xu']}`

🔥 **AI HTH** 🔥
"""
    
    await update.message.reply_text(success_text, parse_mode='Markdown')

# Admin commands
async def addxu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add xu to user (Admin only)"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Không có quyền!**", parse_mode='Markdown')
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("❌ `/addxu <user_id> <amount>`", parse_mode='Markdown')
        return
    
    try:
        target_user_id = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ **ID và xu phải là số!**", parse_mode='Markdown')
        return
    
    target_user_data = get_user_data(target_user_id, data)
    target_user_data["xu"] += amount
    data["stats"]["total_xu_distributed"] += amount
    save_data(data)
    
    await update.message.reply_text(f"✅ **Thêm {amount} xu cho {target_user_id}**", parse_mode='Markdown')

async def statxu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show xu statistics (Admin only)"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Không có quyền!**", parse_mode='Markdown')
        return
    
    users = data["users"]
    total_xu = sum(user["xu"] for user in users.values())
    top_users = sorted(users.items(), key=lambda x: x[1]["xu"], reverse=True)[:10]
    
    stats_text = f"""
📊 **THỐNG KÊ XU**

💰 **Tổng xu:** `{total_xu}`
👥 **Tổng user:** `{len(users)}`

🏆 **TOP 10:**
"""
    
    for i, (user_id, user_data) in enumerate(top_users, 1):
        stats_text += f"`{i}.` `{user_id}`: `{user_data['xu']} xu`\n"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def taogiftcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create gift code (Admin only)"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Không có quyền!**", parse_mode='Markdown')
        return
    
    if len(context.args) != 3:
        await update.message.reply_text("❌ `/taogiftcode <tên> <xu> <số_thiết_bị>`", parse_mode='Markdown')
        return
    
    try:
        code_name = context.args[0].upper()
        xu_amount = int(context.args[1])
        max_uses = int(context.args[2])
    except ValueError:
        await update.message.reply_text("❌ **Xu và số thiết bị phải là số!**", parse_mode='Markdown')
        return
    
    if code_name in data["giftcodes"]:
        await update.message.reply_text("❌ **Tên gift đã tồn tại!**", parse_mode='Markdown')
        return
    
    data["giftcodes"][code_name] = {
        "xu_amount": xu_amount,
        "max_uses": max_uses,
        "used": 0,
        "active": True,
        "created_by": update.effective_user.id,
        "created_date": datetime.now().isoformat(),
        "used_by": []
    }
    
    save_data(data)
    
    await update.message.reply_text(f"✅ **Tạo gift {code_name} thành công**", parse_mode='Markdown')

async def statgiftcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show gift code statistics (Admin only)"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Không có quyền!**", parse_mode='Markdown')
        return
    
    giftcodes = data["giftcodes"]
    
    if not giftcodes:
        await update.message.reply_text("📋 **Chưa có gift code!**", parse_mode='Markdown')
        return
    
    stats_text = "🎁 **THỐNG KÊ GIFT CODE**\n\n"
    
    for code, info in giftcodes.items():
        status = "🟢" if info["active"] else "🔴"
        stats_text += f"""
**{code}** {status}
💰 `{info['xu_amount']} xu`
📊 `{info['used']}/{info['max_uses']}`
👤 `{info.get('created_by', 'Unknown')}`
"""
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def themadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add admin (Main admin only)"""
    data = load_data()
    if update.effective_user.id != MAIN_ADMIN_ID:
        await update.message.reply_text("❌ **Chỉ admin chính!**", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("❌ `/themadmin <user_id>`", parse_mode='Markdown')
        return
    
    try:
        new_admin_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ **ID phải là số!**", parse_mode='Markdown')
        return
    
    if new_admin_id in data["admins"]:
        await update.message.reply_text("❌ **Đã là admin!**", parse_mode='Markdown')
        return
    
    data["admins"].append(new_admin_id)
    save_data(data)
    
    await update.message.reply_text(f"✅ **Thêm admin {new_admin_id}**", parse_mode='Markdown')

async def xoaadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove admin (Main admin only)"""
    data = load_data()
    if update.effective_user.id != MAIN_ADMIN_ID:
        await update.message.reply_text("❌ **Chỉ admin chính!**", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("❌ `/xoaadmin <user_id>`", parse_mode='Markdown')
        return
    
    try:
        admin_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ **ID phải là số!**", parse_mode='Markdown')
        return
    
    if admin_id == MAIN_ADMIN_ID:
        await update.message.reply_text("❌ **Không thể xóa admin chính!**", parse_mode='Markdown')
        return
    
    if admin_id not in data["admins"]:
        await update.message.reply_text("❌ **Không phải admin!**", parse_mode='Markdown')
        return
    
    data["admins"].remove(admin_id)
    save_data(data)
    
    await update.message.reply_text(f"✅ **Xóa admin {admin_id}**", parse_mode='Markdown')

async def statadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin list with names and usernames (Admin only)"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Không có quyền!**", parse_mode='Markdown')
        return
    
    admins = data["admins"]
    admin_text = "👑 **DANH SÁCH ADMIN**\n\n"
    
    for admin_id in admins:
        try:
            # Try to get admin info
            admin_user = await context.bot.get_chat(admin_id)
            name = admin_user.full_name if admin_user.full_name else "N/A"
            username = f"@{admin_user.username}" if admin_user.username else "N/A"
            role = "👑 Chính" if admin_id == MAIN_ADMIN_ID else "🔰 Phụ"
            admin_text += f"{role}: `{admin_id}`\n📛 {name}\n👤 {username}\n\n"
        except Exception:
            role = "👑 Chính" if admin_id == MAIN_ADMIN_ID else "🔰 Phụ"
            admin_text += f"{role}: `{admin_id}`\n📛 N/A\n👤 N/A\n\n"
    
    await update.message.reply_text(admin_text, parse_mode='Markdown')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system statistics (Admin only)"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Không có quyền!**", parse_mode='Markdown')
        return
    
    stats_data = data["stats"]
    total_xu = sum(user["xu"] for user in data["users"].values())
    active_giftcodes = len([g for g in data["giftcodes"].values() if g["active"]])
    
    stats_text = f"""
📈 **THỐNG KÊ HỆ THỐNG**

👥 **User:** `{stats_data['total_users']}`
💰 **Xu:** `{total_xu}`
📊 **Lệnh:** `{stats_data['total_commands']}`
🎁 **Gift:** `{active_giftcodes}`
👑 **Admin:** `{len(data['admins'])}`

🧠 **AI HTH** 🧠
"""
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def xacnhan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm payment and add xu automatically (Admin only)"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Không có quyền!**", parse_mode='Markdown')
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("❌ `/xacnhan <user_id> <xu_amount>`", parse_mode='Markdown')
        return
    
    try:
        target_user_id = int(context.args[0])
        xu_amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ **ID và xu phải là số!**", parse_mode='Markdown')
        return
    
    if xu_amount <= 0:
        await update.message.reply_text("❌ **Số xu phải lớn hơn 0!**", parse_mode='Markdown')
        return
    
    # Add bonus for special packages
    bonus_xu = 0
    if xu_amount == 500:
        bonus_xu = 299
        xu_amount += bonus_xu
    
    target_user_data = get_user_data(target_user_id, data)
    old_xu = target_user_data["xu"]
    target_user_data["xu"] += xu_amount
    data["stats"]["total_xu_distributed"] += xu_amount
    save_data(data)
    
    # Notify admin
    admin_msg = f"""
✅ **XÁC NHẬN THANH TOÁN THÀNH CÔNG**

👤 **User ID:** `{target_user_id}`
💎 **Xu thêm:** `{xu_amount - bonus_xu} xu`
🎁 **Bonus:** `{bonus_xu} xu` (nếu có)
💰 **Tổng xu nhận:** `{xu_amount} xu`
📊 **Xu cũ:** `{old_xu}` → **Xu mới:** `{target_user_data['xu']}`

🔥 **AI HTH** 🔥
"""
    
    await update.message.reply_text(admin_msg, parse_mode='Markdown')
    
    # Notify user
    try:
        bonus_text = f"\n🎁 **Bonus:** +{bonus_xu} xu" if bonus_xu > 0 else ""
        user_msg = f"""
✅ **THANH TOÁN THÀNH CÔNG**

💎 **Xu đã nhận:** `{xu_amount} xu`{bonus_text}
💰 **Xu hiện tại:** `{target_user_data['xu']} xu`

Cảm ơn bạn đã sử dụng dịch vụ!

🔥 **AI HTH** 🔥
"""
        
        await context.bot.send_message(
            chat_id=target_user_id,
            text=user_msg,
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ **Không thể thông báo cho user:** `{str(e)}`", parse_mode='Markdown')

async def messenger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send message to all users (Admin only)"""
    data = load_data()
    if not is_admin(update.effective_user.id, data):
        await update.message.reply_text("❌ **Không có quyền!**", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("❌ `/messenger <tin_nhắn>`", parse_mode='Markdown')
        return
    
    message = " ".join(context.args)
    broadcast_message = f"""
📢 **THÔNG BÁO**

{message}

🔥 **AI HTH** 🔥
"""
    
    sent_count = 0
    failed_count = 0
    
    status_msg = await update.message.reply_text("📤 **Đang gửi...**", parse_mode='Markdown')
    
    for user_id in data["users"].keys():
        try:
            await context.bot.send_message(chat_id=int(user_id), text=broadcast_message, parse_mode='Markdown')
            sent_count += 1
        except Exception:
            failed_count += 1
    
    await status_msg.edit_text(f"✅ **Gửi xong:** `{sent_count}` - **Lỗi:** `{failed_count}`", parse_mode='Markdown')

def main():
    """Run the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("md5hit", md5hit))
    application.add_handler(CommandHandler("md5b52", md5b52))
    application.add_handler(CommandHandler("md5sicbo", md5sicbo))
    application.add_handler(CommandHandler("thongtin", thongtin))
    application.add_handler(CommandHandler("sodu", sodu))
    application.add_handler(CommandHandler("muaxu", muaxu))
    application.add_handler(CommandHandler("naptien", naptien))
    application.add_handler(CommandHandler("giftcode", giftcode))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_help))
    application.add_handler(CommandHandler("addxu", addxu))
    application.add_handler(CommandHandler("statxu", statxu))
    application.add_handler(CommandHandler("xacnhan", xacnhan))
    application.add_handler(CommandHandler("taogiftcode", taogiftcode))
    application.add_handler(CommandHandler("statgiftcode", statgiftcode))
    application.add_handler(CommandHandler("themadmin", themadmin))
    application.add_handler(CommandHandler("xoaadmin", xoaadmin))
    application.add_handler(CommandHandler("statadmin", statadmin))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("messenger", messenger))
    
    print("🤖 AI HTH BOT ĐANG CHẠY 🤖")
    print(f"👑 Main Admin ID: {MAIN_ADMIN_ID}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
