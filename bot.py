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

# Data storage paths
DATA_DIR = Path('user_data')
DATA_DIR.mkdir(exist_ok=True)
BOT_IDENTITIES_FILE = DATA_DIR / 'bot_identities.json'
CHAT_HISTORY_DIR = DATA_DIR / 'chat_history'
CHAT_HISTORY_DIR.mkdir(exist_ok=True)
USER_POINTS_FILE = DATA_DIR / 'user_points.json'
USER_VIP_FILE = DATA_DIR / 'user_vip.json'
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

def get_user_points(user_id):
    points_data = load_user_points()
    return points_data.get(user_id, 0)

def add_user_points(user_id, amount):
    points_data = load_user_points()
    points_data[user_id] = points_data.get(user_id, 0) + amount
    save_user_points(points_data)
    return points_data[user_id]

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
        value="`!daily` - Claim daily reward\n`!game` - Play mini games\n`!points` - Check your points\n`!leaderboard` - View top players",
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
