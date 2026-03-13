import discord
from discord.ext import commands
from discord import app_commands
import random
import settings
import json
import os
import asyncio

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")

FISH_CATEGORIES = [
    ("Common Fish", [
        ("Minnow", 1, 20), ("Bluegill", 2, 18), ("Perch", 3, 16), ("Sunfish", 4, 15), ("Crappie", 5, 14),
        ("Catfish", 7, 13), ("Bass", 10, 12), ("Trout", 12, 11), ("Carp", 15, 10), ("Pike", 18, 9),
        ("Salmon", 20, 8), ("Walleye", 22, 7), ("Sturgeon", 25, 6), ("Eel", 28, 5), ("Red Snapper", 30, 4),
        ("Tuna", 35, 3), ("Swordfish", 40, 2), ("Marlin", 45, 1.5), ("Golden Carp", 48, 1), ("Legendary Koi", 50, 0.8),
    ]),
    ("Funny Fish", [
        ("Rubber Boot", 0, 8), ("Old Soda Can", 0, 8), ("Soggy Pizza Slice", 0, 8),
        ("Golden Toilet Seat", 100, 0.2), ("Left Sock", 0, 8), ("Angry Pufferfish", 8, 6),
        ("Disco Fish", 20, 3), ("Pixelated Fish", 15, 3), ("Fish Stick", 3, 7), ("404 Fish Not Found", 0, 8),
        ("Bananafish", 12, 5), ("Meme Carp", 25, 2), ("Sus Fish", 13, 4), ("Breadfish", 7, 6),
        ("Magic 8-Fish", 18, 3), ("Fishy McFishface", 30, 2), ("Shiny Magikarp", 100, 0.2),
        ("USB Stick (with fish pics)", 0, 2),
    ]),
    ("Custom Funny Fish", [
        ("SmokeyTaco the Salsa Shark", 21, 5), ("Klets the Chatterfish", 9, 3),
        ("Patler the Pancake Piranha", 14, 4), ("Maddie the Meme Catfish", 11, 1.5),
        ("Osiris the Overlord Octopus", 33, 6), ("Flatland the 2D Flounder", 8, 3),
        ("Haydn the Harmonica Haddock", 17, 0.8), ("Wonderboy the Wacky Whale", 50, 2),
        ("Chief the Commanding Carp", 23, 3), ("Fevereagle the Hot-Headed Herring", 19, 1),
    ]),
    ("CS:GO Themed Fish", [
        ("AWP-tuna", 47, 8), ("Flashbang Flounder", 0, 3), ("Smoke Salmon", 15, 10),
        ("Eco Round Goldfish", 1, 2), ("Clutch Carp", 30, 6), ("Deagle Dace", 7, 7),
        ("Baiting Bass", 5, 3), ("Rush B Rainbow Trout", 20, 2), ("Ninja Defuser Eel", 25, 12),
        ("Silver Elite Sardine", 2, 8),
    ]),
    ("Funny/Weird Items", [
        ("SmokeyTaco's Lost Lighter", 0, 8), ("Patler's Chipped Toenail", 0, 7),
        ("Patler's Pancake Spatula", 2, 7), ("Maddie's Meme Mug", 1, 2),
        ("Osiris' Golden Tooth", 25, 8), ("Flatland's Bent Ruler", 0, 6),
        ("Haydn's Harmonica (Out of Tune)", 3, 4), ("Wonderboy's Cape Clip", 7, 5),
        ("Chief's Commanding Whistle", 5, 6), ("Fevereagle's Molted Feather", 3, 5),
        ("secretcode_swimwiththefishes", 5, 5),
    ]),
    ("Mythical Fish", [
        ("Mythical Loch Ness Monster", 1000, 0.01),
        ("Mythical Mermaid", 1000, 0.01),
        ("Mythical The Kraken", 1000, 0.01),
    ]),
    ("CS:GO Extra Items", [
        ("Karambit Koi", 50, 2), ("StatTrak Salmon", 25, 3), ("USP-S Seaweed", 3, 8), ("Desert Eagle Driftwood", 7, 7), ("AWP Dragon Fish", 100, 0.5),
        ("P90 Plankton", 8, 6), ("M4A1-S Muddy Waters", 12, 5), ("AK-47 Algae", 15, 5), ("Glock-18 Goldfish", 10, 6), ("CZ75-Auto Clam", 6, 8),
        ("Nova Nautilus", 9, 7), ("FAMAS Flounder", 13, 5), ("MAC-10 Minnow", 4, 8), ("MP7 Mussel", 5, 8), ("P250 Puffer", 7, 7),
        ("SG 553 Sea Star", 11, 6), ("Galil Grouper", 14, 5), ("Tec-9 Tuna", 16, 6), ("Baited Bombsite", 0, 8), ("Molotov Mackerel", 2, 8),
        ("Flashbang Fishcake", 0, 8), ("Smoke Grenade Sardine", 1, 7), ("HE Grenade Haddock", 3, 7), ("Chicken Chum", 0, 8), ("Inferno Iguana", 8, 5),
        ("Mirage Minnow", 6, 6), ("Dust2 Dace", 5, 6), ("Vertigo Viperfish", 9, 5), ("Nuke Newt", 7, 5), ("Cache Catfish", 10, 5), ("Overpass Octopus", 12, 4),
    ]),
    ("Custom Extra Items", [
        ("SmokeyTaco's Spicy Flip-Flop", 3, 3), ("SmokeyTaco's Salsa Submarine", 8, 4), ("Flatland's Broken Headset", 2, 3), ("Haydn's Infinite Typo", 1, 3),
        ("Patler's Pancake Frisbee", 5, 4), ("Patler's Syrup-Soaked Sock", 2, 2), ("Maddie's Cat Meme Scroll", 4, 4), ("Maddie's Lost Laser Pointer", 3, 4),
        ("Osiris' Sunglass Monocle", 6, 3), ("Osiris' Ancient Selfie Stick", 7, 4), ("Flatland's 1D Worm", 2, 2), ("Flatland's Origami Fish", 5, 3),
        ("Haydn's Out-of-Tune Kazoo", 2, 2), ("Haydn's Fishy Metronome", 3, 3), ("Wonderboy's Cape of Confusion", 4, 4), ("Wonderboy's Mystery Mask", 6, 4),
        ("Chief's Tiny Megaphone", 3, 3), ("Chief's Emergency Donut", 4, 4), ("Fevereagle's Molten Egg", 2, 2), ("Fevereagle's Sunglasses of Sass", 5, 4),
    ]),
]

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "inventory": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "inventory": {}}, f)
        return {"wallets": {}, "inventory": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_fish_pool(has_lucky):
    pool = []
    for category, fish_list in FISH_CATEGORIES:
        for name, worth, chance in fish_list:
            mod_chance = chance
            if has_lucky and worth > 10:
                mod_chance *= 1.5
            pool.extend([(category, name, worth)] * int(mod_chance * 10))
    return pool

class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fishing_members = set()

    @app_commands.command(name="fish", description="Go fishing! Requires a fishing rod.")
    async def fish(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        # Prevent double fishing
        if user_id in self.fishing_members:
            await interaction.response.send_message("You are already fishing! Please wait for your current attempt to finish.", ephemeral=True)
            return
        self.fishing_members.add(user_id)

        data = load_data()
        inventory = data.get("inventory", {})
        user_items = inventory.get(user_id, [])

        # Check for fishing rod
        if "fishing rod" not in [item.lower() for item in user_items]:
            self.fishing_members.discard(user_id)
            await interaction.response.send_message("You need a **Fishing Rod** to fish! Buy one in the shop.", ephemeral=False)
            return

        # Check for lucky rabbit's foot
        has_lucky = any("lucky rabbit" in item.lower() for item in user_items)
        # Check for fishing boat
        has_boat = any("fishingboat" in item.replace(" ", "").lower() for item in user_items)

        # Initial message
        wait_msg = "Casting your line and waiting for fish..."
        if has_boat:
            wait_msg = "Sailing to open water with your fishing boat..."

        await interaction.response.send_message(wait_msg, ephemeral=False)
        await asyncio.sleep(random.randint(3, 10))

        # Prepare fish pool with categories
        fish_pool = get_fish_pool(has_lucky)
        if not fish_pool:
            self.fishing_members.discard(user_id)
            await interaction.followup.send("No fish available to catch!", ephemeral=True)
            return
        category, fish, worth = random.choice(fish_pool)

        # Apply fishing boat multiplier
        final_worth = worth * 3 if has_boat else worth

        # Add fish worth to wallet
        wallets = data.setdefault("wallets", {})
        wallets[user_id] = wallets.get(user_id, 0) + final_worth
        save_data(data)

        boat_msg = "\nYour fishing boat multiplies your catch value by 3!" if has_boat else ""
        await interaction.followup.send(
            f"You cast your line and caught a **{fish}**!\n"
            f"Value: **{final_worth} {settings.CURRENCY_NAME}**{boat_msg}"
        )
        self.fishing_members.discard(user_id)

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.fish, guild=guild)

async def setup(bot):
    await bot.add_cog(Fishing(bot))