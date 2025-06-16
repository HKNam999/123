import json
import asyncio
import websockets
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# Cấu hình bot Telegram
BOT_TOKEN = "8053826988:AAFlCP-OPKJdr9XegaryaRkX8gWmnEknwLg"  # Thay bằng token của bot
CHAT_ID = "-1002596735298"      # Thay bằng chat ID của nhóm
ADMIN_IDS = [123456789]       # Thay bằng danh sách ID của admin

# URL WebSocket
WS_URL = "ws://163.61.110.10:8000/game_sunwin/ws?id=duy914c&key=dduy1514nsadfl"

# Trạng thái bot
bot_running = False

# Khởi tạo bot Telegram
bot = Bot(token=BOT_TOKEN)

# Hàm gửi tin nhắn đến nhóm Telegram
async def send_message_to_group(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"Đã gửi tin nhắn: {message}")
    except TelegramError as e:
        print(f"Lỗi khi gửi tin nhắn Telegram: {e}")

# Hàm xử lý dữ liệu WebSocket
async def process_websocket_message(message):
    try:
        # Parse dữ liệu JSON
        data = json.loads(message)
        required_fields = ["Phien", "Xuc_xac_1", "Xuc_xac_2", "Xuc_xac_3", "Tong", "Ket_qua"]
        if not all(field in data for field in required_fields):
            print("Lỗi: Thiếu trường dữ liệu JSON")
            return

        phien = data["Phien"]
        xuc_xac_1 = data["Xuc_xac_1"]
        xuc_xac_2 = data["Xuc_xac_2"]
        xuc_xac_3 = data["Xuc_xac_3"]
        tong = data["Tong"]
        ket_qua = data["Ket_qua"]

        # Chuyển số thành emoji
        num_to_emoji = {
            1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 
            6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟",
            11: "1️⃣1️⃣", 12: "1️⃣2️⃣", 13: "1️⃣3️⃣", 14: "1️⃣4️⃣", 
            15: "1️⃣5️⃣", 16: "1️⃣6️⃣", 17: "1️⃣7️⃣", 18: "1️⃣8️⃣"
        }

        # Định dạng tin nhắn
        msg = (
            f"Kết quả mới nhất sun.win\n"
            f"=====================\n"
            f"🎲 Phiên: #{phien}\n"
            f"Xúc xắc: {num_to_emoji.get(xuc_xac_1, xuc_xac_1)}•{num_to_emoji.get(xuc_xac_2, xuc_xac_2)}•{num_to_emoji.get(xuc_xac_3, xuc_xac_3)}\n"
            f"Tổng: {num_to_emoji.get(tong, str(tong))}\n"
            f"Kết quả: {ket_qua}"
        )

        # Gửi tin nhắn đến nhóm
        await send_message_to_group(msg)
    except json.JSONDecodeError:
        print("Lỗi: Dữ liệu không phải JSON hợp lệ")
    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu: {e}")

# Hàm chạy WebSocket với reconnect
async def websocket_client():
    global bot_running
    while True:
        if not bot_running:
            await asyncio.sleep(1)
            continue
        try:
            async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=10) as ws:
                print("Đã kết nối đến WebSocket")
                while bot_running:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=60)
                        await process_websocket_message(message)
                    except asyncio.TimeoutError:
                        print("WebSocket timeout, tiếp tục lắng nghe...")
                    except websockets.ConnectionClosed:
                        print("Kết nối WebSocket bị đóng, thử kết nối lại...")
                        break
        except Exception as e:
            print(f"Lỗi kết nối WebSocket: {e}")
            if bot_running:
                print("Thử kết nối lại sau 5 giây...")
                await asyncio.sleep(5)

# Hàm xử lý lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return  # Không phản hồi nếu không phải admin

    # Tạo menu với 2 nút
    keyboard = [
        [
            InlineKeyboardButton("Bật bot", callback_data="start_bot"),
            InlineKeyboardButton("Tắt bot", callback_data="stop_bot")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Chọn hành động:", reply_markup=reply_markup)

# Hàm xử lý nút inline
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_running
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.answer("Bạn không có quyền sử dụng bot này!")
        return

    await query.answer()

    if query.data == "start_bot":
        if bot_running:
            await query.message.reply_text("Bot đã đang chạy!")
        else:
            bot_running = True
            await query.message.reply_text("Bot đã được bật!")
    
    elif query.data == "stop_bot":
        if not bot_running:
            await query.message.reply_text("Bot đã đang tắt!")
        else:
            bot_running = False
            await query.message.reply_text("Bot đã được tắt!")

# Hàm chính
async def main():
    # Tạo application
    application = Application.builder().token(BOT_TOKEN).build()

    # Thêm handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Chạy WebSocket client trong background
    asyncio.create_task(websocket_client())

    # Chạy bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
