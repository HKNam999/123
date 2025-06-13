import asyncio
import json
import logging
import os
import random
import requests
import platform
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(os.getenv("ADMIN_ID", "6020088518"))]
API_URL = "https://wanfox.x10.mx/apisan.php?key=wanfoxdz0902zzz"
API_CHECK_INTERVAL = 5
DB_FILE = "bot_data.json"
PATTERN_FILE = "pattern_data.txt"
TIMEZONE = "Asia/Ho_Chi_Minh"

# Prediction modes
PREDICTION_MODE_API = 1
PREDICTION_MODE_OPPOSITE = 2
PREDICTION_MODE_SELF = 3

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleTaiXiuBot:
    def __init__(self):
        self.running = False
        self.last_session = None
        self.prediction_mode = PREDICTION_MODE_API
        self.pattern_data = {}
        self.load_data()
        self.load_pattern_data()
    
    def load_data(self):
        """Load bot data from JSON file"""
        try:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    'users': {},
                    'keys': {},
                    'stats': {
                        'total_predictions': 0,
                        'correct_predictions': 0,
                        'accuracy': 0.0
                    },
                    'prediction_mode': PREDICTION_MODE_API,
                    'stored_predictions': {}
                }
                self.save_data()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.data = {
                'users': {},
                'keys': {},
                'stats': {
                    'total_predictions': 0,
                    'correct_predictions': 0,
                    'accuracy': 0.0
                },
                'prediction_mode': PREDICTION_MODE_API,
                'stored_predictions': {}
            }
        
        self.prediction_mode = self.data.get('prediction_mode', PREDICTION_MODE_API)
    
    def save_data(self):
        """Save bot data to JSON file"""
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def load_pattern_data(self):
        """Load pattern data from file for mode 3 predictions"""
        try:
            if os.path.exists(PATTERN_FILE):
                with open(PATTERN_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '|' in line:
                            pattern, prediction = line.split('|', 1)
                            self.pattern_data[pattern.strip()] = prediction.strip()
            logger.info(f"Loaded {len(self.pattern_data)} patterns for mode 3")
        except Exception as e:
            logger.error(f"Error loading pattern data: {e}")
            self.pattern_data = {}
    
    def get_api_data(self):
        """Fetch data from API"""
        try:
            response = requests.get(API_URL, timeout=10, verify=False)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.error(f"API returned status code: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching API data: {e}")
            return None
    
    def process_api_data(self, api_data):
        """Process API data and generate prediction based on current mode"""
        try:
            session = api_data.get('phien', 0)
            lsphien = api_data.get('lsphien', '')
            api_confidence = float(api_data.get('tincay', 50))
            api_prediction = api_data.get('dudoan', 'T')
            
            # Get previous result from lsphien[0] (leftmost = newest)
            previous_result = ''
            result_status = ''
            if len(lsphien) > 0:
                prev_char = lsphien[0]
                previous_result = 'Tài' if prev_char == 'T' else 'Xỉu'
                
                # Check if we had a prediction for previous session
                prev_session = session - 1
                if str(prev_session) in self.data['stored_predictions']:
                    stored_pred = self.data['stored_predictions'][str(prev_session)]
                    if stored_pred == previous_result:
                        result_status = ' ✅'
                        self.data['stats']['correct_predictions'] += 1
                    else:
                        result_status = ' ❌'
                    
                    self.data['stats']['total_predictions'] += 1
                    
                    if self.data['stats']['total_predictions'] > 0:
                        self.data['stats']['accuracy'] = (
                            self.data['stats']['correct_predictions'] / 
                            self.data['stats']['total_predictions']
                        ) * 100
                    
                    del self.data['stored_predictions'][str(prev_session)]
                    self.save_data()
            
            # Generate prediction based on current mode
            prediction = 'Tài'
            confidence = api_confidence
            reason = ''
            
            if self.prediction_mode == PREDICTION_MODE_API:
                prediction = 'Tài' if api_prediction == 'T' else 'Xỉu'
                confidence = api_confidence
                reason = 'Dự đoán theo API (Chế độ 1)'
                
            elif self.prediction_mode == PREDICTION_MODE_OPPOSITE:
                prediction = 'Xỉu' if api_prediction == 'T' else 'Tài'
                confidence = api_confidence
                reason = 'Dự đoán ngược API (Chế độ 2)'
                
            elif self.prediction_mode == PREDICTION_MODE_SELF:
                pattern_key = lsphien[:10] if len(lsphien) >= 10 else lsphien
                if pattern_key in self.pattern_data:
                    pred_char = self.pattern_data[pattern_key]
                    prediction = 'Tài' if pred_char == 'T' else 'Xỉu'
                    confidence = random.randint(70, 95)
                    reason = 'Phân tích độc lập từ lịch sử phiên (Chế độ 3)'
                else:
                    t_count = lsphien[:10].count('T')
                    x_count = lsphien[:10].count('X')
                    prediction = 'Xỉu' if t_count > x_count else 'Tài'
                    confidence = random.randint(60, 80)
                    reason = 'Phân tích độc lập từ lịch sử phiên (Chế độ 3)'
            
            # Store current prediction for future comparison
            self.data['stored_predictions'][str(session)] = prediction
            self.save_data()
            
            # Format pattern display (reverse for display)
            pattern_display = lsphien[::-1] if lsphien else ''
            
            # Get current time in Vietnam timezone
            vn_tz = pytz.timezone(TIMEZONE)
            current_time = datetime.now(vn_tz)
            
            result = {
                'session': session,
                'prediction': prediction,
                'confidence': confidence,
                'pattern': pattern_display[:20] + '...' if len(pattern_display) > 20 else pattern_display,
                'timestamp': current_time.strftime('%H:%M:%S'),
                'date': current_time.strftime('%d/%m/%Y'),
                'previous_result': previous_result,
                'result_status': result_status,
                'accuracy': self.data['stats']['accuracy'],
                'stats': {
                    'correct': self.data['stats']['correct_predictions'],
                    'total': self.data['stats']['total_predictions']
                },
                'prediction_mode': self.prediction_mode,
                'reason': reason
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing API data: {e}")
            return None
    
    def format_prediction_message(self, data):
        """Format prediction message"""
        session = data.get('session', 'N/A')
        prediction = data.get('prediction', 'N/A')
        confidence = data.get('confidence', 50.0)
        pattern = data.get('pattern', '')
        timestamp = data.get('timestamp', 'N/A')
        date = data.get('date', 'N/A')
        previous_result = data.get('previous_result', '')
        result_status = data.get('result_status', '')
        accuracy = data.get('accuracy', 0.0)
        stats = data.get('stats', {'correct': 0, 'total': 0})
        prediction_mode = data.get('prediction_mode', 1)
        reason = data.get('reason', '')
        
        # Confidence level emoji
        if confidence >= 85:
            confidence_level = "Rất cao"
            conf_emoji = "🔥"
        elif confidence >= 70:
            confidence_level = "Cao"
            conf_emoji = "💎"
        elif confidence >= 60:
            confidence_level = "Khá"
            conf_emoji = "⚡"
        else:
            confidence_level = "Trung bình"
            conf_emoji = "💫"
        
        message = f"🎰 TÀI XỈU BOT v10.1\n"
        message += f"═══════════════════════════════\n"
        
        if previous_result:
            message += f"🆔 Phiên #{session - 1}\n"
            message += f"📊 Kết quả: {previous_result}{result_status}\n"
            message += f"─────────────────────────────\n"
        
        message += f"🔮 DỰ ĐOÁN PHIÊN #{session}:\n"
        message += f"{conf_emoji} {prediction}\n"
        message += f"📈 Tin cậy: {confidence_level} ({confidence:.1f}%)\n"
        message += f"🧠 Logic: {reason}\n"
        message += f"📊 Độ chính xác: {accuracy:.1f}% ({stats['correct']}/{stats['total']})\n"
        
        if pattern:
            message += f"📉 Pattern: {pattern}\n"
        
        message += f"⏰ {timestamp} • {date}\n"
        message += f"═══════════════════════════════\n"
        
        # Add mode indicator in footer
        mode_text = {
            1: "Chế độ API",
            2: "Chế độ Ngược API", 
            3: "Chế độ Tự Phân Tích"
        }
        message += f"🤖 Enhanced AI v10.1 • {mode_text.get(prediction_mode, 'Chế độ API')} • Phân tích thời gian thực"
        
        return message
    
    async def send_telegram_message(self, chat_id, message):
        """Send message via Telegram Bot API"""
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN not set")
            return False
            
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def send_telegram_message_with_keyboard(self, chat_id, message, keyboard):
        """Send message with inline keyboard via Telegram Bot API"""
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN not set")
            return False
            
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': {
                'inline_keyboard': keyboard
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def answer_callback_query(self, callback_id, text=""):
        """Answer callback query"""
        if not BOT_TOKEN:
            return False
            
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
        data = {
            'callback_query_id': callback_id,
            'text': text
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error answering callback: {e}")
            return False
    
    async def handle_telegram_updates(self):
        """Handle incoming Telegram updates"""
        if not BOT_TOKEN:
            return
            
        offset = 0
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        
        while self.running:
            try:
                params = {'offset': offset, 'timeout': 10}
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('ok') and data.get('result'):
                        for update in data['result']:
                            offset = update['update_id'] + 1
                            
                            if 'message' in update:
                                message = update['message']
                                chat_id = message['chat']['id']
                                user_id = message['from']['id']
                                text = message.get('text', '').strip()
                                
                                if text.startswith('/start'):
                                    await self.handle_start_command(chat_id, user_id, message['from'])
                                elif text.startswith('/menu'):
                                    await self.handle_menu_command(chat_id, user_id)
                                elif text.startswith('/stats'):
                                    await self.handle_stats_command(chat_id, user_id)
                                elif text.startswith('/set') and user_id in ADMIN_IDS:
                                    await self.handle_set_command(chat_id, text)
                                elif text.startswith('/health'):
                                    await self.handle_health_command(chat_id, user_id)
                                elif text.startswith('/key'):
                                    await self.handle_key_command(chat_id, user_id, text)
                                elif text.startswith('/taokey') and user_id in ADMIN_IDS:
                                    await self.handle_create_key_command(chat_id, text)
                                elif text == 'Chạy bot':
                                    await self.handle_start_bot_button(chat_id, user_id)
                                elif text == 'Tắt bot':
                                    await self.handle_stop_bot_button(chat_id, user_id)
                                elif text == 'Thống kê':
                                    await self.handle_stats_command(chat_id, user_id)
                                elif text == 'Trợ giúp':
                                    await self.handle_help_button(chat_id, user_id)
                            
                            elif 'callback_query' in update:
                                callback = update['callback_query']
                                chat_id = callback['message']['chat']['id']
                                user_id = callback['from']['id']
                                data = callback.get('data', '')
                                
                                await self.handle_callback_query(chat_id, user_id, data, callback['id'])
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error handling updates: {e}")
                await asyncio.sleep(5)
    
    async def handle_start_command(self, chat_id, user_id, user_info):
        """Handle /start command"""
        username = user_info.get('username', '')
        first_name = user_info.get('first_name', '')
        
        vn_tz = pytz.timezone(TIMEZONE)
        current_time = datetime.now(vn_tz).strftime('%H:%M %d/%m/%Y')
        
        # Add user to database
        if str(user_id) not in self.data['users']:
            self.data['users'][str(user_id)] = {
                'username': username,
                'first_name': first_name,
                'active': False,
                'joined_date': current_time,
                'key_id': None,
                'key_expires': None,
                'predictions_received': 0
            }
            self.save_data()
        
        if user_id in ADMIN_IDS:
            message = f"""🎰 TÀI XỈU BOT v10.1 ENHANCED
══════════════════════════════

🚀 Tính năng v10.1:
• 🧠 Enhanced AI prediction với độ chính xác cao
• 📊 Multi-strategy analysis
• ⚡ Real-time API monitoring mỗi 5 giây
• 📈 Pattern recognition thông minh
• 🔐 Secure key management system
• 🤖 Termux Android optimized

👑 ADMIN MODE ACTIVATED
📱 Hướng dẫn sử dụng:
• ▶️ Nhấn 'Chạy bot' để bắt đầu nhận dự đoán
• ⏹️ Nhấn 'Tắt bot' để dừng nhận dự đoán
• 📊 Xem thống kê hiệu suất và độ chính xác
• ℹ️ Xem hướng dẫn chi tiết
• /menu - Xem tất cả lệnh có sẵn

👤 Thông tin:
• User: @{username}
• ID: {user_id}
• Chat: private
• Thời gian: {current_time}

🌐 Trạng thái: 🟢 Online & Monitoring

👨‍💻 ADMIN: t.me/hknamvip"""
            
            # Create inline keyboard for admin
            keyboard = [
                [{"text": "📋 Menu", "callback_data": "menu"}],
                [{"text": "▶️ Chạy bot", "callback_data": "start_bot"}, 
                 {"text": "⏹️ Tắt bot", "callback_data": "stop_bot"}],
                [{"text": "📊 Thống kê", "callback_data": "stats"},
                 {"text": "🏥 Health Check", "callback_data": "health"}],
                [{"text": "ℹ️ Trợ giúp", "callback_data": "help"}]
            ]
            
        else:
            message = f"""🎰 TÀI XỈU BOT v10.1
════════════════════

✨ Chào mừng bạn đến với bot dự đoán!

📊 Tính năng:
• 🎯 Dự đoán tài xỉu chính xác cao
• 📈 Phân tích pattern thông minh
• ⚡ Cập nhật real-time

🎮 Hướng dẫn:
• /menu - Xem danh sách lệnh
• Nút "Trợ giúp" - Xem hướng dẫn chi tiết

👤 Thông tin:
• User: @{username}
• ID: {user_id}
• Thời gian: {current_time}

👨‍💻 Liên hệ ADMIN: @hknamvip"""
            
            # Create inline keyboard for regular user
            keyboard = [
                [{"text": "📋 Menu", "callback_data": "menu"}],
                [{"text": "📊 Thống kê", "callback_data": "stats"},
                 {"text": "🏥 Health Check", "callback_data": "health"}],
                [{"text": "ℹ️ Trợ giúp", "callback_data": "help"}]
            ]
        
        await self.send_telegram_message_with_keyboard(chat_id, message, keyboard)
    
    async def handle_menu_command(self, chat_id, user_id):
        """Handle /menu command"""
        if user_id in ADMIN_IDS:
            message = """📋 MENU LỆNH ADMIN

🔧 Quản lý Bot:
• /start - Khởi động bot
• /stats - Xem thống kê chi tiết
• /health - Kiểm tra hệ thống

⚙️ Cài đặt:
• /set 1 - Dự đoán theo API
• /set 2 - Dự đoán ngược API
• /set 3 - Dự đoán pattern file

🔐 Key Management:
• /taokey <key_id> <số_lượt> <số_giờ> - Tạo key mới
• Ví dụ: /taokey ABC123 10 24

👨‍💻 ADMIN: @hknamvip"""
        else:
            message = """📋 MENU LỆNH

🎮 Lệnh cơ bản:
• /start - Khởi động bot
• /stats - Xem thống kê
• /key <key_id> - Kích hoạt key

👨‍💻 Liên hệ: @hknamvip"""
        
        await self.send_telegram_message(chat_id, message)
    
    async def handle_stats_command(self, chat_id, user_id):
        """Handle /stats command"""
        stats = self.data['stats']
        total = stats.get("total_predictions", 0)
        correct = stats.get("correct_predictions", 0)
        accuracy = stats.get("accuracy", 0.0)
        
        if accuracy >= 70:
            accuracy_emoji = "🎯"
            status = "Xuất sắc"
        elif accuracy >= 60:
            accuracy_emoji = "✅"
            status = "Tốt"
        elif accuracy >= 50:
            accuracy_emoji = "📊"
            status = "Trung bình"
        else:
            accuracy_emoji = "📈"
            status = "Cải thiện"
        
        mode_text = {
            1: "🎯 Theo API",
            2: "🔄 Ngược API",
            3: "🧠 Tự dự đoán"
        }
        
        message = f"""📊 THỐNG KÊ DỰ ĐOÁN

🎲 Tổng dự đoán: {total}
✅ Dự đoán đúng: {correct}
❌ Dự đoán sai: {total - correct}
{accuracy_emoji} Độ chính xác: {accuracy:.1f}%
📈 Đánh giá: {status}
⚙️ Chế độ hiện tại: {mode_text.get(self.prediction_mode, '🎯 Theo API')}

{f'Dựa trên {total} dự đoán gần đây' if total > 0 else 'Chưa có dự đoán nào được ghi nhận.'}"""
        
        await self.send_telegram_message(chat_id, message)
    
    async def handle_set_command(self, chat_id, text):
        """Handle /set command"""
        parts = text.split()
        if len(parts) < 2:
            message = """📝 Sử dụng: /set <mode>

1 - Dự đoán theo API
2 - Dự đoán ngược API
3 - Dự đoán pattern file"""
            await self.send_telegram_message(chat_id, message)
            return
        
        try:
            mode = int(parts[1])
            if mode not in [1, 2, 3]:
                await self.send_telegram_message(chat_id, "❌ Mode không hợp lệ. Chỉ chấp nhận 1, 2, hoặc 3.")
                return
            
            self.prediction_mode = mode
            self.data['prediction_mode'] = mode
            self.save_data()
            
            mode_names = {
                1: "🎯 Dự đoán theo API",
                2: "🔄 Dự đoán ngược API",
                3: "🧠 Dự đoán pattern file"
            }
            
            await self.send_telegram_message(chat_id, f"✅ Đã chuyển sang {mode_names[mode]}")
            logger.info(f"Admin changed mode to {mode}")
            
        except ValueError:
            await self.send_telegram_message(chat_id, "❌ Mode phải là số (1, 2, hoặc 3).")
    
    async def handle_health_command(self, chat_id, user_id):
        """Handle /health command"""
        try:
            current_dt = datetime.now()
            
            system_info = {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'architecture': platform.machine(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available': round(psutil.virtual_memory().available / (1024**3), 2),
                'memory_percent': psutil.virtual_memory().percent,
                'cpu_percent': psutil.cpu_percent(interval=1),
                'boot_time': current_dt.fromtimestamp(psutil.boot_time()).strftime('%d/%m/%Y %H:%M:%S')
            }
            
            # Check API status
            api_status = "🔴"
            try:
                response = requests.get(API_URL, timeout=5, verify=False)
                if response.status_code == 200:
                    data = response.json()
                    if 'phien' in data:
                        api_status = "🟢"
            except:
                pass
            
            mode_text = {
                1: "🎯 Theo API",
                2: "🔄 Ngược API",
                3: "🧠 Tự dự đoán"
            }
            
            message = f"""🏥 HEALTH CHECK

🖥️ System: {system_info['platform']} {system_info['platform_release']}
🔧 Architecture: {system_info['architecture']}
💾 Memory: {system_info['memory_available']}GB/{system_info['memory_total']}GB ({100-system_info['memory_percent']:.1f}% free)
⚡ CPU: {system_info['cpu_count']} cores ({100-system_info['cpu_percent']:.1f}% free)
🌐 API Status: {api_status}
🕒 Uptime: Since {system_info['boot_time']}
📊 Bot Mode: {mode_text.get(self.prediction_mode, '🎯 Theo API')}
📈 Accuracy: {self.data['stats']['accuracy']:.1f}%"""
            
            await self.send_telegram_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            await self.send_telegram_message(chat_id, f"❌ Health Check Error: {str(e)}")
    
    # Key Management Methods
    def create_key(self, key_id: str, uses: int, hours: int) -> bool:
        """Create a new key"""
        try:
            vn_tz = pytz.timezone(TIMEZONE)
            created_time = datetime.now(vn_tz)
            expires_time = created_time + timedelta(hours=hours)
            
            self.data['keys'][key_id] = {
                'uses_left': uses,
                'max_uses': uses,
                'created_date': created_time.strftime('%d/%m/%Y %H:%M:%S'),
                'expires_date': expires_time.strftime('%d/%m/%Y %H:%M:%S'),
                'expires_timestamp': expires_time.timestamp(),
                'used_by': [],
                'active': True
            }
            self.save_data()
            return True
        except Exception as e:
            logger.error(f"Error creating key: {e}")
            return False
    
    def is_key_valid(self, key_id: str, user_id: int) -> bool:
        """Check if key is valid for user"""
        try:
            if key_id not in self.data['keys']:
                return False
            
            key_data = self.data['keys'][key_id]
            
            # Check if key is active
            if not key_data.get('active', False):
                return False
            
            # Check if key has expired
            vn_tz = pytz.timezone(TIMEZONE)
            current_time = datetime.now(vn_tz)
            expires_timestamp = key_data.get('expires_timestamp', 0)
            
            if current_time.timestamp() > expires_timestamp:
                return False
            
            # Check if user already used this key
            if user_id in key_data.get('used_by', []):
                return False
            
            # Check if key has uses left
            if key_data.get('uses_left', 0) <= 0:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking key validity: {e}")
            return False
    
    def use_key(self, key_id: str, user_id: int) -> bool:
        """Use a key for user"""
        try:
            if not self.is_key_valid(key_id, user_id):
                return False
            
            key_data = self.data['keys'][key_id]
            
            # Add user to used_by list
            if 'used_by' not in key_data:
                key_data['used_by'] = []
            key_data['used_by'].append(user_id)
            
            # Decrease uses left
            key_data['uses_left'] = key_data.get('uses_left', 0) - 1
            
            # Set user key and active status
            user_data = self.data['users'].get(str(user_id), {})
            user_data['key_id'] = key_id
            user_data['active'] = True
            
            # Set expiry for user
            expires_timestamp = key_data.get('expires_timestamp', 0)
            vn_tz = pytz.timezone(TIMEZONE)
            expires_date = datetime.fromtimestamp(expires_timestamp, vn_tz)
            user_data['key_expires'] = expires_date.strftime('%d/%m/%Y %H:%M:%S')
            
            self.data['users'][str(user_id)] = user_data
            self.save_data()
            return True
            
        except Exception as e:
            logger.error(f"Error using key: {e}")
            return False
    
    def get_key_info(self, key_id: str):
        """Get key information"""
        return self.data['keys'].get(key_id)
    
    async def handle_key_command(self, chat_id, user_id, text):
        """Handle /key command"""
        parts = text.split()
        if len(parts) < 2:
            message = """📝 Sử dụng: /key <key_id>
            
Ví dụ: /key ABC123"""
            await self.send_telegram_message(chat_id, message)
            return
        
        key_id = parts[1].strip()
        
        if self.is_key_valid(key_id, user_id):
            if self.use_key(key_id, user_id):
                key_info = self.get_key_info(key_id)
                vn_tz = pytz.timezone(TIMEZONE)
                expires_timestamp = key_info.get('expires_timestamp', 0)
                expires_date = datetime.fromtimestamp(expires_timestamp, vn_tz)
                
                message = f"""✅ Kích hoạt key thành công!

🔑 Key ID: {key_id}
⏰ Hết hạn: {expires_date.strftime('%d/%m/%Y %H:%M:%S')}
✨ Bạn đã được kích hoạt nhận dự đoán!

Chúc bạn may mắn! 🍀"""
                await self.send_telegram_message(chat_id, message)
                logger.info(f"User {user_id} activated key {key_id}")
            else:
                await self.send_telegram_message(chat_id, "❌ Lỗi khi kích hoạt key. Vui lòng thử lại.")
        else:
            await self.send_telegram_message(chat_id, "❌ Key không hợp lệ hoặc đã hết hạn.")
    
    async def handle_create_key_command(self, chat_id, text):
        """Handle /taokey command"""
        parts = text.split()
        if len(parts) < 4:
            message = """📝 Sử dụng: /taokey <key_id> <số_lượt> <số_giờ>

Ví dụ: /taokey ABC123 10 24
- ABC123: ID của key
- 10: Số lượt sử dụng
- 24: Số giờ có hiệu lực"""
            await self.send_telegram_message(chat_id, message)
            return
        
        try:
            key_id = parts[1].strip()
            uses = int(parts[2])
            hours = int(parts[3])
            
            if key_id in self.data['keys']:
                await self.send_telegram_message(chat_id, f"❌ Key {key_id} đã tồn tại.")
                return
            
            if uses <= 0 or hours <= 0:
                await self.send_telegram_message(chat_id, "❌ Số lượt và số giờ phải lớn hơn 0.")
                return
            
            if self.create_key(key_id, uses, hours):
                vn_tz = pytz.timezone(TIMEZONE)
                expires_time = datetime.now(vn_tz) + timedelta(hours=hours)
                
                message = f"""✅ Tạo key thành công!

🔑 Key ID: {key_id}
🎯 Số lượt: {uses}
⏰ Thời hạn: {hours} giờ
📅 Hết hạn: {expires_time.strftime('%d/%m/%Y %H:%M:%S')}

Chia sẻ key này với người dùng để họ kích hoạt."""
                await self.send_telegram_message(chat_id, message)
                logger.info(f"Admin created key {key_id} with {uses} uses for {hours} hours")
            else:
                await self.send_telegram_message(chat_id, "❌ Lỗi khi tạo key.")
                
        except ValueError:
            await self.send_telegram_message(chat_id, "❌ Số lượt và số giờ phải là số nguyên.")
        except Exception as e:
            await self.send_telegram_message(chat_id, f"❌ Lỗi: {str(e)}")
    
    # Button Handlers
    async def handle_start_bot_button(self, chat_id, user_id):
        """Handle start bot button"""
        user_data = self.data['users'].get(str(user_id), {})
        
        # Check if user has valid key
        key_id = user_data.get('key_id')
        if not key_id or not self.is_key_valid(key_id, user_id):
            if user_id not in ADMIN_IDS:
                await self.send_telegram_message(chat_id, "❌ Bạn cần key hợp lệ để nhận dự đoán. Sử dụng /key <key_id> để kích hoạt.")
                return
        
        user_data['active'] = True
        self.data['users'][str(user_id)] = user_data
        self.save_data()
        
        await self.send_telegram_message(chat_id, "✅ Bot đã được kích hoạt! Bạn sẽ nhận được dự đoán tự động.")
    
    async def handle_stop_bot_button(self, chat_id, user_id):
        """Handle stop bot button"""
        user_data = self.data['users'].get(str(user_id), {})
        user_data['active'] = False
        self.data['users'][str(user_id)] = user_data
        self.save_data()
        
        await self.send_telegram_message(chat_id, "⏹️ Bot đã được tắt. Bạn sẽ không nhận dự đoán nữa.")
    
    async def handle_help_button(self, chat_id, user_id):
        """Handle help button"""
        help_text = """📖 HƯỚNG DẪN SỬ DỤNG

🎯 Bot dự đoán tài xỉu tự động:
• Bot sẽ gửi dự đoán mỗi phiên mới
• Độ chính xác cao dựa trên AI
• Theo dõi kết quả real-time

🔑 Kích hoạt:
• Sử dụng /key <key_id> để kích hoạt
• Nhấn "Chạy bot" để bắt đầu nhận dự đoán
• Nhấn "Tắt bot" để dừng

💡 Lưu ý:
• Chỉ tham khảo, không đảm bảo 100%
• Chơi có trách nhiệm
• Quản lý vốn hợp lý

📞 Hỗ trợ: @hknamvip"""
        await self.send_telegram_message(chat_id, help_text)
    
    async def handle_callback_query(self, chat_id, user_id, data, callback_id):
        """Handle inline keyboard button presses"""
        await self.answer_callback_query(callback_id)
        
        if data == "menu":
            await self.handle_menu_command(chat_id, user_id)
        elif data == "stats":
            await self.handle_stats_command(chat_id, user_id)
        elif data == "health":
            await self.handle_health_command(chat_id, user_id)
        elif data == "help":
            await self.handle_help_button(chat_id, user_id)
        elif data == "start_bot":
            await self.handle_start_bot_button(chat_id, user_id)
        elif data == "stop_bot":
            await self.handle_stop_bot_button(chat_id, user_id)
    
    async def broadcast_predictions(self, prediction_data):
        """Broadcast predictions to active users"""
        message = self.format_prediction_message(prediction_data)
        
        # Print to console
        print(f"\n{message}\n")
        
        # Send to all active users
        sent_count = 0
        for user_id_str, user_data in self.data['users'].items():
            user_id = int(user_id_str)
            
            # Check if user is active
            if not user_data.get('active', False):
                continue
            
            # Check if user has valid key (skip for admins)
            if user_id not in ADMIN_IDS:
                key_id = user_data.get('key_id')
                if not key_id:
                    continue
                
                # Check if key is still valid
                vn_tz = pytz.timezone(TIMEZONE)
                current_time = datetime.now(vn_tz)
                key_expires = user_data.get('key_expires')
                if key_expires:
                    try:
                        expires_dt = datetime.strptime(key_expires, '%d/%m/%Y %H:%M:%S')
                        expires_dt = vn_tz.localize(expires_dt)
                        if current_time > expires_dt:
                            # Key expired, deactivate user
                            user_data['active'] = False
                            self.save_data()
                            continue
                    except:
                        continue
            
            # Send prediction to user
            success = await self.send_telegram_message(user_id, message)
            if success:
                sent_count += 1
                user_data['predictions_received'] = user_data.get('predictions_received', 0) + 1
                logger.info(f"Sent prediction to user {user_id}")
        
        if sent_count > 0:
            self.save_data()
            logger.info(f"Broadcast sent to {sent_count} active users")
    
    async def api_monitoring_loop(self):
        """Main API monitoring loop"""
        logger.info("Starting API monitoring loop")
        
        while self.running:
            try:
                api_data = self.get_api_data()
                if api_data:
                    current_session = api_data.get('phien')
                    
                    if current_session != self.last_session:
                        self.last_session = current_session
                        logger.info(f"New session detected: {current_session}")
                        
                        prediction_data = self.process_api_data(api_data)
                        if prediction_data:
                            await self.broadcast_predictions(prediction_data)
                
                await asyncio.sleep(API_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in API monitoring loop: {e}")
                await asyncio.sleep(API_CHECK_INTERVAL)
    
    async def run(self):
        """Run the bot"""
        logger.info("Starting Simple Tai Xiu Bot")
        
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN not set, running in console mode only")
        else:
            logger.info("BOT_TOKEN found, enabling Telegram features")
        
        self.running = True
        
        # Start both monitoring tasks
        tasks = [
            asyncio.create_task(self.api_monitoring_loop()),
        ]
        
        if BOT_TOKEN:
            tasks.append(asyncio.create_task(self.handle_telegram_updates()))
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            self.running = False

async def main():
    bot = SimpleTaiXiuBot()
    
    # Test functions first
    logger.info("Testing API connection...")
    api_data = bot.get_api_data()
    if api_data:
        logger.info("✅ API connection successful")
        prediction = bot.process_api_data(api_data)
        if prediction:
            message = bot.format_prediction_message(prediction)
            logger.info(f"✅ Prediction generated")
    else:
        logger.error("❌ API connection failed")
    
    # Start the bot
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())