import token
from idlelib import config

import discord
from discord.ext import commands
import json
import asyncio
from datetime import timedelta
import os

# 1. BOT SETUP
intents = discord.Intents.all()
bot  = commands.Bot(command_prefix="!", intents=intents)


# Hilfsfunktion zum Laden/Speichern der Kanal-Daten
def load_data():
    if not os.path.exists("data.json"):
        return {}
    with open("data.json", "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)


# 2. TICKET SYSTEM UI
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Unban Appeal", description="Apply for an unban", emoji="🔓"),
            discord.SelectOption(label="Questions & Support", description="General questions about the server",
                                 emoji="❓"),
            discord.SelectOption(label="Report a Bug", description="Report an error or bug", emoji="🐛"),
        ]
        super().__init__(placeholder="Select a category...", min_values=1, max_values=1, options=options,
                         custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        kategorie_name = self.values[0]
        guild = interaction.guild
        user = interaction.user

        await interaction.response.send_message(f"Your ticket for **{kategorie_name}** is being created...",
                                                ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        kanal_name = f"{kategorie_name.lower().replace(' ', '-')}-{user.name}"
        channel = await guild.create_text_channel(name=kanal_name, overwrites=overwrites)

        embed = discord.Embed(
            title=f"🎫 Ticket: {kategorie_name}",
            description=f"Hello {user.mention}, thank you for reaching out.\nA staff member will assist you shortly.\n\nClick the button below to close this ticket.",
            color=discord.Color.orange()
        )

        view = TicketCloseView()
        await channel.send(embed=embed, view=view)


class TicketCloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("This ticket will be deleted in 5 seconds...", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception:
            pass


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCloseButton())


class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())


# --- GANZ OBEN (unter deine Imports): ---
is_filter_active = True
schimpfwoerter = ["arsch", "arschkriecher", "arschloch", "asozialer", "assi", "bastard", "behindert", "bekloppt",
    "besserwisser", "bitch", "blödmann", "clown", "depp", "drecksau", "dreckskerl", "dummschwätzer",
    "eigenbrötler", "elend", "ficker", "fotze", "fratze", "hackfresse", "hampelmann", "hurensohn",
    "hure", "idiot", "idoten", "itaker", "jammerlappen", "kackvogel", "kacke", "kek", "lappen",
    "lelek", "loser", "lumpi", "lusche", "mistgeburt", "misststück", "missgeburt", "miststück",
    "neidhammel", "nervensäge", "niete", "noob", "ochse", "pfeife", "pimmel", "pisser", "popel",
    "pussy", "ratte", "rabenmutter", "sackgesicht", "sau", "schandmaul", "scheisse", "scheisser",
    "schlampe", "schmarotzer", "schmock", "schnorrer", "schwein", "spacko", "spasst", "spasti",
    "spinner", "stümper", "trottel", "vogel", "vollidiot", "vollpfosten", "wichser", "wichtigtuer",
    "wixer", "zicke",
    "ass", "asshole", "asswipe", "bastard", "bitch", "bullshit", "crap", "cunt",
    "dick", "dickhead", "dildo", "dipshit", "douche", "douchebag", "dumbass", "dumbshit",
    "fag", "faggot", "freak", "fuck", "fucker", "fucking", "fuckface", "fuckhead",
    "goddamn", "hell", "ho", "hoe", "idiot", "infidel", "jerk", "jerkoff",
    "loser", "moron", "motherfucker", "nerd", "noob", "nigger", "nuts", "piss",
    "pissed", "pisser", "prick", "pussy", "retard", "scumbag", "shit", "shithead",
    "shitter", "slut", "sonofabitch", "sucker", "twat", "wanker", "whore", "wimp", "nigga"]

# --- HIER DEIN EVENT: ---
@bot.event
async def on_message(message):
    global is_filter_active
    if message.author.bot:
        return

    if is_filter_active:
        msg_content = message.content.lower()
        if any(wort in msg_content for wort in schimpfwoerter):
            try:
                await message.delete()
            except Exception:
                pass

            is_admin = message.author.guild_permissions.administrator or message.author.id == message.guild.owner_id

            if is_admin:
                await message.channel.send(
                    f"{message.author.mention} Oh, you cool boy – no offense, but my boy, you are muted now!",
                    delete_after=10)
            else:
                try:
                    dauer = timedelta(minutes=1)
                    await message.author.timeout(dauer, reason="Schimpfwort benutzt")
                except Exception as e:
                    print(f"Fehler beim Muten: {e}")

                await message.channel.send(f"{message.author.mention} Oh, you cool guy – no offense, my friend!",
                                           delete_after=10)
            return

    await bot.process_commands(message)

# --- HIER DER BEFEHL (unten dran): ---
@bot.command()
@commands.has_permissions(administrator=True)
async def beleidigungen(ctx, status: str):
    global is_filter_active
    if status.lower() == "start":
        is_filter_active = True
        await ctx.send("✅ Filter aktiviert.")
    elif status.lower() == "stop":
        is_filter_active = False
        await ctx.send("❌ Filter deaktiviert.")




# 4. TEXT COMMANDS (!setup, !willkommen & !website)
@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="📩 Create a Support Ticket",
        description="Do you need help, want to report a bug, or submit an unban appeal?\n\nJust select the appropriate category from the dropdown menu below to open a private ticket with the staff team!",
        color=discord.Color.blue()
    )

    view = TicketDropdownView()
    await ctx.message.delete()
    await ctx.send(embed=embed, view=view)


