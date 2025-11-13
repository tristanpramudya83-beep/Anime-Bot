import discord
import discord
from discord.ext import commands
import google.generativeai as genai
import os
import aiohttp
import io
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

# Configure Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Game settings
VIP_PRICE = 10000  # Points needed to buy VIP
DAILY_REWARD = 100  # Daily login reward
GAME_REWARD_MIN = 10
GAME_REWARD_MAX = 50

# Character gacha data
CHARACTER_GACHA = {
    "SSR": {  # 5% chance
        "chance": 5,
        "characters": [
            {"name": "Rem", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/10/24/20/39/03/136647945_p0_square1200.jpg", "anime": "Re:Zero"},
            {"name": "Mikasa", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/11/05/22/12/48/137133871_p0_square1200.jpg", "anime": "Attack on Titan"},
            {"name": "Zero Two", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/09/27/00/32/32/135545960_p0_square1200.jpg", "anime": "Darling in the Franxx"},
            {"name": "Alya", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/11/09/14/01/37/137269614_p0_square1200.jpg", "anime": "Roshidere"},
            {"name": "Asuna", "image": "https://i.pximg.net/c/250x250_80_a2/custom-thumb/img/2025/10/28/12/02/51/136792583_p0_custom1200.jpg", "anime": "Sword Art Online"}
        ]
    },
    "SR": {  # 15% chance
        "chance": 15,
        "characters": [
            {"name": "Hinata", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/10/08/04/47/47/136008613_p0_square1200.jpg", "anime": "Naruto"},
            {"name": "Ochaco", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/11/04/21/37/48/137094463_p0_square1200.jpg", "anime": "My Hero Academia"},
            {"name": "Lucy", "image": "https://i.pximg.net/c/250x250_80_a2/custom-thumb/img/2025/11/06/10/27/33/137150477_p0_custom1200.jpg", "anime": "Fairy Tail"},
            {"name": "Yoruichi", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/11/08/00/54/54/137212368_p0_square1200.jpg", "anime": "Bleach"},
            {"name": "Winry", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/10/04/11/30/34/135855101_p0_square1200.jpg", "anime": "Fullmetal Alchemist"}
        ]
    },
    "R": {  # 30% chance
        "chance": 30,
        "characters": [
            {"name": "Itsuki", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/11/02/08/24/42/136994040_p0_square1200.jpg", "anime": "Gotoubun no Hanayome"},
            {"name": "Nino", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/10/24/10/22/10/136632672_p0_square1200.jpg", "anime": "Gotoubun no Hanayome"},
            {"name": "Waguri", "image": "https://i.pximg.net/c/250x250_80_a2/custom-thumb/img/2025/09/04/19/19/50/134705517_p0_custom1200.jpg", "anime": "Kaoru Hana wa Rin to Saku"},
            {"name": "Erza", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/09/06/23/01/54/134792097_p0_square1200.jpg", "anime": "Fairy Tail"},
            {"name": "Inori", "image": "https://i.pximg.net/c/250x250_80_a2/custom-thumb/img/2025/09/23/01/37/47/135426424_p0_custom1200.jpg", "anime": "Guilty Crown"}
        ]
    },
    "N": {  # 50% chance
        "chance": 50,
        "characters": [
            {"name": "Yuki", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2025/05/27/05/31/50/130857774_p0_square1200.jpg", "anime": "Roshidere"},
            {"name": "Yui", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2024/12/23/23/00/29/125463133_p0_square1200.jpg", "anime": "K-On!"},
            {"name": "Mio", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2024/03/20/00/55/09/117074256_p0_square1200.jpg", "anime": "K-On!"},
            {"name": "Ritsu", "image": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2021/09/25/00/04/15/92990847_p0_square1200.jpg", "anime": "K-On!"},
            {"name": "Miku", "image": "https://i.pximg.net/c/250x250_80_a2/custom-thumb/img/2025/06/21/14/28/31/131803442_p0_custom1200.jpg", "anime": "Gotoubun no Hanayome"}
        ]
    }
}

# Data storage paths
DATA_DIR = Path('user_data')
DATA_DIR.mkdir(exist_ok=True)
BOT_IDENTITIES_FILE = DATA_DIR / 'bot_identities.json'
CHAT_HISTORY_DIR = DATA_DIR / 'chat_history'
CHAT_HISTORY_DIR.mkdir(exist_ok=True)
USER_POINTS_FILE = DATA_DIR / 'user_points.json'
USER_VIP_FILE = DATA_DIR / 'user_vip.json'
USER_CHARACTERS_FILE = DATA_DIR / 'user_characters.json'
DAILY_CLAIMS_FILE = DATA_DIR / 'daily_claims.json'
STICKERS_DIR = DATA_DIR / 'stickers'
STICKERS_DIR.mkdir(exist_ok=True)
EMOJIS_DIR = DATA_DIR / 'emojis'
EMOJIS_DIR.mkdir(exist_ok=True)
SOUNDBOARDS_DIR = DATA_DIR / 'soundboards'
SOUNDBOARDS_DIR.mkdir(exist_ok=True)

# Load or initialize bot identities
def load_bot_identities():
    if BOT_IDENTITIES_FILE.exists():
        try:
            with open(BOT_IDENTITIES_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:  # File is empty
                    print("[WARNING] bot_identities.json is empty, initializing...")
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Corrupted bot_identities.json: {e}")
            print("[INFO] Backing up corrupted file and creating new one...")
            # Backup the corrupted file
            import shutil
            backup_path = DATA_DIR / f'bot_identities.json.backup'
            shutil.copy(BOT_IDENTITIES_FILE, backup_path)
            print(f"[INFO] Backup saved to: {backup_path}")
            return {}
    return {}

def save_bot_identities(identities):
    with open(BOT_IDENTITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(identities, f, indent=2, ensure_ascii=False)

def load_chat_history(user_id):
    history_file = CHAT_HISTORY_DIR / f'{user_id}.json'
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:  # File is empty
                    return []
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Corrupted chat history for user {user_id}: {e}")
            return []  # Return empty history if corrupted
    return []

def save_chat_history(user_id, history):
    history_file = CHAT_HISTORY_DIR / f'{user_id}.json'
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def add_to_chat_history(user_id, role, content):
    history = load_chat_history(user_id)
    history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat()
    })
    # Keep last 50 messages to avoid excessive memory usage
    if len(history) > 50:
        history = history[-50:]
    save_chat_history(user_id, history)
    return history

bot_identities = load_bot_identities()

# Points and VIP system functions
def load_user_points():
    if USER_POINTS_FILE.exists():
        with open(USER_POINTS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    return {}

def save_user_points(points_data):
    with open(USER_POINTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(points_data, f, indent=2, ensure_ascii=False)

def load_user_vip():
    if USER_VIP_FILE.exists():
        with open(USER_VIP_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    return {}

def save_user_vip(vip_data):
    with open(USER_VIP_FILE, 'w', encoding='utf-8') as f:
        json.dump(vip_data, f, indent=2, ensure_ascii=False)

def load_daily_claims():
    if DAILY_CLAIMS_FILE.exists():
        with open(DAILY_CLAIMS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    return {}

def save_daily_claims(claims_data):
    with open(DAILY_CLAIMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(claims_data, f, indent=2, ensure_ascii=False)

def load_user_characters():
    if USER_CHARACTERS_FILE.exists():
        try:
            with open(USER_CHARACTERS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    # Ensure we return a dictionary
                    return data if isinstance(data, dict) else {}
                return {}
        except (json.JSONDecodeError, Exception) as e:
            print(f"[ERROR] Error loading user characters: {e}")
            return {}
    return {}

def get_user_characters(user_id):
    """Get characters for specific user"""
    characters_data = load_user_characters()
    user_chars = characters_data.get(user_id, {})
    # Ensure we return a dictionary, not None
    return user_chars if isinstance(user_chars, dict) else {}

def save_user_characters(characters_data):
    with open(USER_CHARACTERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(characters_data, f, indent=2, ensure_ascii=False)

def add_character_to_inventory(user_id, character, tier):
    inventory = load_user_characters()
    if user_id not in inventory:
        inventory[user_id] = {}
    
    char_name = character["name"]
    if char_name not in inventory[user_id]:
        inventory[user_id][char_name] = {
            "name": character["name"],
            "anime": character["anime"],
            "image": character["image"],
            "tier": tier,
            "count": 1
        }
    else:
        inventory[user_id][char_name]["count"] += 1
    
    save_user_characters(inventory)
    return True

def get_user_points(user_id):
    points_data = load_user_points()
    return points_data.get(user_id, 0)

def add_user_points(user_id, amount):
    points_data = load_user_points()
    points_data[user_id] = points_data.get(user_id, 0) + amount
    save_user_points(points_data)
    return points_data[user_id]

def deduct_user_points(user_id, amount):
    points_data = load_user_points()
    current_points = points_data.get(user_id, 0)
    if current_points < amount:
        return False
    points_data[user_id] = current_points - amount
    save_user_points(points_data)
    return True

def transfer_points(sender_id, receiver_id, amount):
    """Transfer points from one user to another"""
    if sender_id == receiver_id:
        return False, "Anda tidak dapat mentransfer point ke diri sendiri!"
    
    if amount <= 0:
        return False, "Jumlah transfer harus lebih dari 0!"
    
    # Check if sender has enough points
    sender_points = get_user_points(sender_id)
    if sender_points < amount:
        return False, f"Point tidak cukup! Anda hanya memiliki {sender_points} point."
    
    # Deduct points from sender
    if not deduct_user_points(sender_id, amount):
        return False, "Gagal mengurangi point pengirim!"
    
    # Add points to receiver
    add_user_points(receiver_id, amount)
    
    return True, f"Berhasil mentransfer {amount} point!"

def is_vip(user_id):
    vip_data = load_user_vip()
    return vip_data.get(user_id, False)

def set_vip(user_id, status=True):
    vip_data = load_user_vip()
    vip_data[user_id] = status
    save_user_vip(vip_data)


def ask_gemini(question: str, context: str = None) -> str:
    """Ask Gemini AI a question with optional context"""
    try:
        if context:
            full_prompt = f"{context}\n\nUser: {question}"
            response = model.generate_content(full_prompt)
        else:
            response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"Maaf, terjadi error saat memproses pertanyaan: {str(e)}"

def ask_gemini_with_personality(question: str, bot_name: str, personality: str, chat_history: list) -> str:
    """Ask Gemini AI with bot personality and chat history"""
    try:
        # Build context from personality and chat history
        context_parts = [
            f"You are {bot_name}. Your personality: {personality}",
            "\nPrevious conversation:"
        ]
        
        # Add last 10 messages from history for context
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        for msg in recent_history:
            role_label = "User" if msg['role'] == 'user' else bot_name
            context_parts.append(f"{role_label}: {msg['content']}")
        
        context_parts.append(f"\nUser: {question}")
        context_parts.append(f"\n{bot_name} (respond in character):")
        
        full_prompt = "\n".join(context_parts)
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Maaf, terjadi error saat memproses pertanyaan: {str(e)}"


@bot.event
async def on_ready():
    print(f'{bot.user} telah online!')
    print(f'Bot ID: {bot.user.id}')
    print('Bot siap digunakan!')
    print(f'[DEBUG] Data directory: {DATA_DIR.absolute()}')
    print(f'[DEBUG] Bot identities file: {BOT_IDENTITIES_FILE.absolute()}')
    print(f'[DEBUG] Chat history directory: {CHAT_HISTORY_DIR.absolute()}')


@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Handle DM messages
    if isinstance(message.channel, discord.DMChannel):
        user_id = str(message.author.id)
        
        # Handle setup command in DM (check this FIRST before checking identity)
        if message.content.startswith('/setup'):
            await handle_setup_dm(message)
            return
        
        # Check if user has set up bot identity
        if user_id not in bot_identities:
            welcome_msg = (
                "👋 Halo! Sebelum kita bisa chat, kamu harus setup identitas bot terlebih dahulu.\n\n"
                "Gunakan perintah berikut:\n"
                "```/setup nama: [Nama Bot]\npersonality: [Deskripsi personality bot]```\n\n"
                "**Contoh:**\n"
                "```/setup nama: Luna\npersonality: Kamu adalah asisten AI yang ramah, ceria, dan suka membantu. Kamu berbicara dengan gaya santai tapi sopan, dan suka menggunakan emoji. Kamu sangat tertarik dengan teknologi dan seni.```"
            )
            await message.channel.send(welcome_msg)
            return
        
        # Handle chat with bot personality
        bot_identity = bot_identities[user_id]
        bot_name = bot_identity['name']
        personality = bot_identity['personality']
        
        # Send typing indicator
        async with message.channel.typing():
            # Get chat history
            chat_history = load_chat_history(user_id)
            
            # Add user message to history
            add_to_chat_history(user_id, 'user', message.content)
            
            # Get response from Gemini with personality
            response = ask_gemini_with_personality(
                message.content,
                bot_name,
                personality,
                chat_history
            )
            
            # Add bot response to history
            add_to_chat_history(user_id, 'bot', response)
            
            # Send response (split if too long)
            if len(response) > 2000:
                chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)
        
        return
    
    # Check if bot is mentioned (in server channels)
    if bot.user.mentioned_in(message):
        # Remove the mention from the message
        content = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        
        if not content:
            await message.channel.send("Halo! Mention saya dan tanyakan sesuatu, atau minta saya mencari gambar dengan format: `cari gambar: [deskripsi]`")
            return
        
        # Regular question for Gemini AI
        async with message.channel.typing():
            answer = ask_gemini(content)
            
            # Split long messages (Discord limit is 2000 characters)
            if len(answer) > 2000:
                chunks = [answer[i:i+2000] for i in range(0, len(answer), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(answer)
    
    # Process commands
    await bot.process_commands(message)


async def handle_setup_dm(message):
    """Handle bot identity setup in DM"""
    user_id = str(message.author.id)
    content = message.content[6:].strip()  # Remove '/setup'
    
    print(f"[DEBUG] Setup request from user {user_id}")
    print(f"[DEBUG] Content: {content[:50]}...")  # Show first 50 chars
    
    try:
        # Parse setup command
        if 'nama:' not in content.lower() or 'personality:' not in content.lower():
            await message.channel.send(
                "❌ Format salah! Gunakan format:\n"
                "```/setup nama: [Nama Bot]\npersonality: [Personality]```"
            )
            return
        
        # Extract name and personality (case-insensitive split)
        content_lower = content.lower()
        personality_pos = content_lower.find('personality:')
        
        if personality_pos == -1:
            await message.channel.send("❌ Keyword 'personality:' tidak ditemukan!")
            return
        
        # Get name part (everything before 'personality:')
        name_part = content[:personality_pos].replace('nama:', '').replace('name:', '', 1).replace('Nama:', '').strip()
        # Get personality part (everything after 'personality:')
        personality_part = content[personality_pos:].split(':', 1)[1].strip()
        
        if not name_part or not personality_part:
            await message.channel.send(
                "❌ Nama dan personality tidak boleh kosong!"
            )
            return
        
        print(f"[DEBUG] Extracted name: {name_part}")
        print(f"[DEBUG] Extracted personality: {personality_part[:50]}...")
        
        # Save bot identity
        bot_identities[user_id] = {
            'name': name_part,
            'personality': personality_part,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"[DEBUG] Saving identity to file...")
        save_bot_identities(bot_identities)
        print(f"[DEBUG] Identity saved! File should exist at: {BOT_IDENTITIES_FILE}")
        
        # Clear old chat history when setting up new identity
        print(f"[DEBUG] Creating chat history...")
        save_chat_history(user_id, [])
        print(f"[DEBUG] Chat history created!")
        
        await message.channel.send(
            f"✅ **Bot identity berhasil di-setup!**\n\n"
            f"🤖 **Nama:** {name_part}\n"
            f"🎭 **Personality:** {personality_part}\n\n"
            f"Sekarang kamu bisa mulai chat denganku! Kirim pesan apa saja untuk memulai percakapan.\n\n"
            f"💡 **Tips:**\n"
            f"• Gunakan `/reset` untuk menghapus riwayat chat\n"
            f"• Gunakan `/identity` untuk melihat identity bot\n"
            f"• Gunakan `/setup` lagi untuk mengubah identity"
        )
        
        print(f"[DEBUG] Setup completed successfully for user {user_id}")
        
    except Exception as e:
        print(f"[ERROR] Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        await message.channel.send(f"❌ Error saat setup: {str(e)}")


@bot.command(name='transfer')
async def transfer_command(ctx, recipient: discord.Member = None, amount: int = None):
    """Transfer points to another user"""
    if recipient is None or amount is None:
        await ctx.send("❌ Format salah! Gunakan: `!transfer @user jumlah`")
        return
    
    sender_id = str(ctx.author.id)
    receiver_id = str(recipient.id)
    
    success, message = transfer_points(sender_id, receiver_id, amount)
    
    if success:
        sender_points = get_user_points(sender_id)
        receiver_points = get_user_points(receiver_id)
        
        embed = discord.Embed(
            title="💸 Transfer Point Berhasil!",
            description=f"{ctx.author.mention} mentransfer **{amount} point** ke {recipient.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="Sisa Point Pengirim", value=f"{sender_points} point", inline=True)
        embed.add_field(name="Point Penerima", value=f"{receiver_points} point", inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ {message}")

@bot.command(name='gacha')
async def gacha_command(ctx):
    """Play gacha game to earn points"""
    user_id = str(ctx.author.id)
    cost = 50  # Cost to play
    
    # Check if user has enough points
    user_points = get_user_points(user_id)
    if user_points < cost:
        await ctx.send(f"❌ Point tidak cukup! Kamu butuh {cost} point untuk bermain gacha. Kamu hanya memiliki {user_points} point.")
        return
    
    # Deduct points
    deduct_user_points(user_id, cost)
    
    # Determine rewards
    import random
    
    # Define gacha tiers and rewards
    tiers = {
        "SSR": {"chance": 5, "min_reward": 200, "max_reward": 500},
        "SR": {"chance": 15, "min_reward": 100, "max_reward": 200},
        "R": {"chance": 30, "min_reward": 50, "max_reward": 100},
        "N": {"chance": 50, "min_reward": 10, "max_reward": 50}
    }
    
    # Roll for tier
    roll = random.randint(1, 100)
    cumulative_chance = 0
    selected_tier = "N"  # Default
    
    for tier, data in tiers.items():
        cumulative_chance += data["chance"]
        if roll <= cumulative_chance:
            selected_tier = tier
            break
    
    # Determine reward amount
    tier_data = tiers[selected_tier]
    reward = random.randint(tier_data["min_reward"], tier_data["max_reward"])
    
    # Add reward
    add_user_points(user_id, reward)
    
    # Prepare response
    tier_emojis = {
        "SSR": "🌟",
        "SR": "✨",
        "R": "⭐",
        "N": "⚪"
    }
    
    embed = discord.Embed(
        title=f"{tier_emojis[selected_tier]} Gacha Result: {selected_tier} Tier!",
        description=f"Kamu mendapatkan **{reward} point**!",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="Biaya", value=f"{cost} point", inline=True)
    embed.add_field(name="Hadiah", value=f"{reward} point", inline=True)
    embed.add_field(name="Keuntungan", value=f"{reward - cost} point", inline=True)
    
    new_balance = get_user_points(user_id)
    embed.set_footer(text=f"Saldo point: {new_balance}")
    
    await ctx.send(embed=embed)

@bot.command(name='charagacha')
async def character_gacha(ctx):
    """Gacha karakter anime"""
    user_id = str(ctx.author.id)
    cost = 100  # Cost to play character gacha

    # Check if user has enough points
    user_points = get_user_points(user_id)
    if user_points < cost:
        await ctx.send(f"❌ Point tidak cukup! Kamu butuh {cost} point untuk gacha karakter. Kamu hanya memiliki {user_points} point.")
        return

    # Deduct points
    deduct_user_points(user_id, cost)

    # Determine rarity
    import random
    roll = random.randint(1, 100)
    cumulative_chance = 0
    selected_rarity = "N"  # Default

    for rarity, data in CHARACTER_GACHA.items():
        cumulative_chance += data["chance"]
        if roll <= cumulative_chance:
            selected_rarity = rarity
            break

    # Get random character from selected rarity
    characters = CHARACTER_GACHA[selected_rarity]["characters"]
    character = random.choice(characters)

    # Add character to user's inventory
    add_character_to_inventory(user_id, character, selected_rarity)

    # Prepare response
    rarity_colors = {
        "SSR": discord.Color.gold(),
        "SR": discord.Color.purple(),
        "R": discord.Color.blue(),
        "N": discord.Color.green()
    }

    rarity_emojis = {
        "SSR": "🌟",
        "SR": "✨",
        "R": "⭐",
        "N": "⚪"
    }

    embed = discord.Embed(
        title=f"{rarity_emojis[selected_rarity]} Gacha Result: {selected_rarity} Tier!",
        description=f"Kamu mendapat **{character['name']}** dari {character['anime']}!",
        color=rarity_colors[selected_rarity]
    )

    embed.set_image(url=character['image'])
    embed.add_field(name="Biaya", value=f"{cost} point", inline=True)
    embed.add_field(name="Rarity", value=f"{selected_rarity} Tier", inline=True)
    
    new_balance = get_user_points(user_id)
    embed.set_footer(text=f"Karakter telah ditambahkan ke inventory. Sisa point: {new_balance}")

    await ctx.send(embed=embed)

@bot.command(name='inventory')
async def inventory_command(ctx):
    """Tampilkan inventory karakter"""
    user_id = str(ctx.author.id)
    user_characters = get_user_characters(user_id)

    if not user_characters:
        await ctx.send("🎒 Inventory kamu kosong! Mainkan `!charagacha` untuk mendapatkan karakter.")
        return

    # Convert dictionary to list for sorting
    character_list = list(user_characters.values())

    # Sort characters by rarity
    rarity_order = {"SSR": 0, "SR": 1, "R": 2, "N": 3}
    sorted_characters = sorted(character_list, key=lambda x: rarity_order[x['tier']])

    # Pagination
    items_per_page = 5
    pages = [sorted_characters[i:i + items_per_page] for i in range(0, len(sorted_characters), items_per_page)]
    total_pages = len(pages)

    current_page = 0

    def create_embed(page_num):
        embed = discord.Embed(
            title=f"🎒 Inventory Karakter - {ctx.author.name}",
            description=f"Halaman {page_num + 1}/{total_pages}",
            color=discord.Color.blue()
        )

        for char in pages[page_num]:
            embed.add_field(
                name=f"{char['name']} ({char['tier']}) x{char['count']}",
                value=f"Anime: {char['anime']}",
                inline=False
            )
        
        embed.set_footer(text="Gunakan reaksi untuk navigasi halaman.")
        return embed

    message = await ctx.send(embed=create_embed(current_page))

    if total_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                    current_page += 1
                    await message.edit(embed=create_embed(current_page))
                elif str(reaction.emoji) == "⬅️" and current_page > 0:
                    current_page -= 1
                    await message.edit(embed=create_embed(current_page))

                await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

@bot.command(name='sellchar')
async def sell_character(ctx):
    """Jual karakter dari inventory dengan harga berdasarkan tier"""
    user_id = str(ctx.author.id)
    user_characters = get_user_characters(user_id)
    
    if not user_characters:
        await ctx.send("🎒 Inventory kamu kosong! Mainkan `!charagacha` untuk mendapatkan karakter.")
        return
    
    # Harga berdasarkan tier
    tier_prices = {
        "SSR": 500,
        "SR": 300,
        "R": 150,
        "N": 50
    }
    
    # Convert dictionary to list for sorting
    character_list = list(user_characters.values())
    
    # Sort characters by rarity
    rarity_order = {"SSR": 0, "SR": 1, "R": 2, "N": 3}
    sorted_characters = sorted(character_list, key=lambda x: rarity_order[x['tier']])
    
    # Create selection embed
    embed = discord.Embed(
        title=f"💰 Jual Karakter - {ctx.author.name}",
        description="Pilih karakter yang ingin dijual dengan memasukkan nomor karakter.",
        color=discord.Color.gold()
    )
    
    for idx, char in enumerate(sorted_characters, 1):
        price = tier_prices.get(char['tier'], 0)
        embed.add_field(
            name=f"{idx}. {char['name']} ({char['tier']}) x{char['count']}",
            value=f"Anime: {char['anime']}\nHarga: {price} point per karakter",
            inline=False
        )
    
    embed.set_footer(text="Masukkan nomor karakter untuk menjual.")
    await ctx.send(embed=embed)
    
    # Wait for user selection
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        selection = int(msg.content)
        
        if 1 <= selection <= len(sorted_characters):
            selected_char = sorted_characters[selection-1]
            char_name = selected_char['name']
            char_tier = selected_char['tier']
            char_count = selected_char['count']
            price = tier_prices.get(char_tier, 0)
            
            # Ask for quantity to sell
            quantity_embed = discord.Embed(
                title="📊 Masukkan Jumlah",
                description=f"Kamu memiliki **{char_count}** karakter **{char_name}** ({char_tier}).\n"
                           f"Berapa banyak yang ingin kamu jual?\n"
                           f"Harga per karakter: **{price} point**",
                color=discord.Color.blue()
            )
            quantity_embed.set_footer(text=f"Masukkan jumlah (1-{char_count}) atau '0' untuk batal.")
            await ctx.send(embed=quantity_embed)
            
            # Wait for quantity input
            def quantity_check(m):
                if m.author == ctx.author and m.channel == ctx.channel:
                    if m.content.isdigit():
                        qty = int(m.content)
                        return 0 <= qty <= char_count
                return False
            
            try:
                qty_msg = await bot.wait_for('message', check=quantity_check, timeout=60.0)
                quantity = int(qty_msg.content)
                
                if quantity == 0:
                    await ctx.send("❌ Penjualan dibatalkan.")
                    return
                
                total_price = price * quantity
                
                # Create confirmation embed
                confirm_embed = discord.Embed(
                    title="🛒 Konfirmasi Jual",
                    description=f"Apakah kamu yakin ingin menjual **{quantity}** karakter **{char_name}**?",
                    color=discord.Color.orange()
                )
                confirm_embed.add_field(name="Tier", value=char_tier, inline=True)
                confirm_embed.add_field(name="Jumlah", value=f"{quantity}", inline=True)
                confirm_embed.add_field(name="Total Harga", value=f"{total_price} point", inline=True)
                confirm_embed.add_field(name="Sisa Karakter", value=f"{char_count - quantity}", inline=True)
                confirm_embed.add_field(name="Anime", value=selected_char['anime'], inline=False)
                confirm_embed.set_footer(text="Balas dengan 'ya' untuk konfirmasi atau 'tidak' untuk batal.")
                
                await ctx.send(embed=confirm_embed)
                
                # Wait for confirmation
                def confirm_check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['ya', 'tidak', 'yes', 'no', 'y', 'n']
                
                try:
                    confirm_msg = await bot.wait_for('message', check=confirm_check, timeout=30.0)
                    if confirm_msg.content.lower() in ['ya', 'yes', 'y']:
                        # Process sale
                        # Load the entire characters data structure first to ensure consistency
                        all_characters = load_user_characters()
                        
                        # Check if user exists and has the character with sufficient quantity
                        if (user_id in all_characters and 
                            char_name in all_characters[user_id] and 
                            all_characters[user_id][char_name]['count'] >= quantity):
                            
                            # Reduce count for the specific character
                            all_characters[user_id][char_name]['count'] -= quantity
                            
                            # Get the new count for display and decision making
                            new_count = all_characters[user_id][char_name]['count']
                            
                            # Remove character if count reaches 0
                            if new_count <= 0:
                                del all_characters[user_id][char_name]
                                remaining_text = "Karakter dihapus dari inventory"
                            else:
                                remaining_text = f"{new_count}"
                            
                            # Save the entire inventory
                            save_user_characters(all_characters)
                            
                            # Add points to user
                            add_user_points(user_id, total_price)
                            
                            # Get updated points
                            new_points = get_user_points(user_id)
                            
                            # Create success embed
                            success_embed = discord.Embed(
                                title="✅ Penjualan Berhasil!",
                                description=f"Kamu telah menjual **{quantity}** karakter **{char_name}** dan mendapatkan **{total_price} point**!",
                                color=discord.Color.green()
                            )
                            success_embed.add_field(name="Sisa Karakter", value=remaining_text, inline=True)
                            success_embed.set_footer(text=f"Total point: {new_points}")
                            
                            await ctx.send(embed=success_embed)
                        else:
                            await ctx.send("❌ Karakter tidak ditemukan di inventory atau jumlah tidak mencukupi!")
                    else:
                        await ctx.send("❌ Penjualan dibatalkan.")
                except asyncio.TimeoutError:
                    await ctx.send("⏰ Waktu habis! Penjualan dibatalkan.")
            except asyncio.TimeoutError:
                await ctx.send("⏰ Waktu habis! Silakan coba lagi.")
        else:
            await ctx.send("❌ Nomor karakter tidak valid!")
    except asyncio.TimeoutError:
        await ctx.send("⏰ Waktu habis! Silakan coba lagi.")

@bot.command(name='duel')
async def duel_command(ctx, opponent: discord.Member = None, bet: int = None):
    """Duel another user using characters from inventory"""
    if opponent is None or bet is None:
        await ctx.send("❌ Format salah! Gunakan: `!duel @user jumlah_taruhan`")
        return
    
    if opponent.id == ctx.author.id:
        await ctx.send("❌ Kamu tidak bisa berduel dengan dirimu sendiri!")
        return
    
    if bet <= 0:
        await ctx.send("❌ Jumlah taruhan harus lebih dari 0!")
        return
    
    challenger_id = str(ctx.author.id)
    opponent_id = str(opponent.id)
    
    # Check if both users have enough points
    challenger_points = get_user_points(challenger_id)
    opponent_points = get_user_points(opponent_id)
    
    if challenger_points < bet:
        await ctx.send(f"❌ Point tidak cukup! Kamu hanya memiliki {challenger_points} point.")
        return
    
    if opponent_points < bet:
        await ctx.send(f"❌ {opponent.display_name} tidak memiliki cukup point! Mereka hanya memiliki {opponent_points} point.")
        return
    
    # Check if both users have characters in inventory
    challenger_chars = get_user_characters(challenger_id)
    opponent_chars = get_user_characters(opponent_id)
    
    if not challenger_chars:
        await ctx.send(f"❌ Kamu tidak memiliki karakter di inventaris! Gunakan `!charagacha` untuk mendapatkan karakter.")
        return
    
    if not opponent_chars:
        await ctx.send(f"❌ {opponent.display_name} tidak memiliki karakter di inventaris!")
        return
    
    # Create duel request embed
    embed = discord.Embed(
        title="⚔️ Tantangan Duel!",
        description=f"{ctx.author.mention} menantang {opponent.mention} untuk berduel karakter dengan taruhan **{bet} point**!",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Opponent, ketik 'accept' untuk menerima atau 'decline' untuk menolak dalam 30 detik.")
    
    duel_msg = await ctx.send(embed=embed)
    
    # Wait for opponent's response
    def check(m):
        return m.author.id == opponent.id and m.channel == ctx.channel and m.content.lower() in ['accept', 'decline']
    
    try:
        import asyncio
        response = await bot.wait_for('message', check=check, timeout=30.0)
        
        if response.content.lower() == 'decline':
            await ctx.send(f"🛑 {opponent.display_name} menolak tantangan duel!")
            return
        
        # Duel accepted, now select characters
        await ctx.send(f"⚔️ Duel diterima! Silakan pilih karakter kalian masing-masing.")
        
        # Function to get character selection from user
        async def select_character(user, user_chars, user_name):
            # Create character selection embed
            char_embed = discord.Embed(
                title=f"🎯 {user_name}, pilih karaktermu!",
                description="Balas dengan nomor karakter yang ingin digunakan:",
                color=discord.Color.blue()
            )
            
            # List characters with their tiers
            for i, (char_name, char_data) in enumerate(user_chars.items(), 1):
                char_embed.add_field(
                    name=f"{i}. {char_name}",
                    value=f"**Tier:** {char_data['tier']}\n**Jumlah:** {char_data['count']}",
                    inline=False
                )
            
            await ctx.send(embed=char_embed)
            
            def char_check(m):
                try:
                    selection = int(m.content)
                    return (m.author.id == user.id and 
                           m.channel == ctx.channel and 
                           1 <= selection <= len(user_chars))
                except ValueError:
                    return False
            
            try:
                char_response = await bot.wait_for('message', check=char_check, timeout=60.0)
                selection = int(char_response.content)
                selected_char_name = list(user_chars.keys())[selection - 1]
                return selected_char_name
            except asyncio.TimeoutError:
                return None
        
        # Get character selections
        challenger_char_name = await select_character(ctx.author, challenger_chars, ctx.author.display_name)
        if challenger_char_name is None:
            await ctx.send("⏰ Waktu habis untuk memilih karakter!")
            return
        
        opponent_char_name = await select_character(opponent, opponent_chars, opponent.display_name)
        if opponent_char_name is None:
            await ctx.send("⏰ Waktu habis untuk lawan memilih karakter!")
            return
        
        # Get character data
        challenger_char = challenger_chars[challenger_char_name]
        opponent_char = opponent_chars[opponent_char_name]
        
        # Battle simulation with tier-based logic
        await ctx.send(f"⚔️ Duel dimulai! {ctx.author.display_name} menggunakan **{challenger_char_name}** vs {opponent.display_name} menggunakan **{opponent_char_name}**!")
        await asyncio.sleep(2)
        
        # Define tier hierarchy (higher is better)
        tier_hierarchy = {
            'SSR': 5,
            'SR': 4,
            'R': 3,
            'N': 2
        }
        
        challenger_tier_level = tier_hierarchy.get(challenger_char['tier'], 1)
        opponent_tier_level = tier_hierarchy.get(opponent_char['tier'], 1)
        
        # Determine winner based on tier
        if challenger_tier_level > opponent_tier_level:
            winner = ctx.author
            winner_id = challenger_id
            loser = opponent
            loser_id = opponent_id
            win_reason = f"**{challenger_char_name}** (Tier {challenger_char['tier']}) mengalahkan **{opponent_char_name}** (Tier {opponent_char['tier']})!"
        elif opponent_tier_level > challenger_tier_level:
            winner = opponent
            winner_id = opponent_id
            loser = ctx.author
            loser_id = challenger_id
            win_reason = f"**{opponent_char_name}** (Tier {opponent_char['tier']}) mengalahkan **{challenger_char_name}** (Tier {challenger_char['tier']})!"
        else:
            # Same tier - random outcome (50/50 chance)
            if random.random() < 0.5:
                winner = ctx.author
                winner_id = challenger_id
                loser = opponent
                loser_id = opponent_id
                win_reason = f"Pertarungan sengit! **{challenger_char_name}** menang secara dramatis melawan **{opponent_char_name}** (Tier {challenger_char['tier']})!"
            else:
                winner = opponent
                winner_id = opponent_id
                loser = ctx.author
                loser_id = challenger_id
                win_reason = f"Pertarungan sengit! **{opponent_char_name}** menang secara dramatis melawan **{challenger_char_name}** (Tier {opponent_char['tier']})!"
        
        # Transfer points
        deduct_user_points(loser_id, bet)
        add_user_points(winner_id, bet)
        
        # Announce winner
        result_embed = discord.Embed(
            title="🏆 Hasil Duel Karakter!",
            description=win_reason,
            color=discord.Color.gold()
        )
        
        result_embed.add_field(
            name=f"{ctx.author.display_name}",
            value=f"Karakter: **{challenger_char_name}** (Tier {challenger_char['tier']})",
            inline=True
        )
        
        result_embed.add_field(
            name=f"{opponent.display_name}",
            value=f"Karakter: **{opponent_char_name}** (Tier {opponent_char['tier']})",
            inline=True
        )
        
        result_embed.add_field(
            name="💰 Hadiah",
            value=f"{winner.mention} memenangkan **{bet} point**!",
            inline=False
        )
        
        winner_points = get_user_points(winner_id)
        loser_points = get_user_points(loser_id)
        
        result_embed.set_footer(text=f"Points: {winner.display_name} ({winner_points}) | {loser.display_name} ({loser_points})")
        
        await ctx.send(embed=result_embed)
        
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Waktu habis! {opponent.display_name} tidak merespon tantangan.")

@bot.command(name='help')
async def help_command(ctx):
    """Show help message"""
    embed = discord.Embed(
        title="🤖 Bot Discord AI dengan Gemini",
        description="Bot ini menggunakan Gemini AI untuk menjawab pertanyaan dan mencari gambar!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📝 Cara Menggunakan",
        value=f"Mention bot {bot.user.mention} diikuti dengan pertanyaan atau perintah Anda",
        inline=False
    )
    
    embed.add_field(
        name="💬 Bertanya",
        value=f"{bot.user.mention} Apa itu Python?",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Game & Points",
        value="`!daily` - Claim daily reward\n`!game` - Play mini games\n`!points` - Check your points\n`!leaderboard` - View top players\n`!gacha` - Main gacha (50 point)\n`!charagacha` - Gacha karakter anime (100 point)\n`!inventory` - Lihat koleksi karakter\n`!sellchar` - Jual karakter dari inventory\n`!duel @user jumlah` - Tantang user lain dengan karakter\n`!transfer @user jumlah` - Transfer point",
        inline=False
    )
    
    embed.add_field(
        name="👑 VIP Features",
        value="`!shop` - Buy VIP status\n`!vip` - Check VIP status\n`!sticker` - Create sticker (VIP)\n`!emoji` - Create emoji (VIP)\n`!soundboard` - Add soundboard (VIP)",
        inline=False
    )
    
    embed.set_footer(text="Bot ini menggunakan Gemini AI dan Google Custom Search")
    
    await ctx.send(embed=embed)


@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')


@bot.command(name='reset')
async def reset_chat(ctx):
    """Reset chat history (DM only)"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("❌ Command ini hanya bisa digunakan di DM!")
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in bot_identities:
        await ctx.send("❌ Kamu belum setup bot identity. Gunakan `/setup` terlebih dahulu.")
        return
    
    save_chat_history(user_id, [])
    await ctx.send("✅ Riwayat chat berhasil dihapus! Percakapan dimulai dari awal.")


@bot.command(name='identity')
async def show_identity(ctx):
    """Show bot identity (DM only)"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("❌ Command ini hanya bisa digunakan di DM!")
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in bot_identities:
        await ctx.send("❌ Kamu belum setup bot identity. Gunakan `/setup` terlebih dahulu.")
        return
    
    identity = bot_identities[user_id]
    chat_history = load_chat_history(user_id)
    
    embed = discord.Embed(
        title="🤖 Bot Identity",
        color=discord.Color.purple()
    )
    embed.add_field(name="📝 Nama", value=identity['name'], inline=False)
    embed.add_field(name="🎭 Personality", value=identity['personality'], inline=False)
    embed.add_field(name="💬 Jumlah Pesan", value=f"{len(chat_history)} pesan", inline=True)
    embed.add_field(name="📅 Dibuat", value=identity['created_at'][:10], inline=True)
    embed.set_footer(text="Gunakan /setup untuk mengubah identity")
    
    await ctx.send(embed=embed)


@bot.command(name='dmhelp')
async def dm_help(ctx):
    """Show DM features help"""
    embed = discord.Embed(
        title="💬 Fitur DM Chat",
        description="Bot ini bisa chat dengan kamu lewat DM dengan personality yang bisa kamu atur!",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="🔧 Setup Bot Identity",
        value=(
            "Sebelum chat, setup identity bot terlebih dahulu:\n"
            "```/setup nama: [Nama]\npersonality: [Personality]```\n"
            "Contoh:\n"
            "```/setup nama: Luna\npersonality: Asisten ramah yang suka teknologi```"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💬 Chat dengan Bot",
        value="Setelah setup, kirim pesan apa saja untuk chat!",
        inline=False
    )
    
    embed.add_field(
        name="🔄 Reset Chat History",
        value="`/reset` - Hapus riwayat percakapan",
        inline=True
    )
    
    embed.add_field(
        name="🔍 Lihat Identity",
        value="`/identity` - Lihat identity bot kamu",
        inline=True
    )
    
    embed.set_footer(text="Setiap user punya bot identity dan memory sendiri!")
    
    await ctx.send(embed=embed)


# Game commands
@bot.command(name='daily')
async def daily_reward(ctx):
    """Claim daily reward"""
    user_id = str(ctx.author.id)
    today = datetime.now().strftime('%Y-%m-%d')
    
    claims = load_daily_claims()
    last_claim = claims.get(user_id)
    
    if last_claim == today:
        await ctx.send(f"❌ Kamu sudah mengambil daily reward hari ini! Kembali lagi besok.")
        return
    
    # Give reward
    new_points = add_user_points(user_id, DAILY_REWARD)
    claims[user_id] = today
    save_daily_claims(claims)
    
    embed = discord.Embed(
        title="🎁 Daily Reward!",
        description=f"Kamu mendapat **{DAILY_REWARD} points**!",
        color=discord.Color.gold()
    )
    embed.add_field(name="💰 Total Points", value=f"{new_points} points")
    embed.set_footer(text="Kembali lagi besok untuk claim lagi!")
    
    await ctx.send(embed=embed)


@bot.command(name='game')
async def play_game(ctx):
    """Play mini games to earn points"""
    import random
    
    # Simple number guessing game
    number = random.randint(1, 10)
    
    embed = discord.Embed(
        title="🎮 Tebak Angka!",
        description="Aku udah pilih angka antara 1-10. Tebak angkanya!",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Ketik angka 1-10 dalam 15 detik!")
    
    await ctx.send(embed=embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        guess = int(msg.content)
        
        if guess == number:
            reward = GAME_REWARD_MAX
            new_points = add_user_points(str(ctx.author.id), reward)
            
            embed = discord.Embed(
                title="🎉 BENAR!",
                description=f"Angka yang benar adalah **{number}**!",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 Reward", value=f"+{reward} points")
            embed.add_field(name="📊 Total Points", value=f"{new_points} points")
            await ctx.send(embed=embed)
        else:
            reward = GAME_REWARD_MIN
            new_points = add_user_points(str(ctx.author.id), reward)
            
            embed = discord.Embed(
                title="❌ Salah!",
                description=f"Angka yang benar adalah **{number}**, tapi kamu dapat participation reward!",
                color=discord.Color.red()
            )
            embed.add_field(name="💰 Reward", value=f"+{reward} points")
            embed.add_field(name="📊 Total Points", value=f"{new_points} points")
            await ctx.send(embed=embed)
            
    except Exception:
        await ctx.send("⏰ Waktu habis! Coba lagi dengan `!game`")


@bot.command(name='points')
async def check_points(ctx):
    """Check your points"""
    user_id = str(ctx.author.id)
    points = get_user_points(user_id)
    vip_status = is_vip(user_id)
    
    embed = discord.Embed(
        title=f"💰 Points - {ctx.author.name}",
        color=discord.Color.gold()
    )
    embed.add_field(name="💎 Points", value=f"{points} points", inline=False)
    embed.add_field(name="👑 VIP Status", value="✅ VIP" if vip_status else "❌ Non-VIP", inline=False)
    
    if not vip_status:
        embed.add_field(
            name="🛒 Want VIP?",
            value=f"Beli VIP dengan `!shop` (Harga: {VIP_PRICE} points)",
            inline=False
        )
    
    await ctx.send(embed=embed)


@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """Show top players"""
    points_data = load_user_points()
    
    if not points_data:
        await ctx.send("📊 Leaderboard masih kosong!")
        return
    
    # Sort by points
    sorted_users = sorted(points_data.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(
        title="🏆 Leaderboard Top 10",
        color=discord.Color.purple()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    for idx, (user_id, points) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(int(user_id))
            medal = medals[idx-1] if idx <= 3 else f"#{idx}"
            vip_badge = " 👑" if is_vip(user_id) else ""
            embed.add_field(
                name=f"{medal} {user.name}{vip_badge}",
                value=f"💰 {points} points",
                inline=False
            )
        except:
            continue
    
    await ctx.send(embed=embed)


@bot.command(name='shop')
async def shop(ctx):
    """Show shop and buy VIP"""
    user_id = str(ctx.author.id)
    points = get_user_points(user_id)
    vip_status = is_vip(user_id)
    
    embed = discord.Embed(
        title="🛒 Shop",
        description="Beli VIP untuk unlock fitur eksklusif!",
        color=discord.Color.blue()
    )
    
    if vip_status:
        embed.add_field(
            name="👑 Status VIP",
            value="✅ Kamu sudah VIP!",
            inline=False
        )
    else:
        embed.add_field(
            name="👑 VIP Package",
            value=f"**Harga: {VIP_PRICE} points**\n\n**Fitur VIP:**\n🎨 Buat custom stickers\n😀 Buat custom emojis\n🔊 Upload soundboards\n\nPoints kamu: {points}",
            inline=False
        )
        
        if points >= VIP_PRICE:
            embed.add_field(
                name="💳 Cara Beli",
                value="Ketik `!buyvip` untuk membeli VIP!",
                inline=False
            )
        else:
            needed = VIP_PRICE - points
            embed.add_field(
                name="❌ Points Tidak Cukup",
                value=f"Kamu butuh {needed} points lagi!",
                inline=False
            )
    
    await ctx.send(embed=embed)


@bot.command(name='buyvip')
async def buy_vip(ctx):
    """Purchase VIP status"""
    user_id = str(ctx.author.id)
    points = get_user_points(user_id)
    
    if is_vip(user_id):
        await ctx.send("❌ Kamu sudah VIP!")
        return
    
    if points < VIP_PRICE:
        needed = VIP_PRICE - points
        await ctx.send(f"❌ Points tidak cukup! Kamu butuh {needed} points lagi.")
        return
    
    # Deduct points and grant VIP
    points_data = load_user_points()
    points_data[user_id] = points - VIP_PRICE
    save_user_points(points_data)
    set_vip(user_id, True)
    
    embed = discord.Embed(
        title="🎉 VIP Berhasil Dibeli!",
        description="Selamat! Kamu sekarang VIP member!",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="✨ Fitur Unlocked",
        value="🎨 `!sticker` - Buat sticker\n😀 `!emoji` - Buat emoji\n🔊 `!soundboard` - Upload soundboard",
        inline=False
    )
    embed.add_field(
        name="💰 Sisa Points",
        value=f"{points_data[user_id]} points",
        inline=False
    )
    
    await ctx.send(embed=embed)


@bot.command(name='vip')
async def vip_status(ctx):
    """Check VIP status"""
    user_id = str(ctx.author.id)
    vip_status = is_vip(user_id)
    
    if vip_status:
        embed = discord.Embed(
            title="👑 VIP Member",
            description="Kamu adalah VIP member!",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="✨ Fitur VIP Aktif",
            value="🎨 Create custom stickers\n😀 Create custom emojis\n🔊 Upload soundboards",
            inline=False
        )
    else:
        embed = discord.Embed(
            title="❌ Bukan VIP",
            description="Kamu belum VIP member.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="🛒 Ingin VIP?",
            value=f"Gunakan `!shop` untuk beli VIP ({VIP_PRICE} points)",
            inline=False
        )
    
    await ctx.send(embed=embed)


# VIP-only features: Sticker, Emoji, Soundboard
@bot.command(name='sticker')
async def create_sticker(ctx):
    """Create custom sticker (VIP only)"""
    user_id = str(ctx.author.id)
    
    if not is_vip(user_id):
        await ctx.send("❌ Fitur ini hanya untuk VIP members! Gunakan `!shop` untuk beli VIP.")
        return
    
    # Check if user has admin permissions
    if not ctx.author.guild_permissions.manage_emojis:
        await ctx.send("❌ Kamu butuh permission 'Manage Emojis and Stickers' untuk membuat sticker!")
        return
    
    embed = discord.Embed(
        title="🎨 Buat Sticker",
        description="Upload gambar untuk dijadikan sticker!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📋 Cara Menggunakan",
        value="1. Upload gambar (PNG/JPG)\n2. Berikan nama sticker\n3. Bot akan membuat sticker untuk server ini",
        inline=False
    )
    embed.set_footer(text="Upload gambar dalam 30 detik...")
    
    await ctx.send(embed=embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and len(m.attachments) > 0
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        attachment = msg.attachments[0]
        
        # Check file type
        if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            await ctx.send("❌ File harus berupa gambar (PNG/JPG/GIF)!")
            return
        
        # Ask for sticker name
        await ctx.send("📝 Berikan nama untuk sticker ini:")
        
        def name_check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        name_msg = await bot.wait_for('message', check=name_check, timeout=15.0)
        sticker_name = name_msg.content.strip()[:32]  # Discord limit
        
        # Download image
        image_data = await attachment.read()
        
        # Create sticker
        sticker = await ctx.guild.create_sticker(
            name=sticker_name,
            description=f"Created by {ctx.author.name}",
            emoji="🎨",
            file=discord.File(io.BytesIO(image_data), filename=attachment.filename)
        )
        
        success_embed = discord.Embed(
            title="✅ Sticker Berhasil Dibuat!",
            description=f"Sticker **{sticker_name}** telah ditambahkan ke server!",
            color=discord.Color.green()
        )
        success_embed.set_thumbnail(url=sticker.url)
        await ctx.send(embed=success_embed)
        
    except discord.Forbidden:
        await ctx.send("❌ Bot tidak memiliki permission untuk membuat sticker!")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Error saat membuat sticker: {str(e)}")
    except Exception as e:
        await ctx.send(f"⏰ Waktu habis atau terjadi error: {str(e)}")


@bot.command(name='emoji')
async def create_emoji(ctx):
    """Create custom emoji (VIP only)"""
    user_id = str(ctx.author.id)
    
    if not is_vip(user_id):
        await ctx.send("❌ Fitur ini hanya untuk VIP members! Gunakan `!shop` untuk beli VIP.")
        return
    
    # Check if user has admin permissions
    if not ctx.author.guild_permissions.manage_emojis:
        await ctx.send("❌ Kamu butuh permission 'Manage Emojis and Stickers' untuk membuat emoji!")
        return
    
    embed = discord.Embed(
        title="😀 Buat Emoji",
        description="Upload gambar untuk dijadikan emoji!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📋 Cara Menggunakan",
        value="1. Upload gambar (PNG/JPG, max 256KB)\n2. Berikan nama emoji\n3. Bot akan membuat emoji untuk server ini",
        inline=False
    )
    embed.set_footer(text="Upload gambar dalam 30 detik...")
    
    await ctx.send(embed=embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and len(m.attachments) > 0
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        attachment = msg.attachments[0]
        
        # Check file type
        if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            await ctx.send("❌ File harus berupa gambar (PNG/JPG/GIF)!")
            return
        
        # Check file size (Discord limit: 256KB for emoji)
        if attachment.size > 256000:
            await ctx.send("❌ Ukuran file terlalu besar! Max 256KB untuk emoji.")
            return
        
        # Ask for emoji name
        await ctx.send("📝 Berikan nama untuk emoji ini (huruf dan angka saja):")
        
        def name_check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        name_msg = await bot.wait_for('message', check=name_check, timeout=15.0)
        emoji_name = ''.join(c for c in name_msg.content if c.isalnum())[:32]  # Discord limit
        
        if not emoji_name:
            await ctx.send("❌ Nama emoji tidak valid!")
            return
        
        # Download image
        image_data = await attachment.read()
        
        # Create emoji
        emoji = await ctx.guild.create_custom_emoji(
            name=emoji_name,
            image=image_data
        )
        
        success_embed = discord.Embed(
            title="✅ Emoji Berhasil Dibuat!",
            description=f"Emoji **:{emoji_name}:** telah ditambahkan ke server!",
            color=discord.Color.green()
        )
        success_embed.add_field(name="🚀 Cara Pakai", value=f"Ketik `:{emoji_name}:` atau gunakan {emoji}")
        await ctx.send(embed=success_embed)
        
    except discord.Forbidden:
        await ctx.send("❌ Bot tidak memiliki permission untuk membuat emoji!")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Error saat membuat emoji: {str(e)}")
    except Exception as e:
        await ctx.send(f"⏰ Waktu habis atau terjadi error: {str(e)}")


@bot.command(name='soundboard')
async def add_soundboard(ctx):
    """Add soundboard (VIP only)"""
    user_id = str(ctx.author.id)
    
    if not is_vip(user_id):
        await ctx.send("❌ Fitur ini hanya untuk VIP members! Gunakan `!shop` untuk beli VIP.")
        return
    
    embed = discord.Embed(
        title="🔊 Upload Soundboard",
        description="Upload file audio untuk dijadikan soundboard!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📋 Cara Menggunakan",
        value="1. Upload file audio (MP3/WAV/OGG, max 5MB)\n2. File akan disimpan di server\n3. Gunakan `!play [nama]` untuk memutar",
        inline=False
    )
    embed.set_footer(text="Upload audio dalam 30 detik...")
    
    await ctx.send(embed=embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and len(m.attachments) > 0
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        attachment = msg.attachments[0]
        
        # Check file type
        if not attachment.filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            await ctx.send("❌ File harus berupa audio (MP3/WAV/OGG/M4A)!")
            return
        
        # Check file size (max 5MB)
        if attachment.size > 5000000:
            await ctx.send("❌ Ukuran file terlalu besar! Max 5MB.")
            return
        
        # Save audio file
        safe_filename = ''.join(c for c in attachment.filename if c.isalnum() or c in '._-')
        file_path = SOUNDBOARDS_DIR / f"{ctx.author.id}_{safe_filename}"
        
        await attachment.save(file_path)
        
        success_embed = discord.Embed(
            title="✅ Soundboard Berhasil Ditambahkan!",
            description=f"Audio **{attachment.filename}** telah disimpan!",
            color=discord.Color.green()
        )
        success_embed.add_field(
            name="💾 File Info",
            value=f"Nama: {attachment.filename}\nUkuran: {attachment.size / 1000:.1f} KB",
            inline=False
        )
        success_embed.set_footer(text="Gunakan !listsounds untuk melihat semua soundboard")
        await ctx.send(embed=success_embed)
        
    except Exception as e:
        await ctx.send(f"⏰ Waktu habis atau terjadi error: {str(e)}")


@bot.command(name='listsounds')
async def list_soundboards(ctx):
    """List all available soundboards"""
    sounds = list(SOUNDBOARDS_DIR.glob('*'))
    
    if not sounds:
        await ctx.send("💭 Belum ada soundboard yang tersimpan. VIP members bisa upload dengan `!soundboard`")
        return
    
    embed = discord.Embed(
        title="🔊 Soundboard List",
        description=f"Total: {len(sounds)} sounds",
        color=discord.Color.blue()
    )
    
    for sound in sounds[:25]:  # Limit to 25 to avoid embed limits
        filename = sound.name
        size_kb = sound.stat().st_size / 1000
        embed.add_field(
            name=filename,
            value=f"Size: {size_kb:.1f} KB",
            inline=True
        )
    
    embed.set_footer(text="Soundboards uploaded by VIP members")
    await ctx.send(embed=embed)


if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN tidak ditemukan di file .env")
    else:
        bot.run(TOKEN)