@bot.group(name="willkommen", invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def willkommen(ctx):
    await ctx.send("Nutze `!willkommen setup`, um diesen Kanal als Willkommens-Kanal einzurichten.")


@willkommen.command(name="setup")
@commands.has_permissions(administrator=True)
async def willkommen_setup(ctx):
    data = load_data()
    guild_id = str(ctx.guild.id)

    if guild_id not in data:
        data[guild_id] = {}

    data[guild_id]["welcome_channel"] = ctx.channel.id
    save_data(data)

    await ctx.send(f"✅ Dieser Kanal ({ctx.channel.mention}) wurde erfolgreich als Willkommens-Kanal gespeichert!")


# AUF ENGLISCH UMBENANNT UND ANGEPASST
@bot.command(name="website")
async def website(ctx):
    await ctx.send("Here is the link to the J🤝🤝 BOT  website: https://jbot.sticklight.app//")


SERVER_STRUCTURE = {
    "======= 📊 SERVER 📊 =======": [
        "💁‍♀️-server info ",
        "Announcements "
    ],
    "======= VC =======": [
        "🔊-voice-1",
        "🔊-voice-2",
        "🔊-voice-3",
        "🔊-voice-4",
        "🔊-voice-5"
    ],
    "======= Welcome =======": [
        "👋-welcome",
        "📄-rules",
        "📜-terms-of-service",
        "🔗-discord-invite",
        "✅-legit-check",
        "🕳-void",
        "🙊-update",
        "📱social-media"
    ],
    "======= General =======": [
        "💬-chat",
        "🤝-suggestions",
        "📁-self-promo",
        "🎉-giveaway",
        "💛-partner",
        "👹-hall-of-ayri",
        "⚔-clan",
        "🎫-ticket-tool",
        "📳server-ip",
        "📹videos"
    ],
    "======= Information =======": [
        "ℹ-information",
        "🛡-security",
        "🔄-changelogs",
        "✅-proofs",
        "👑-vip",
        "🧾-team-list"
    ]
}


@bot.group()
async def kanal(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Please use: `!kanal setup`")


@kanal.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild
    await ctx.send("Starting setup, please wait...")

    for category_name, channels in SERVER_STRUCTURE.items():
        category = await guild.create_category(category_name)

        for channel_name in channels:
            if "🔊" in channel_name:
                await guild.create_voice_channel(channel_name, category=category)
            else:
                await guild.create_text_channel(channel_name, category=category)

            await asyncio.sleep(1.5)

    await ctx.send("Setup complete!")
@bot.command()
@commands.has_permissions(administrator=True)
async def rules(ctx, option: int = 1):
    # Schwarzer Seitenbalken
    schwarz = discord.Color.from_rgb(0, 0, 0)

    # Deutsch (Option 1)
    if option == 1:
        embed = discord.Embed(
            title="🎵 Serverregeln",
            description="Bitte lies dir die Regeln sorgfältig durch und bestätige dies mit einer Reaktion durch das ✅ Emoji.",
            color=schwarz
        )
        embed.add_field(name="§1 Respekt", value="• Behandle alle Mitglieder respektvoll.\n• Keine Beleidigungen, Diskriminierung, Mobbing oder gezielte Hetze.", inline=False)
        embed.add_field(name="§2 Werbung", value="• Jegliche Eigen-, Fremd- oder Serverwerbung ist ohne ausdrückliche Genehmigung verboten.\n• Dies beinhaltet Songs, Social Media, Discord-Server, Streams oder Videos.", inline=False)
        embed.add_field(name="§3 Spam", value="• Spam, Flooding oder unnötiges Pingen ist untersagt.\n• Nutze die korrekten Kanäle.", inline=False)
        embed.add_field(name="§4 Feedback", value="• Konstruktive Kritik ist willkommen.\n• Respektiere die Meinungen anderer.", inline=False)
        embed.add_field(name="§5 Verbotene Inhalte", value="• Keine NSFW-, Hass-, extremistischen oder illegalen Inhalte.", inline=False)
        embed.add_field(name="§6 Datenschutz", value="• Veröffentliche keine persönlichen Daten von dir oder anderen ohne Zustimmung.", inline=False)
        embed.add_field(name="§7 Team", value="• Befolge die Anweisungen des Server-Teams.\n• Entscheidungen des Teams müssen respektiert werden.", inline=False)
        embed.add_field(name="§8 Konsequenzen", value="Verstöße können mit einer Verwarnung, einem Timeout, Kick oder permanenten Bann bestraft werden.\n\nMit dem Betreten des Servers akzeptierst du diese Regeln.", inline=False)

    # Englisch (Option 2)
    elif option == 2:
        embed = discord.Embed(
            title="🎵 Server Rules",
            description="Please read the rules carefully and confirm by reacting with the ✅ emoji.",
            color=schwarz
        )
        embed.add_field(name="§1 Respect", value="• Treat all members with respect.\n• No insults, discrimination, mobbing or hate speech.", inline=False)
        embed.add_field(name="§2 Self-Promotion", value="• Any self-promotion is prohibited.\n• This includes songs, social media, discord servers, streams or videos.\n• Promotion is only allowed with explicit permission from the team.", inline=False)
        embed.add_field(name="§3 No Spam", value="• No spam, flooding or unnecessary pings.\n• Use the correct channels.", inline=False)
        embed.add_field(name="§4 Feedback", value="• Constructive criticism is welcome.\n• Respect the opinions of others.", inline=False)
        embed.add_field(name="§5 Prohibited Content", value="• No NSFW, hate, extremist or illegal content.", inline=False)
        embed.add_field(name="§6 Data Privacy", value="• Do not publish personal data of yourself or others without consent.", inline=False)
        embed.add_field(name="§7 Team", value="• Follow the instructions of the server team.\n• Decisions of the team must be respected.", inline=False)
        embed.add_field(name="§8 Consequences", value="Violations can be punished with a warning, timeout, kick or permanent ban.\n\nBy entering the server you accept these rules.", inline=False)

    else:
        await ctx.send("Bitte benutze `!rules 1` für Deutsch oder `!rules 2` für Englisch.")
        return

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")

RULES_FILE = "rules_setup.json"


def load_rules_data():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_rules_data(data):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# 1. ERST DIE HILFSFUNKTIONEN DEFINIEREN
RULES_FILE = "rules_setup.json"


def load_rules_data():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_rules_data(data):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@bot.command()
@commands.has_permissions(administrator=True)
async def emoji(ctx, action=None):

    if action != "setup":
        await ctx.send("❌ Benutze: `!emoji setup`")
        return

    role = discord.utils.get(ctx.guild.roles, name="Member")

    if role is None:
        await ctx.send("❌ Die Rolle `Member` wurde nicht gefunden!")
        return

    embed = discord.Embed(
        title="Verifizierung",
        description="Klicke auf ✅, um die Rolle **Member** zu bekommen.",
        color=discord.Color.green()
    )

    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")

    # Daten speichern
    with open("emoji_setup.txt", "w") as f:
        f.write(f"{ctx.guild.id}|{ctx.channel.id}|{message.id}|{role.id}")

    await ctx.send("✅ Verifizierung wurde eingerichtet!")


@bot.event
async def on_raw_reaction_add(payload):

    if payload.member is None or payload.member.bot:
        return

    try:
        with open("emoji_setup.txt", "r") as f:
            guild_id, channel_id, message_id, role_id = f.read().split("|")

        if (
            payload.guild_id == int(guild_id)
            and payload.channel_id == int(channel_id)
            and payload.message_id == int(message_id)
            and str(payload.emoji) == "✅"
        ):
            guild = bot.get_guild(payload.guild_id)
            role = guild.get_role(int(role_id))
            member = guild.get_member(payload.user_id)

            if role and member and role not in member.roles:
                await member.add_roles(role)

    except FileNotFoundError:
        pass

TICKET_DATA_FILE = "ticket_data.json"


# ------------------------------
# SAVE / LOAD
# ------------------------------

def load_ticket_data():
    if os.path.exists(TICKET_DATA_FILE):
        try:
            with open(TICKET_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    return {}


ticket_data = load_ticket_data()


def save_ticket_data():
    with open(TICKET_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(ticket_data, f, indent=4)


# ------------------------------
# TICKET CLOSE BUTTON
# ------------------------------

class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.red,
        custom_id="persistent_close_ticket"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "🔒 This ticket will be closed in 5 seconds."
        )

        await asyncio.sleep(5)

        try:
            await interaction.channel.delete()
        except:
            pass


# ------------------------------
# TICKET CATEGORY DROPDOWN
# ------------------------------

class TicketSelect(discord.ui.Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="General Question",
                description="Ask us anything",
                emoji="❓",
                value="question"
            ),

            discord.SelectOption(
                label="Support",
                description="Get help with an issue",
                emoji="🛠️",
                value="support"
            ),

            discord.SelectOption(
                label="Report a Bug",
                description="Report a bug or problem",
                emoji="🐛",
                value="bug"
            ),

            discord.SelectOption(
                label="Player Report",
                description="Report another player",
                emoji="🚨",
                value="report"
            ),

            discord.SelectOption(
                label="Other",
                description="Something else",
                emoji="📩",
                value="other"
            )

        ]

        super().__init__(
            placeholder="Select a ticket category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_ticket_select"
        )


    async def callback(self, interaction: discord.Interaction):

        guild = interaction.guild
        user = interaction.user
        ticket_type = self.values[0]

        # Check if user already has a ticket
        for channel in guild.text_channels:

            if channel.topic == f"ticket-owner:{user.id}":

                await interaction.response.send_message(
                    f"❌ You already have an open ticket: {channel.mention}",
                    ephemeral=True
                )

                return


        # Find / create ticket category
        category = discord.utils.get(
            guild.categories,
            name="TICKETS"
        )

        if category is None:

            category = await guild.create_category(
                "TICKETS"
            )


        # Permissions
        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
        }


        # Create ticket channel
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites,
            topic=f"ticket-owner:{user.id}"
        )


        # Save ticket
        ticket_data[str(channel.id)] = {
            "guild_id": guild.id,
            "user_id": user.id,
            "category": ticket_type
        }

        save_ticket_data()


        # Category names
        category_names = {

            "question": "General Question",
            "support": "Support",
            "bug": "Report a Bug",
            "report": "Player Report",
            "other": "Other"

        }

        category_name = category_names.get(
            ticket_type,
            "Other"
        )


        # Ticket embed
        embed = discord.Embed(
            title="🎫 Ticket Created",
            description=(
                f"Welcome {user.mention}!\n\n"
                f"**Category:** `{category_name}`\n\n"
                "Please describe your issue as clearly as possible. "
                "A member of our team will assist you shortly."
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Created by Jason"
        )


        await channel.send(
            content=user.mention,
            embed=embed,
            view=CloseTicketView()
        )


        await interaction.response.send_message(
            f"✅ Your ticket has been created: {channel.mention}",
            ephemeral=True
        )


# ------------------------------
# TICKET PANEL VIEW
# ------------------------------

class TicketView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            TicketSelect()
        )


# ------------------------------
# !ticket COMMAND
# ------------------------------

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):

    embed = discord.Embed(
        title="🎫 Support Center",
        description=(
            "Need help?\n\n"
            "Select a category below to create a ticket.\n\n"
            "❓ **General Question**\n"
            "Ask us anything.\n\n"
            "🛠️ **Support**\n"
            "Get help with an issue.\n\n"
            "🐛 **Report a Bug**\n"
            "Report a bug or problem.\n\n"
            "🚨 **Player Report**\n"
            "Report another player.\n\n"
            "📩 **Other**\n"
            "For anything else."
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(
        text="Created by Jason"
    )


    message = await ctx.send(
        embed=embed,
        view=TicketView()
    )


    # Save panel
    ticket_data["panel"] = {
        "guild_id": ctx.guild.id,
        "channel_id": ctx.channel.id,
        "message_id": message.id
    }

    save_ticket_data()


# ------------------------------
# LOAD BUTTONS AFTER RESTART
# ------------------------------

@bot.event
async def on_ready():

    # Persistent views
    bot.add_view(
        TicketView()
    )

    bot.add_view(
        CloseTicketView()
    )

    print(f"✅ Logged in as {bot.user}")
    print("🎫 Persistent ticket system loaded.")

# ==============================
# PERSISTENT HUHU / WELCOME SYSTEM
# ==============================

import json
import os

WELCOME_FILE = "welcome_data.json"


# Daten laden
if os.path.exists(WELCOME_FILE):
    try:
        with open(WELCOME_FILE, "r", encoding="utf-8") as f:
            welcome_data = json.load(f)
    except:
        welcome_data = {}
else:
    welcome_data = {}


# Daten speichern
def save_welcome_data():
    with open(WELCOME_FILE, "w", encoding="utf-8") as f:
        json.dump(welcome_data, f, indent=4)


# ==============================
# !huhu
# ==============================

@bot.command()
@commands.has_permissions(administrator=True)
async def huhu(ctx):

    guild_id = str(ctx.guild.id)

    welcome_data[guild_id] = {
        "channel_id": ctx.channel.id
    }

    save_welcome_data()

    embed = discord.Embed(
        title="✅ Welcome System",
        description=(
            f"Welcome messages are now enabled in "
            f"{ctx.channel.mention}!"
        ),
        color=discord.Color.green()
    )

    embed.set_footer(
        text="Created by Jason"
    )

    await ctx.send(embed=embed)


# ==============================
# WHEN SOMEONE JOINS
# ==============================

@bot.event
async def on_member_join(member):

    guild_id = str(member.guild.id)

    if guild_id not in welcome_data:
        return

    channel_id = welcome_data[guild_id].get("channel_id")

    if not channel_id:
        return

    channel = member.guild.get_channel(channel_id)

    if channel is None:
        return

    embed = discord.Embed(
        title="👋 Welcome!",
        description=(
            f"🎉 **{member.mention} joined the server!**\n\n"
            f"Welcome to **{member.guild.name}**!\n\n"
            "We hope you enjoy your stay! ❤️"
        ),
        color=discord.Color.green()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"Member #{member.guild.member_count}"
    )

    await channel.send(embed=embed)

# ==========================================
# DISCORD MODERATION LOGS
# ==========================================

LOGS_FILE = "logs_data.json"


# ==========================================
# LOAD LOG DATA
# ==========================================

if os.path.exists(LOGS_FILE):
    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            logs_data = json.load(f)
    except:
        logs_data = {}
else:
    logs_data = {}


# ==========================================
# SAVE LOG DATA
# ==========================================

def save_logs_data():
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs_data, f, indent=4)


# ==========================================
# !logs
# ==========================================

@bot.command()
@commands.has_permissions(administrator=True)
async def logs(ctx):

    guild_id = str(ctx.guild.id)

    logs_data[guild_id] = {
        "channel_id": ctx.channel.id
    }

    save_logs_data()

    embed = discord.Embed(
        title="📜 Moderation Logs",
        description=(
            f"All important server actions will now be logged here.\n\n"
            f"📍 Channel: {ctx.channel.mention}\n\n"
            "The log system is permanently saved."
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(
        text="Created by Jason"
    )

    await ctx.send(embed=embed)


# ==========================================
# SEND LOG
# ==========================================

async def send_log(
    guild,
    title,
    description,
    color=discord.Color.blurple()
):

    guild_id = str(guild.id)

    if guild_id not in logs_data:
        return

    channel_id = logs_data[guild_id].get(
        "channel_id"
    )

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)

    if channel is None:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=discord.utils.utcnow()
    )

    embed.set_footer(
        text=f"Server: {guild.name}"
    )

    try:
        await channel.send(embed=embed)
    except:
        pass


# ==========================================
# MEMBER JOIN
# ==========================================

@bot.event
async def on_member_join(member):

    await send_log(
        member.guild,
        "📥 Member Joined",
        (
            f"**User:** {member.mention}\n"
            f"**Username:** `{member}`\n"
            f"**ID:** `{member.id}`"
        ),
        discord.Color.green()
    )


# ==========================================
# MEMBER LEAVE
# ==========================================

@bot.event
async def on_member_remove(member):

    await send_log(
        member.guild,
        "📤 Member Left",
        (
            f"**User:** `{member}`\n"
            f"**ID:** `{member.id}`"
        ),
        discord.Color.red()
    )


# ==========================================
# MESSAGE DELETE
# ==========================================

@bot.event
async def on_message_delete(message):

    if message.author.bot:
        return

    if not message.guild:
        return

    content = message.content

    if not content:
        content = "*No text content*"

    if len(content) > 1000:
        content = content[:1000] + "..."

    await send_log(
        message.guild,
        "🗑️ Message Deleted",
        (
            f"**Author:** {message.author.mention}\n"
            f"**Channel:** {message.channel.mention}\n"
            f"**Message:**\n```{content}```"
        ),
        discord.Color.orange()
    )


# ==========================================
# MESSAGE EDIT
# ==========================================

@bot.event
async def on_message_edit(before, after):

    if before.author.bot:
        return

    if not before.guild:
        return

    if before.content == after.content:
        return

    old_content = before.content or "*Empty*"
    new_content = after.content or "*Empty*"

    if len(old_content) > 500:
        old_content = old_content[:500] + "..."

    if len(new_content) > 500:
        new_content = new_content[:500] + "..."

    await send_log(
        before.guild,
        "✏️ Message Edited",
        (
            f"**User:** {before.author.mention}\n"
            f"**Channel:** {before.channel.mention}\n\n"
            f"**Before:**\n```{old_content}```\n"
            f"**After:**\n```{new_content}```"
        ),
        discord.Color.yellow()
    )


# ==========================================
# MEMBER UPDATE
# ==========================================

@bot.event
async def on_member_update(before, after):

    # Timeout
    if before.timed_out_until != after.timed_out_until:

        if after.timed_out_until is not None:

            await send_log(
                after.guild,
                "🔇 Member Timed Out",
                (
                    f"**User:** {after.mention}\n"
                    f"**ID:** `{after.id}`\n"
                    f"**Until:** <t:{int(after.timed_out_until.timestamp())}:F>"
                ),
                discord.Color.red()
            )

        else:

            await send_log(
                after.guild,
                "🔊 Timeout Removed",
                (
                    f"**User:** {after.mention}\n"
                    f"**ID:** `{after.id}`"
                ),
                discord.Color.green()
            )


    # Rollen
    before_roles = set(before.roles)
    after_roles = set(after.roles)

    added_roles = after_roles - before_roles
    removed_roles = before_roles - after_roles

    for role in added_roles:

        if role.is_default():
            continue

        await send_log(
            after.guild,
            "➕ Role Added",
            (
                f"**User:** {after.mention}\n"
                f"**Role:** {role.mention}"
            ),
            discord.Color.green()
        )

    for role in removed_roles:

        if role.is_default():
            continue

        await send_log(
            after.guild,
            "➖ Role Removed",
            (
                f"**User:** {after.mention}\n"
                f"**Role:** {role.mention}"
            ),
            discord.Color.orange()
        )


# ==========================================
# ROLE CREATED
# ==========================================

@bot.event
async def on_guild_role_create(role):

    await send_log(
        role.guild,
        "➕ Role Created",
        f"**Role:** {role.mention}\n**Name:** `{role.name}`",
        discord.Color.green()
    )


# ==========================================
# ROLE DELETED
# ==========================================

@bot.event
async def on_guild_role_delete(role):

    await send_log(
        role.guild,
        "🗑️ Role Deleted",
        f"**Role:** `{role.name}`",
        discord.Color.red()
    )


# ==========================================
# CHANNEL CREATED
# ==========================================

@bot.event
async def on_guild_channel_create(channel):

    await send_log(
        channel.guild,
        "📁 Channel Created",
        (
            f"**Channel:** {channel.mention}\n"
            f"**Name:** `{channel.name}`"
        ),
        discord.Color.green()
    )


# ==========================================
# CHANNEL DELETED
# ==========================================

@bot.event
async def on_guild_channel_delete(channel):

    await send_log(
        channel.guild,
        "🗑️ Channel Deleted",
        f"**Channel:** `{channel.name}`",
        discord.Color.red()
    )

@bot.command(name="sper")
@commands.has_permissions(administrator=True)
async def sperre_und_privatisieren(ctx):
    guild = ctx.guild
    everyone_role = guild.default_role
    member_role = discord.utils.get(guild.roles, name="Member")

    if not member_role:
        await ctx.send("❌ Die Rolle **Member** wurde auf dem Server nicht gefunden! Bitte erstelle sie zuerst.")
        return

    status_msg = await ctx.send("🔒 Sperre den Server und stelle alle Kategorien auf privat...")

    # 1. Alle Kategorien anpassen
    for category in guild.categories:
        try:
            # @everyone: Komplett aussperren (Kanal nicht mehr sichtbar)
            await category.set_permissions(
                everyone_role,
                view_channel=False
            )

            # Member: Dürfen Kanäle SEHEN, aber NICHT SCHREIBEN oder SPRECHEN
            await category.set_permissions(
                member_role,
                view_channel=True,
                send_messages=False,
                send_messages_in_threads=False,
                create_public_threads=False,
                create_private_threads=False,
                read_message_history=True,
                connect=True,
                speak=False
            )

            # Synchronisiere alle Kanäle innerhalb der Kategorie, damit sie die neuen Rechte übernehmen
            for channel in category.channels:
                try:
                    await channel.edit(sync_permissions=True)
                except discord.HTTPException:
                    pass

        except discord.Forbidden:
            print(f"Keine Rechte für Kategorie: {category.name}")
        except discord.HTTPException as e:
            print(f"Fehler bei Kategorie {category.name}: {e}")

    # 2. Alle aktiven Threads sperren
    for thread in guild.threads:
        try:
            await thread.edit(locked=True)
        except discord.Forbidden:
            print(f"Keine Rechte für Thread: {thread.name}")

    await status_msg.edit(
        content="✅ **Erfolgreich ausgeführt!**\n"
                "• Kanäle sind jetzt **privat** (nur für Admins & Member sichtbar).\n"
                "• Member können die Kanäle lesen, aber **nicht mehr schreiben**.\n"
                "• Nur **Administratoren** können weiterhin schreiben!"
    )

@sperre_und_privatisieren.error
async def sper_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du benötigst Administrator-Rechte, um diesen Befehl auszuführen.")

@bot.command(name="A")
@commands.has_permissions(manage_roles=True)
async def annehmen(ctx, member: discord.Member):
    # Rolle "Member" suchen
    role = discord.utils.get(ctx.guild.roles, name="Member")

    if role is None:
        await ctx.send("❌ Die Rolle **Member** wurde nicht gefunden.")
        return

    # Prüfen, ob der Bot die Rolle vergeben darf
    if role >= ctx.guild.me.top_role:
        await ctx.send("❌ Ich kann die Rolle **Member** nicht vergeben. Meine Bot-Rolle muss über der Member-Rolle stehen.")
        return

    # Rolle vergeben
    await member.add_roles(role)

    # Schöne Nachricht
    embed = discord.Embed(
        title="✅ Mitglied angenommen",
        description=f"**{member.mention} wurde angenommen!**\n\n"
                    f"🎉 Willkommen auf dem Server!\n"
                    f"👤 Rolle: **Member**",
        color=discord.Color.green()
    )

    embed.set_footer(text=f"Angenommen von {ctx.author}")

    await ctx.send(embed=embed)

@bot.command(name="AN")
@commands.has_permissions(manage_roles=True)
async def nicht_angenommen(ctx, member: discord.Member):
    # Rolle "NICHT AKTEPTIERT" suchen
    role = discord.utils.get(ctx.guild.roles, name="NICHT AKTEPTIERT")

    if role is None:
        await ctx.send("❌ Die Rolle **NICHT AKTEPTIERT** wurde nicht gefunden.")
        return

    # Prüfen, ob der Bot die Rolle vergeben darf
    if role >= ctx.guild.me.top_role:
        await ctx.send(
            "❌ Ich kann die Rolle **NICHT AKTEPTIERT** nicht vergeben. "
            "Meine Bot-Rolle muss über dieser Rolle stehen."
        )
        return

    # Rolle vergeben
    await member.add_roles(role)

    # Traurige Nachricht
    embed = discord.Embed(
        title="😢 Bewerbung abgelehnt",
        description=(
            f"**{member.mention} wurde leider nicht akzeptiert.**\n\n"
            f"😢 Deine Bewerbung wurde abgelehnt.\n"
            f"👤 Rolle: **NICHT AKTEPTIERT**"
        ),
        color=discord.Color.red()
    )

    embed.set_footer(text=f"Entscheidung von {ctx.author}")

    await ctx.send(embed=embed)

# ============================================================
# SERVER-SETUPS
# ============================================================


# ============================================================
# STANDARD-SERVER
# ============================================================

STANDARD_STRUCTURE = {

    "INFOS": [
        ("👋", "willkommen", False),
        ("📜", "regeln", False),
        ("📢", "ankündigungen", False),
        ("ℹ️", "informationen", False),
    ],

    "COMMUNITY": [
        ("💬", "hauptchat", True),
        ("🗣️", "community", True),
        ("🎥", "videos", True),
        ("📸", "bilder", True),
        ("😂", "memes", True),
        ("💡", "ideen", True),
    ],

    "BOTS": [
        ("🤖", "bot-befehle", True),
        ("📊", "server-statistiken", False),
        ("🎁", "giveaways", True),
    ],

    "SPRACHKANÄLE": [
        ("🔊", "lobby", True),
        ("🎙️", "talk", True),
        ("🎵", "musik", True),
    ],
}


# ============================================================
# COMMUNITY CHANNEL
# ============================================================

COMMUNITY_CHANNEL_STRUCTURE = {

    "📊 SERVER 📊": [
        ("💁", "server-info", False),
        ("📢", "announcements", False),
        ("🟧", "server-ip", False),
        ("📹", "videos", False),
    ],

    "VC": [
        ("🔊", "voice-1", True),
        ("🔊", "voice-2", True),
        ("🔊", "voice-3", True),
        ("🔊", "voice-4", True),
        ("🔊", "voice-5", True),
        ("✋", "Waiting Room", True),
    ],

    "Welcome": [
        ("👏", "welcome", False),
        ("📄", "rules", False),
        ("📜", "terms-of-service", False),
        ("🔗", "discord-invite", False),
        ("✅", "legit-check", False),
        ("🕳️", "void", False),
        ("🏫", "update", False),
        ("🎰", "social-media", False),
    ],

    "Information": [
        ("ℹ️", "information", False),
        ("🛡️", "security", False),
        ("🔄", "changelogs", False),
        ("✅", "proofs", False),
        ("👑", "vip", False),
        ("📜", "team-list", False),
    ],

    "General": [
        ("💬", "chat", True),
        ("🤝", "suggestions", True),
        ("📁", "self-promo", True),
        ("🎉", "giveaway", True),
        ("💛", "partner", True),
        ("😈", "hall-of-ayri", True),
        ("⚔️", "clan", True),
        ("🎫", "ticket-tool", True),
    ],
}


# ============================================================
# GAMING-SERVER
# ============================================================

GAMING_STRUCTURE = {

    "📌 INFOS": [
        ("👋", "willkommen", False),
        ("📜", "regeln", False),
        ("📢", "ankündigungen", False),
        ("ℹ️", "informationen", False),
    ],

    "🎮 GAMING LOBBY": [
        ("🎮", "suche-mitspieler", True),
        ("💬", "gaming-chat", True),
        ("🔥", "setup-showcase", True),
        ("🕹️", "game-talk", True),
        ("👥", "team-suche", True),
        ("🎮", "Ticket Tool", True),
    ],

    "🏆 COMPETE & CLIPS": [
        ("🏆", "turniere", True),
        ("📸", "gaming-clips", True),
        ("🎥", "highlights", True),
        ("🥇", "erfolge", True),
        ("⚔️", "competitive", True),
    ],

    "🤖 BOTS & MEDIA": [
        ("🤖", "bot-befehle", True),
        ("🎵", "musik", True),
        ("🎁", "giveaways", True),
        ("📊", "statistiken", False),
    ],

    "🔊 GAMING-TALK": [
        ("🔊", "gaming-lobby", True),
        ("🎙️", "team-talk", True),
        ("🎧", "chill-lounge", True),
        ("🎮", "gaming-voice", True),
        ("✋", "Waiting Room", True),
    ],
}


# ============================================================
# STREAMER-SERVER
# ============================================================

STREAMER_STRUCTURE = {

    # --------------------------------------------------------
    # SERVER STATUS
    # Diese beiden werden separat erstellt.
    # --------------------------------------------------------

    "Server Status": [],

    # --------------------------------------------------------
    # WILLKOMMEN
    # --------------------------------------------------------

    "Willkommen": [
        ("🎉", "willkommen", False),
        ("📜", "regeln", False),
        ("🔔", "ankündigung", False),
        ("❓", "server-info", False),
        ("⚡", "partnerschaften", False),
    ],

    # --------------------------------------------------------
    # GENERAL TEXT
    # --------------------------------------------------------

    "General - Text": [
        ("💬", "general", True),
        ("🌐", "tiktok-twitch", True),
        ("💻", "setups", True),
        ("🤖", "bot-commands", True),
        ("🎫", "ticket-support", True),
    ],

    # --------------------------------------------------------
    # GENERAL VOICE
    # --------------------------------------------------------

    "General - Voice": [
        ("🔇", "muted", "muted"),
        ("🎙️", "lounge-1", "voice"),
        ("🎙️", "lounge-2", "voice"),
        ("🎙️", "lounge-3", "voice"),
        ("🔒", "private-vc-1", "private"),
        ("🔒", "private-vc-2", "private"),
        ("🔒", "private-vc-3", "private"),
        ("🎧", "music-bots", "voice"),
        ("✋", "Waiting Room", True),
    ],

    # --------------------------------------------------------
    # SPECIAL ROOMS
    # --------------------------------------------------------

    "Special Rooms": [
        ("👍", "gang", False),
        ("🏆", "vips", False),
        ("💎", "nitro-boosters", False),
    ],
}


# ============================================================
# HILFSFUNKTION
# ============================================================

def make_channel_name(emoji, name):

    return f"{emoji}-{name.lower()}"


# ============================================================
# ROLLE ERSTELLEN / FINDEN
# ============================================================

async def get_or_create_role(
    guild,
    name,
    colour=None
):

    role = discord.utils.get(
        guild.roles,
        name=name
    )

    if role:
        return role

    return await guild.create_role(
        name=name,
        colour=colour or discord.Colour.default(),
        reason="Server Setup"
    )


# ============================================================
# SERVER-ROLLEN
# ============================================================

async def create_server_roles(
    guild,
    gaming=False,
    streamer=False
):

    roles = {}

    # --------------------------------------------------------
    # MEMBER
    # --------------------------------------------------------

    roles["Member"] = await get_or_create_role(
        guild,
        "Member",
        discord.Colour.blue()
    )

    # --------------------------------------------------------
    # GAMING ROLLEN
    # --------------------------------------------------------

    if gaming:

        gaming_roles = {

            "Gamer": discord.Colour.green(),

            "Clips": discord.Colour.purple(),

            "PC": discord.Colour.dark_grey(),

            "Console": discord.Colour.orange(),

            "Streamer": discord.Colour.red(),
        }

        for role_name, colour in gaming_roles.items():

            roles[role_name] = await get_or_create_role(
                guild,
                role_name,
                colour
            )

    # --------------------------------------------------------
    # STREAMER ROLLEN
    # --------------------------------------------------------

    if streamer:

        streamer_roles = {

            "Streamer": discord.Colour.red(),

            "Content-Creator": discord.Colour.purple(),

            "Twitch": discord.Colour.purple(),

            "YouTube": discord.Colour.red(),

            "TikTok": discord.Colour.pink(),

            "VIP": discord.Colour.gold(),

            "Booster": discord.Colour.purple(),
        }

        for role_name, colour in streamer_roles.items():

            roles[role_name] = await get_or_create_role(
                guild,
                role_name,
                colour
            )

    return roles


# ============================================================
# EVERYONE PERMISSIONS
# ============================================================

def everyone_permissions():

    return discord.PermissionOverwrite(
        view_channel=False
    )


# ============================================================
# MEMBER PERMISSIONS
# ============================================================

def member_permissions(
    read_only=False
):

    permissions = discord.PermissionOverwrite(

        view_channel=True,

        read_message_history=True,

        connect=True,

        speak=True
    )

    if read_only:

        permissions.send_messages = False

        permissions.create_public_threads = False

        permissions.create_private_threads = False

        permissions.send_messages_in_threads = False

    else:

        permissions.send_messages = True

        permissions.create_public_threads = True

        permissions.create_private_threads = True

        permissions.send_messages_in_threads = True

    return permissions


# ============================================================
# ADMIN PERMISSIONS
# ============================================================

def admin_permissions():

    return discord.PermissionOverwrite(

        view_channel=True,

        send_messages=True,

        read_message_history=True,

        connect=True,

        speak=True,

        manage_channels=True,

        manage_messages=True
    )


# ============================================================
# KATEGORIE ERSTELLEN
# ============================================================

async def create_setup_category(
    guild,
    category_name,
    member_role
):

    overwrites = {

        guild.default_role:
            everyone_permissions(),

        member_role:
            member_permissions(False)
    }

    category = await guild.create_category(

        name=category_name,

        overwrites=overwrites,

        reason="Server Setup"
    )

    return category


# ============================================================
# TEXTKANAL ERSTELLEN
# ============================================================

async def create_setup_text_channel(
    category,
    emoji,
    name,
    writable,
    member_role
):

    guild = category.guild

    overwrites = {

        guild.default_role:
            everyone_permissions(),

        member_role:
            member_permissions(
                read_only=not writable
            )
    }

    return await guild.create_text_channel(

        name=make_channel_name(
            emoji,
            name
        ),

        category=category,

        overwrites=overwrites,

        reason="Server Setup"
    )


# ============================================================
# NORMALES VOICE ERSTELLEN
# ============================================================

async def create_setup_voice_channel(
    category,
    emoji,
    name,
    member_role
):

    guild = category.guild

    overwrites = {

        guild.default_role:
            everyone_permissions(),

        member_role:
            member_permissions(False)
    }

    return await guild.create_voice_channel(

        name=make_channel_name(
            emoji,
            name
        ),

        category=category,

        overwrites=overwrites,

        reason="Server Setup"
    )


# ============================================================
# STREAMER STATUS CHANNEL
# ============================================================

async def create_streamer_status_channel(
    category,
    emoji,
    channel_name,
    number
):

    guild = category.guild

    # Jeder darf den Status sehen.
    # Niemand darf dem Voice-Kanal beitreten.

    overwrites = {

        guild.default_role:
            discord.PermissionOverwrite(

                view_channel=True,

                connect=False,

                speak=False,

                send_messages=False,

                read_message_history=True
            )
    }

    return await guild.create_voice_channel(

        name=f"{emoji}・{number} {channel_name}",

        category=category,

        overwrites=overwrites,

        reason="Streamer Server Status"
    )


# ============================================================
# STREAMER VOICE
# ============================================================

async def create_streamer_voice_channel(
    category,
    emoji,
    name,
    member_role,
    private=False,
    muted=False
):

    guild = category.guild

    # --------------------------------------------------------
    # MUTED
    # --------------------------------------------------------

    if muted:

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(

                    view_channel=True,

                    connect=False,

                    speak=False
                ),

            member_role:
                discord.PermissionOverwrite(

                    view_channel=True,

                    connect=False,

                    speak=False
                )
        }

    # --------------------------------------------------------
    # PRIVATE
    # --------------------------------------------------------

    elif private:

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            member_role:
                discord.PermissionOverwrite(

                    view_channel=True,

                    connect=True,

                    speak=True
                )
        }

    # --------------------------------------------------------
    # NORMALES VOICE
    # --------------------------------------------------------

    else:

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            member_role:
                discord.PermissionOverwrite(

                    view_channel=True,

                    connect=True,

                    speak=True
                )
        }

    return await guild.create_voice_channel(

        name=f"{emoji}-{name}",

        category=category,

        overwrites=overwrites,

        reason="Streamer Server Setup"
    )


# ============================================================
# STREAMER STATUS AKTUALISIEREN
# ============================================================

async def update_streamer_status(
    guild
):

    category = discord.utils.get(
        guild.categories,
        name="Server Status"
    )

    if category is None:
        return

    members_channel = None
    boosts_channel = None

    for channel in category.voice_channels:

        if "mitglieder" in channel.name.lower():

            members_channel = channel

        elif "boosts" in channel.name.lower():

            boosts_channel = channel

    # --------------------------------------------------------
    # MITGLIEDER
    # --------------------------------------------------------

    if members_channel:

        try:

            await members_channel.edit(

                name=(
                    f"👥・{guild.member_count} "
                    f"mitglieder"
                )
            )

        except discord.HTTPException:

            pass

    # --------------------------------------------------------
    # BOOSTS
    # --------------------------------------------------------

    if boosts_channel:

        try:

            await boosts_channel.edit(

                name=(
                    f"💎・"
                    f"{guild.premium_subscription_count} "
                    f"boosts"
                )
            )

        except discord.HTTPException:

            pass


# ============================================================
# KOMPLETTES SERVER-SETUP
# ============================================================

async def create_server_setup(
    guild,
    setup_type
):

    gaming = (
        setup_type == "gaming"
    )

    streamer = (
        setup_type == "streamer"
    )

    # --------------------------------------------------------
    # ROLLEN
    # --------------------------------------------------------

    roles = await create_server_roles(

        guild,

        gaming=gaming,

        streamer=streamer
    )

    member_role = roles["Member"]

    # --------------------------------------------------------
    # STRUKTUR
    # --------------------------------------------------------

    if setup_type == "standard":

        structure = STANDARD_STRUCTURE

    elif setup_type == "community":

        structure = COMMUNITY_CHANNEL_STRUCTURE

    elif setup_type == "gaming":

        structure = GAMING_STRUCTURE

    elif setup_type == "streamer":

        structure = STREAMER_STRUCTURE

    else:

        raise ValueError(
            "Unbekanntes Server-Setup."
        )

    created_categories = []

    # ========================================================
    # KATEGORIEN
    # ========================================================

    for category_name, channels in structure.items():

        category = await create_setup_category(

            guild,

            category_name,

            member_role
        )

        created_categories.append(
            category
        )

        # ====================================================
        # STREAMER SERVER STATUS
        # ====================================================

        if (
            setup_type == "streamer"
            and category_name == "Server Status"
        ):

            members_channel = (
                await create_streamer_status_channel(

                    category,

                    "👥",

                    "mitglieder",

                    guild.member_count
                )
            )

            boosts_channel = (
                await create_streamer_status_channel(

                    category,

                    "💎",

                    "boosts",

                    guild.premium_subscription_count
                )
            )

            continue

        # ====================================================
        # KANÄLE
        # ====================================================

        for channel_data in channels:

            emoji = channel_data[0]

            channel_name = channel_data[1]

            channel_type = channel_data[2]

            # ------------------------------------------------
            # STREAMER VOICE
            # ------------------------------------------------

            if (
                setup_type == "streamer"
                and category_name == "General - Voice"
            ):

                if channel_type == "muted":

                    await create_streamer_voice_channel(

                        category,

                        emoji,

                        channel_name,

                        member_role,

                        muted=True
                    )

                elif channel_type == "private":

                    await create_streamer_voice_channel(

                        category,

                        emoji,

                        channel_name,

                        member_role,

                        private=True
                    )

                else:

                    await create_streamer_voice_channel(

                        category,

                        emoji,

                        channel_name,

                        member_role
                    )

                continue

            # ------------------------------------------------
            # VC-KATEGORIEN
            # ------------------------------------------------

            if (

                category_name == "SPRACHKANÄLE"

                or category_name == "VC"

                or category_name == "🔊 GAMING-TALK"

            ):

                await create_setup_voice_channel(

                    category,

                    emoji,

                    channel_name,

                    member_role
                )

            # ------------------------------------------------
            # NORMALE TEXTKANÄLE
            # ------------------------------------------------

            else:

                await create_setup_text_channel(

                    category,

                    emoji,

                    channel_name,

                    channel_type,

                    member_role
                )

    return roles, created_categories


# ============================================================
# STREAMER STATUS - MEMBER JOIN
# ============================================================

@bot.event
async def on_member_join(member):

    try:

        await update_streamer_status(
            member.guild
        )

    except Exception:

        pass


# ============================================================
# STREAMER STATUS - MEMBER LEAVE
# ============================================================

@bot.event
async def on_member_remove(member):

    try:

        await update_streamer_status(
            member.guild
        )

    except Exception:

        pass


# ============================================================
# DROPDOWN
# ============================================================

class ChannelSetupSelect(
    discord.ui.Select
):

    def __init__(self):

        options = [

            # ------------------------------------------------
            # STANDARD
            # ------------------------------------------------

            discord.SelectOption(

                label="Standard-Server",

                description=(
                    "Erstellt einen normalen "
                    "Community-Server."
                ),

                emoji="🌐",

                value="standard"
            ),

            # ------------------------------------------------
            # COMMUNITY
            # ------------------------------------------------

            discord.SelectOption(

                label="Community Channel",

                description=(
                    "Erstellt einen umfangreichen "
                    "Community-Server."
                ),

                emoji="📊",

                value="community"
            ),

            # ------------------------------------------------
            # GAMING
            # ------------------------------------------------

            discord.SelectOption(

                label="Gaming-Server",

                description=(
                    "Erstellt einen Server "
                    "für Gaming."
                ),

                emoji="🎮",

                value="gaming"
            ),

            # ------------------------------------------------
            # STREAMER
            # ------------------------------------------------

            discord.SelectOption(

                label="Streamer-Server",

                description=(
                    "Erstellt einen Server "
                    "für Streamer und Creator."
                ),

                emoji="🎥",

                value="streamer"
            )
        ]

        super().__init__(

            placeholder=(
                "Wähle ein Server-Setup..."
            ),

            min_values=1,

            max_values=1,

            options=options
        )

    # ========================================================
    # CALLBACK
    # ========================================================

    async def callback(
        self,
        interaction
    ):

        # ----------------------------------------------------
        # ADMIN CHECK
        # ----------------------------------------------------

        if not (
            interaction
            .user
            .guild_permissions
            .administrator
        ):

            await interaction.response.send_message(

                "❌ Du musst Administrator sein.",

                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # AUSWAHL
        # ----------------------------------------------------

        selected = self.values[0]

        if selected == "standard":

            setup_name = (
                "Standard-Server"
            )

        elif selected == "community":

            setup_name = (
                "Community Channel"
            )

        elif selected == "gaming":

            setup_name = (
                "Gaming-Server"
            )

        elif selected == "streamer":

            setup_name = (
                "Streamer-Server"
            )

        else:

            setup_name = (
                "Server-Setup"
            )

        # ----------------------------------------------------
        # LOADING
        # ----------------------------------------------------

        await interaction.response.defer(
            ephemeral=True
        )

        # ----------------------------------------------------
        # SERVER ERSTELLEN
        # ----------------------------------------------------

        try:

            roles, categories = (
                await create_server_setup(

                    interaction.guild,

                    selected
                )
            )

            role_names = ", ".join(

                role.name

                for role in roles.values()
            )

            await interaction.followup.send(

                (
                    f"✅ **{setup_name} wurde erstellt!**\n\n"

                    f"📁 Kategorien: "
                    f"**{len(categories)}**\n"

                    f"🎭 Rollen: "
                    f"**{role_names}**\n\n"

                    "🔒 Die normalen erstellten "
                    "Bereiche sind für `@everyone` "
                    "unsichtbar.\n"

                    "👤 Mitglieder mit der Rolle "
                    "`Member` können sie sehen.\n\n"

                    "📊 Beim Streamer-Server werden "
                    "Mitglieder und Boosts automatisch "
                    "angezeigt."
                ),

                ephemeral=True
            )

        # ----------------------------------------------------
        # KEINE RECHTE
        # ----------------------------------------------------

        except discord.Forbidden:

            await interaction.followup.send(

                (
                    "❌ Der Bot hat nicht genügend Rechte.\n\n"

                    "Bitte gib ihm mindestens:\n"

                    "• Kanäle verwalten\n"
                    "• Rollen verwalten\n"
                    "• Kanäle ansehen\n"
                    "• Rollen verwalten"
                ),

                ephemeral=True
            )

        # ----------------------------------------------------
        # DISCORD FEHLER
        # ----------------------------------------------------

        except discord.HTTPException as error:

            await interaction.followup.send(

                (
                    "❌ Discord konnte die "
                    "Serverstruktur nicht vollständig "
                    "erstellen.\n\n"

                    f"Fehler: `{error}`"
                ),

                ephemeral=True
            )

        # ----------------------------------------------------
        # ANDERER FEHLER
        # ----------------------------------------------------

        except Exception as error:

            await interaction.followup.send(

                (
                    "❌ Ein unerwarteter Fehler "
                    "ist aufgetreten.\n\n"

                    f"Fehler: `{error}`"
                ),

                ephemeral=True
            )


# ============================================================
# DROPDOWN VIEW
# ============================================================

class ChannelSetupView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

        self.add_item(
            ChannelSetupSelect()
        )


# ============================================================
# !channel
# ============================================================

@bot.command(
    name="channel"
)

@commands.guild_only()
async def channel(ctx):

    # --------------------------------------------------------
    # ADMIN CHECK
    # --------------------------------------------------------

    if not (
        ctx.author
        .guild_permissions
        .administrator
    ):

        await ctx.send(

            "❌ Nur Administratoren können "
            "`!channel` benutzen.",

            delete_after=8
        )

        return

    # --------------------------------------------------------
    # EMBED
    # --------------------------------------------------------

    embed = discord.Embed(

        title="🛠️ Server-Setup",

        description=(

            "Wähle unten ein Server-Setup aus.\n\n"

            "🌐 **Standard-Server**\n"
            "Ein normaler Community-Server mit "
            "Infos, Community, Bots und Sprachkanälen.\n\n"

            "📊 **Community Channel**\n"
            "Ein umfangreicher Community-Server mit "
            "Server, VC, Welcome, Information und "
            "General.\n\n"

            "🎮 **Gaming-Server**\n"
            "Ein Gaming-Server mit Gaming-Rollen, "
            "Gaming-Lobby, Turnieren, Clips und "
            "Sprachkanälen.\n\n"

            "🎥 **Streamer-Server**\n"
            "Ein Server für Streamer und Creator "
            "mit Mitglieder-/Boost-Anzeige, "
            "Textkanälen, Voice-Channels, privaten "
            "VCs und Special Rooms."
        ),

        colour=discord.Colour.blurple()
    )

    embed.set_footer(

        text=(
            "Nur Administratoren können "
            "dieses Setup starten " 
            "Made By Jason (J🤝🤝)"

        )
    )

    # --------------------------------------------------------
    # DROPDOWN SENDEN
    # --------------------------------------------------------

    await ctx.send(

        embed=embed,

        view=ChannelSetupView()
    )

# ============================================================
# !nachrichtaus
# ============================================================

@bot.command(name="nachrichtaus")
@commands.guild_only()
async def nachrichtaus(ctx):

    # Nur Administratoren
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(
            "❌ Nur Administratoren können diesen Befehl benutzen.",
            delete_after=5
        )
        return

    channel = ctx.channel
    everyone = ctx.guild.default_role

    # Aktuelle Rechte von @everyone übernehmen
    overwrite = channel.overwrites_for(everyone)

    # Schreiben deaktivieren
    overwrite.send_messages = False

    # Threads deaktivieren
    overwrite.create_public_threads = False
    overwrite.create_private_threads = False
    overwrite.send_messages_in_threads = False

    try:
        await channel.set_permissions(
            everyone,
            overwrite=overwrite,
            reason=f"Nachrichten deaktiviert von {ctx.author}"
        )

        # Bestätigung
        await ctx.send(
            "🔒 Dieser Kanal ist jetzt gesperrt. "
            "Neue Nachrichten werden nach 5 Sekunden gelöscht.",
            delete_after=5
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Ich habe keine Berechtigung, die Kanalrechte zu ändern.",
            delete_after=5
        )

    except discord.HTTPException as error:
        await ctx.send(
            f"❌ Fehler: `{error}`",
            delete_after=5
        )


# ============================================================
# NEUE NACHRICHTEN NACH 5 SEKUNDEN LÖSCHEN
# ============================================================

@bot.event
async def on_message(message):

    # Bot-Nachrichten nicht löschen
    if message.author.bot:
        return

    # Nur Nachrichten in Kanälen bearbeiten,
    # in denen @everyone nicht schreiben darf.
    if isinstance(message.channel, discord.TextChannel):

        overwrite = message.channel.overwrites_for(
            message.guild.default_role
        )

        if overwrite.send_messages is False:

            try:
                await message.delete(delay=5)

            except discord.NotFound:
                pass

            except discord.Forbidden:
                pass

            except discord.HTTPException:
                pass

            return

    # Andere Bot-Befehle weiterhin verarbeiten
    await bot.process_commands(message)

# ============================================================
# !hilfe
# ============================================================

@bot.command(name="hilfe")
@commands.guild_only()
async def hilfe(ctx):

    embed = discord.Embed(
        title="📖 BEFEHLE",
        description=(
            "`!ticket`\n"
            "`!huhu`\n"
            "`!help`\n"
            "`!rules 1`\n"
            "`!rules 2`\n"
            "`!website`\n"
            "`!logs`\n"
            "`!nachrichtenaus`\n"
            "`!a`\n"
            "`!an`\n"
            "`!emoji`\n"
            "`!chanel`\n"
            "`!sper`\n"
            "`!beleidigungen`\n"
            "`!unname`\n"
            "`!autorole`\n"
            "`!delete`"

        ),
        colour=discord.Colour.blurple()
    )

    embed.set_footer(
        text=f"Angefordert von {ctx.author}"
    )

    await ctx.send(embed=embed)

# ============================================================
# !delete
# Löscht alle Kategorien und Kanäle
# ============================================================

@bot.command(name="delete")
@commands.guild_only()
async def delete(ctx):

    # Nur Administratoren
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(
            "❌ Nur Administratoren können `!delete` benutzen.",
            delete_after=5
        )
        return

    # Sicherheitsabfrage
    confirm_message = await ctx.send(
        "⚠️ **ACHTUNG!**\n\n"
        "Dieser Befehl löscht **ALLE KANÄLE UND KATEGORIEN** "
        "auf diesem Server.\n\n"
        "Rollen werden **nicht** gelöscht.\n\n"
        "Schreibe innerhalb von **15 Sekunden** `BESTÄTIGEN`, "
        "um fortzufahren."
    )

    def check(message):
        return (
            message.author == ctx.author
            and message.channel == ctx.channel
            and message.content.upper() == "BESTÄTIGEN"
        )

    try:
        confirmation = await bot.wait_for(
            "message",
            timeout=15,
            check=check
        )

    except TimeoutError:
        await confirm_message.edit(
            content="❌ Vorgang abgebrochen. Keine Bestätigung erhalten."
        )
        return

    # Bestätigung löschen
    try:
        await confirmation.delete()
    except discord.HTTPException:
        pass

    await confirm_message.edit(
        content="🗑️ **Lösche alle Kanäle und Kategorien...**"
    )

    guild = ctx.guild

    deleted = 0

    # Kategorien zuerst löschen
    for category in list(guild.categories):

        try:
            await category.delete(
                reason=f"Server-Bereinigung durch {ctx.author}"
            )
            deleted += 1

        except discord.Forbidden:
            pass

        except discord.HTTPException:
            pass

    # Verbleibende Kanäle löschen
    for channel in list(guild.channels):

        try:
            await channel.delete(
                reason=f"Server-Bereinigung durch {ctx.author}"
            )
            deleted += 1

        except discord.Forbidden:
            pass

        except discord.HTTPException:
            pass

    # Diese Nachricht kann eventuell nicht mehr existieren,
    # falls der Kanal währenddessen gelöscht wurde.
    print(
        f"🗑️ {deleted} Kanäle/Kategorien auf "
        f"{guild.name} gelöscht."
    )

# ============================================================
# !unname
# Kanal umbenennen
# ============================================================

@bot.command(name="unname")
@commands.guild_only()
async def unname(ctx):

    # Nur Administratoren
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(
            "❌ Nur Administratoren können `!unname` benutzen.",
            delete_after=5
        )
        return

    await ctx.send(
        "✏️ **Wie soll dieser Kanal heißen?**\n"
        "Schreibe den neuen Namen hier in den Chat.\n\n"
        "⏱️ Du hast 30 Sekunden Zeit.",
        delete_after=30
    )

    def check(message):
        return (
            message.author == ctx.author
            and message.channel == ctx.channel
            and not message.author.bot
        )

    try:
        message = await bot.wait_for(
            "message",
            timeout=30,
            check=check
        )

    except TimeoutError:
        await ctx.send(
            "❌ Zeit abgelaufen. Der Kanal wurde nicht umbenannt.",
            delete_after=5
        )
        return

    new_name = message.content.strip()

    # Discord-Kanalnamen dürfen nicht leer sein
    if not new_name:
        await ctx.send(
            "❌ Der Kanalname darf nicht leer sein.",
            delete_after=5
        )
        return

    # Kanalnamen auf 100 Zeichen begrenzen
    new_name = new_name[:100]

    try:
        await ctx.channel.edit(
            name=new_name,
            reason=f"Kanal umbenannt von {ctx.author}"
        )

        # Nachricht mit dem neuen Namen löschen
        try:
            await message.delete()
        except discord.HTTPException:
            pass

        await ctx.send(
            f"✅ Kanal wurde zu **`{new_name}`** umbenannt.",
            delete_after=5
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Ich habe keine Berechtigung, diesen Kanal umzubenennen.",
            delete_after=5
        )

    except discord.HTTPException as error:
        await ctx.send(
            f"❌ Fehler beim Umbenennen: `{error}`",
            delete_after=5
        )

# ============================================================
# !autorole
# Erstellt automatisch wichtige Server-Rollen
# ============================================================

@bot.command(name="autorole")
@commands.guild_only()
async def autorole(ctx):

    # --------------------------------------------------------
    # ADMIN CHECK
    # --------------------------------------------------------

    if not ctx.author.guild_permissions.administrator:
        await ctx.send(
            "❌ Nur Administratoren können `!autorole` benutzen.",
            delete_after=5
        )
        return

    # --------------------------------------------------------
    # ROLLEN
    # --------------------------------------------------------
    #
    # Nur Standard-Farben verwenden, die discord.py sicher
    # unterstützt.
    #

    roles = [

        # STAFF
        ("👑 Owner", discord.Colour.red()),
        ("🛡️ Co-Owner", discord.Colour.dark_red()),
        ("🔨 Head-Admin", discord.Colour.orange()),
        ("⚔️ Admin", discord.Colour.dark_orange()),

        # MODERATION
        ("🔧 Head-Moderator", discord.Colour.gold()),
        ("🛡️ Moderator", discord.Colour.blue()),
        ("🔰 Trial-Moderator", discord.Colour.blue()),

        # BUILDER
        ("🏗️ Head-Builder", discord.Colour.green()),
        ("🏗️ Builder", discord.Colour.dark_green()),

        # DEVELOPMENT
        ("💻 Head-Developer", discord.Colour.purple()),
        ("💻 Developer", discord.Colour.dark_purple()),
        ("⌨️ Scripter", discord.Colour.magenta()),

        # MEDIA
        ("🎨 Designer", discord.Colour.pink()),
        ("🎬 Media", discord.Colour.red()),
        ("📸 Content-Creator", discord.Colour.pink()),

        # CREATOR
        ("🎥 Streamer", discord.Colour.purple()),
        ("📺 YouTuber", discord.Colour.red()),

        # SUPPORT
        ("🎫 Support", discord.Colour.teal()),
        ("🤝 Helper", discord.Colour.green()),

        # SPECIAL
        ("💎 VIP", discord.Colour.gold()),
        ("🌟 Booster", discord.Colour.purple()),

        # SYSTEM
        ("🤖 Bot", discord.Colour.dark_grey()),
        ("👤 Member", discord.Colour.blue()),
        ("🚫 Muted", discord.Colour.dark_grey()),
    ]

    created = []
    existing = []

    # --------------------------------------------------------
    # ROLLEN ERSTELLEN
    # --------------------------------------------------------

    for role_name, colour in roles:

        # Prüfen, ob die Rolle bereits existiert
        existing_role = discord.utils.get(
            ctx.guild.roles,
            name=role_name
        )

        if existing_role is not None:
            existing.append(role_name)
            continue

        try:

            new_role = await ctx.guild.create_role(
                name=role_name,
                colour=colour,
                reason=f"Automatische Rollen-Erstellung durch {ctx.author}"
            )

            created.append(new_role)

        except discord.Forbidden:

            await ctx.send(
                "❌ Ich kann keine weiteren Rollen erstellen.\n\n"
                "Überprüfe bitte:\n"
                "• Der Bot hat `Rollen verwalten`.\n"
                "• Die Bot-Rolle steht über den Rollen, "
                "die er erstellen soll.",
                delete_after=10
            )

            return

        except discord.HTTPException as error:

            await ctx.send(
                "❌ Discord hat beim Erstellen einer Rolle "
                "einen Fehler zurückgegeben:\n\n"
                f"`{error}`",
                delete_after=10
            )

            return

    # --------------------------------------------------------
    # ERGEBNIS
    # --------------------------------------------------------

    embed = discord.Embed(
        title="🎭 AUTO ROLE",
        colour=discord.Colour.blurple()
    )

    if created:

        created_text = "\n".join(
            f"• {role.mention}"
            for role in created
        )

        embed.add_field(
            name=f"✅ Neu erstellt ({len(created)})",
            value=created_text,
            inline=False
        )

    if existing:

        existing_text = "\n".join(
            f"• `{name}`"
            for name in existing
        )

        embed.add_field(
            name=f"ℹ️ Bereits vorhanden ({len(existing)})",
            value=existing_text,
            inline=False
        )

    if not created:

        embed.description = (
            "Alle vorgesehenen Rollen sind bereits vorhanden."
        )

    embed.set_footer(
        text=f"Ausgeführt von {ctx.author}"
    )

    await ctx.send(embed=embed)

# ============================================================
# !channelreset
# Löscht alle Nachrichten im aktuellen Kanal
# ============================================================

@bot.command(name="channelreset")
@commands.guild_only()
async def channelreset(ctx):

    # Nur Administratoren
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(
            "❌ Nur Administratoren können `!channelreset` benutzen.",
            delete_after=5
        )
        return

    channel = ctx.channel

    try:
        # Alle Nachrichten löschen
        deleted = await channel.purge(
            limit=None,
            reason=f"!channelreset von {ctx.author}"
        )

        # Diese Nachricht wird nach dem Löschen der anderen
        # Nachrichten gesendet und nach 5 Sekunden gelöscht.
        await channel.send(
            f"🧹 **Kanal zurückgesetzt!**\n"
            f"🗑️ {len(deleted)} Nachrichten wurden gelöscht.",
            delete_after=5
        )

    except discord.Forbidden:

        await ctx.send(
            "❌ Ich habe keine Berechtigung, "
            "Nachrichten in diesem Kanal zu verwalten.",
            delete_after=8
        )

    except discord.HTTPException as error:

        await ctx.send(
            f"❌ Discord-Fehler beim Löschen:\n`{error}`",
            delete_after=8
        )

@bot.command()
@commands.has_permissions(administrator=True)
async def private(ctx, status: str = None):
    if status is None:
        await ctx.send("❌ Benutzung: `!private off`")
        return

    if status.lower() != "off":
        await ctx.send("❌ Benutzung: `!private off`")
        return

    guild = ctx.guild
    everyone = guild.default_role

    await ctx.send("🔄 Mache alle Kategorien und Kanäle öffentlich...")

    erfolgreich = 0
    fehler = 0

    # Alle Kategorien öffentlich machen
    for category in guild.categories:
        try:
            await category.set_permissions(
                everyone,
                view_channel=True
            )
            erfolgreich += 1
        except (discord.Forbidden, discord.HTTPException):
            fehler += 1

    # Alle Kanäle öffentlich machen
    for channel in guild.channels:
        if isinstance(channel, discord.CategoryChannel):
            continue

        try:
            await channel.set_permissions(
                everyone,
                view_channel=True
            )
            erfolgreich += 1
        except (discord.Forbidden, discord.HTTPException):
            fehler += 1

    await ctx.send(
        f"✅ **Private-Modus ausgeschaltet!**\n"
        f"🌐 Öffentlich gemacht: **{erfolgreich}**\n"
        f"⚠️ Fehler: **{fehler}**"
    )


@private.error
async def private_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du brauchst Administrator-Rechte.")

@bot.command()
@commands.has_permissions(administrator=True)
async def privatkanal(ctx):

    everyone = ctx.guild.default_role

    member_role = discord.utils.get(
        ctx.guild.roles,
        name="Member"
    )

    if member_role is None:
        await ctx.send("❌ Die Rolle `Member` wurde nicht gefunden.")
        return

    try:
        # Kanal privat machen
        await ctx.channel.set_permissions(
            everyone,
            view_channel=False
        )

        # Member darf rein
        await ctx.channel.set_permissions(
            member_role,
            view_channel=True
        )

        # 5 Sekunden warten
        await asyncio.sleep(5)

        # Alle Nachrichten löschen
        async for message in ctx.channel.history(limit=None):
            try:
                await message.delete()
            except discord.NotFound:
                pass
            except discord.Forbidden:
                print("❌ Keine Berechtigung zum Löschen.")
                return
            except discord.HTTPException:
                pass

    except discord.Forbidden:
        await ctx.send(
            "❌ Der Bot braucht die Berechtigungen "
            "`Kanäle verwalten` und `Nachrichten verwalten`."
        )

    except discord.HTTPException as e:
        print(f"Discord-Fehler: {e}")


@privatkanal.error
async def privatkanal_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ Du brauchst Administrator-Rechte."
        )

@bot.command()
@commands.has_permissions(administrator=True)
async def chat(ctx, aktion: str = None):

    if aktion is None:
        await ctx.send(
            "❌ Benutzung: `!chat schreiben`"
        )
        return

    if aktion.lower() == "schreiben":

        try:
            # @everyone darf den Kanal sehen,
            # aber NICHT schreiben
            await ctx.channel.set_permissions(
                ctx.guild.default_role,
                view_channel=True,
                send_messages=False
            )

            # Administratoren dürfen weiterhin schreiben
            await ctx.channel.set_permissions(
                ctx.guild.me,
                send_messages=True
            )

            await ctx.send(
                "🔒 **Chat gesperrt!**\n"
                "👑 Nur Administratoren können jetzt schreiben."
            )

        except discord.Forbidden:
            await ctx.send(
                "❌ Ich habe keine Berechtigung, "
                "die Kanal-Berechtigungen zu ändern."
            )

        except discord.HTTPException as e:
            print(f"Discord-Fehler: {e}")

    else:
        await ctx.send(
            "❌ Benutzung: `!chat schreiben`"
        )


@chat.error
async def chat_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ Du brauchst Administrator-Rechte."
        )

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx):

    try:
        # Den !clear-Befehl selbst ebenfalls löschen
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass

        # Kompletten Nachrichtenverlauf durchgehen
        while True:
            messages = [
                message
                async for message in ctx.channel.history(
                    limit=100
                )
            ]

            if not messages:
                break

            for message in messages:
                try:
                    await message.delete()

                except discord.NotFound:
                    pass

                except discord.Forbidden:
                    print("❌ Keine Berechtigung zum Löschen.")
                    return

                except discord.HTTPException as e:
                    print(f"❌ Fehler beim Löschen: {e}")

        print(f"✅ Der komplette Chat #{ctx.channel.name} wurde geleert.")

    except discord.Forbidden:
        print(
            "❌ Der Bot braucht 'Nachrichten verwalten' "
            "und 'Nachrichtenverlauf lesen'."
        )

    except discord.HTTPException as e:
        print(f"❌ Discord-Fehler: {e}")


@clear.error
async def clear_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ Du brauchst Administrator-Rechte."
        )

@bot.command(name="nurich")
@commands.has_permissions(administrator=True)
async def nurich(ctx):

    try:
        # Alle anderen dürfen lesen, aber nicht schreiben
        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            view_channel=True,
            send_messages=False
        )

        # Nur du darfst schreiben
        await ctx.channel.set_permissions(
            ctx.author,
            view_channel=True,
            send_messages=True
        )

        await ctx.send(
            f"🔒 **Kanal gesperrt!**\n"
            f"✍️ Nur {ctx.author.mention} kann schreiben."
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Der Bot hat keine Berechtigung, "
            "die Kanalrechte zu ändern."
        )

    except discord.HTTPException as e:
        print(f"Discord-Fehler: {e}")


@nurich.error
async def nurich_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du brauchst Administrator-Rechte.")
    else:
        print(f"Fehler bei !nurich: {error}")

bot.run("bot token")