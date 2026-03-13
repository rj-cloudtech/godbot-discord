import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import json
from datetime import datetime, timedelta
import asyncio

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")
BANKROBBER_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "bankrobber.json")
JAIL_ROLE_ID = 1376060569437605909

GENERAL_CHANNEL_ID = 1274453503506644992  # Replace with your actual channel ID
BOT_COMMANDS_CHANNEL_ID = 1274833152782897264  # Replace with your actual channel ID

JAILBREAK_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "jailbreak.json")

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "bank": 0}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "bank": 0}, f)
        return {"wallets": {}, "bank": 0}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_bankrobber():
    if not os.path.exists(BANKROBBER_FILE):
        with open(BANKROBBER_FILE, "w") as f:
            json.dump({"last_robbery": 0, "jail": {}}, f)
    with open(BANKROBBER_FILE, "r") as f:
        return json.load(f)

def save_bankrobber(data):
    with open(BANKROBBER_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_jailbreak():
    if not os.path.exists(JAILBREAK_FILE):
        with open(JAILBREAK_FILE, "w") as f:
            json.dump({"rolls": {}, "stories_used": []}, f)
    with open(JAILBREAK_FILE, "r") as f:
        return json.load(f)

def save_jailbreak(data):
    with open(JAILBREAK_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Add these stories at the top of your file
STORIES = [
    "story1", "story2", "story3", "story4", "story5", "story6"
]

def get_story(story_idx, names):
    leader = names[0]
    follower = names[1] if len(names) > 1 else names[0]
    all_names = ", ".join(names)
    random_member = random.choice(names)
    linus_member = random.choice(names)
    linusified = f"{linus_member} Linus" if " " not in linus_member else f"{linus_member.split(' ', 1)[0]} Linus {linus_member.split(' ', 1)[1]}"
    stories = [
        (
            f"{leader} had every detail memorized, Bellicks’ rotations, the blind spots, and the secret tunnel behind the toilet. "
            f"His team followed his lead, crawling through a vent, avoiding motion sensors, and bypassing the final gate.\n"
            f"Just as freedom seemed within reach, Brad Bellick appeared, gun in hand.\n"
            f'\"You really thought this would work?\"\n'
            f"{follower} smirked, holding up the remote.\n"
            f"Click. The prison lights flickered, shutting down the cameras.\n"
            f"By the time the power came back, {all_names} were gone and the guards were left in confusion."
        ),
        (
            f"{all_names} spent six months digging through their cell walls with stolen spoons. "
            f"On the night of their escape, they placed dummy heads in their beds and squeezed into an air vent.\n\n"
            f"Slipping into the freezing waters, they paddled their handmade raft into the storm.\n\n"
            f"The next morning, the prison was in an uproar. No bodies were ever found.\n\n"
            f"Some say they drowned. Others claim they vanished into the wilderness.\n\n"
            f"But years later, a postcard arrived. \"Still free.\""
        ),
        (
            f"{all_names} were trapped on the Moon, arrested for stealing the King’s intergalactic cheese.\n"
            f"Their plan? Catapulting themselves to Earth using a stolen anti-gravity mattress.\n"
            f"Step one: Distract the guards by arguing whether sand is spicy. Step two: Steal one hamster, because every escape needs a mascot. "
            f"Step three: Activate the mattress and fling themselves back to Earth.\n"
            f"Unfortunately, Jerry forgot to adjust landing coordinates.\n"
            f"The trio crashed into a pizza shop, covered in Moon dust.\n"
            f'The owner sighed. "Gentlemen, your toppings are unacceptable."\n'
            f"Now, they’re serving cosmic cheese pizzas to pay off their sentence."
        ),
        (
            f"{all_names} were stuck in Maximum Security Time Prison, a facility designed to punish those who messed with history.\n"
            f"Their escape plan? A treadmill.\n"
            f"Step one: Convince the guards that the prison gym needed a treadmill upgrade. Step two: Modify the treadmill to run at 88 miles per hour (because, obviously, that’s how time travel works). "
            f"Step three: All three run at top speed, generating enough temporal energy to rip a hole in reality.\n"
            f"The problem? The treadmill malfunctioned, sending them straight into Medieval England.\n"
            f"Now they’re stuck training knights on the art of cardio and trying to convince people that eating vegetables is not witchcraft."
        ),
        (
            f"{all_names} were imprisoned in The Infinite Jello Cube, a sentient prison that constantly whispered \"You are but dust\" in their ears.\n"
            f"Their escape plan? Making the prison question its own existence.\n"
            f"Step one: Teach the Jello Cube philosophy, ask it if a prison is really a prison if the prisoners don’t believe in walls. "
            f"Step two: Introduce marshmallows into the conversation. Step three: Watch reality collapse as the prison starts sobbing, realizing it was just a collection of fruity regrets.\n"
            f"It worked. The Jello Cube imploded into raw confusion, launching the trio into The Land of Floating Doorframes, where everything was either soup or a concept.\n"
            f"A flying turtle handed them a receipt for “one existential crisis”, and the sky turned into a game show host that kept yelling \"Spin the universe!\".\n"
            f"No one knows if they ever truly escaped, or if escape was just an illusion formed by a marshmallow’s dream."
        ),
        (
            f"{all_names} had been locked in The Hatch, a mysterious underground prison designed to hold time criminals, people who had meddled with the server's past.\n"
            f"But they weren’t planning to rot away in Dharma Initiative solitude.\n"
            f"Their plan? Summon the Smoke Monster.\n"
            f"Step one: Steal an old VHS tape labeled \"DO NOT WATCH.\" Step two: Play it anyway, unleashing confusing 1980s commercials that disrupted the island’s reality. "
            f"Step three: Convince the Smoke Monster that it was actually a cloud of sentient boredom and persuade it to dissolve into pure existential dread.\n"
            f"The island shook violently, and suddenly, polar bears rained from the sky.\n"
            f"A sideways reality shift yanked them into a timeline where everyone was slightly more sentient crabs, but nobody understood the concept of chairs.\n"
            f"{random_member}: \"Maybe this was a bad idea.\"\n"
            f"And somewhere, in the jungle, {linusified} just stared at the sky, whispering, \"This isn’t even canon.\""
        ),
    ]
    return stories[story_idx]

class BankRobber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # On cog load (bot start), check all jailed users and release if time is up
        await self.release_expired_jail_members()

    async def release_expired_jail_members(self):
        bankrobber_data = load_bankrobber()
        jail = bankrobber_data.setdefault("jail", {})
        now = datetime.utcnow().timestamp()
        to_release = [uid for uid, release_time in jail.items() if now >= release_time]
        if not to_release:
            return
        for uid in to_release:
            guilds = self.bot.guilds
            for guild in guilds:
                member = guild.get_member(int(uid))
                if member:
                    jail_role = guild.get_role(JAIL_ROLE_ID)
                    if jail_role and jail_role in member.roles:
                        try:
                            await member.remove_roles(jail_role)
                        except Exception:
                            pass
            del jail[uid]
        save_bankrobber(bankrobber_data)

    @app_commands.command(name="bankrobber", description="Try to rob the bank! 10% chance to win, 90% chance to go to jail.")
    async def bankrobber(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        now = datetime.utcnow().timestamp()
        bankrobber_data = load_bankrobber()

        # Check if user is in jail
        jail = bankrobber_data.setdefault("jail", {})
        if user_id in jail:
            release_time = jail[user_id]
            if now < release_time:
                remaining = timedelta(seconds=int(release_time - now))
                await interaction.response.send_message(
                    f"🚔 You are in jail for trying to rob the bank! Time left: {remaining}.",
                    ephemeral=True
                )
                return
            else:
                # Release from jail
                del jail[user_id]
                guild = interaction.guild
                member = guild.get_member(interaction.user.id)
                if member:
                    jail_role = guild.get_role(JAIL_ROLE_ID)
                    if jail_role in member.roles:
                        await member.remove_roles(jail_role)
                save_bankrobber(bankrobber_data)

        # Check cooldown (12 hours)
        last_robbery = bankrobber_data.get("last_robbery", 0)
        cooldown = 12 * 60 * 60  # 12 hours in seconds
        if now < last_robbery + cooldown:
            next_time = datetime.utcfromtimestamp(last_robbery + cooldown)
            await interaction.response.send_message(
                f"🚨 Someone just tried to rob the bank! There is a lot of police now. Wait until {next_time.strftime('%Y-%m-%d %H:%M UTC')} and try again.",
                ephemeral=False
            )
            return

        # Attempt robbery
        if random.random() < 0.10:
            # Success
            data = load_data()
            bank_amount = data.get("bank", 0)
            if bank_amount <= 0:
                await interaction.response.send_message("🏦 The bank is empty! Nothing to rob.", ephemeral=False)
                return
            wallets = data.setdefault("wallets", {})
            wallets[user_id] = wallets.get(user_id, 0) + bank_amount
            data["bank"] = 0
            save_data(data)
            bankrobber_data["last_robbery"] = now
            save_bankrobber(bankrobber_data)
            await interaction.response.send_message(
                f"💰 {interaction.user.mention} successfully robbed the bank and got **{bank_amount}** coins! The police are now on high alert for 12 hours.",
                ephemeral=False
            )
        else:
            # Fail, go to jail
            jail[user_id] = now + 24 * 60 * 60  # 24 hours in jail
            bankrobber_data["last_robbery"] = now
            save_bankrobber(bankrobber_data)
            guild = interaction.guild
            member = guild.get_member(interaction.user.id)
            if member:
                jail_role = guild.get_role(JAIL_ROLE_ID)
                if jail_role and jail_role not in member.roles:
                    await member.add_roles(jail_role)
            await interaction.response.send_message(
                f"🚔 {interaction.user.mention} tried to rob the bank and got caught! You're in jail for 24 hours.",
                ephemeral=False
            )

    @app_commands.command(name="escape", description="Try to break out of jail with other inmates!")
    async def escape(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        bankrobber_data = load_bankrobber()
        jail = bankrobber_data.setdefault("jail", {})
        if user_id not in jail:
            await interaction.response.send_message("You are not in jail!", ephemeral=True)
            return

        jailbreak_data = load_jailbreak()
        rolls = jailbreak_data.setdefault("rolls", {})
        if user_id in rolls:
            await interaction.response.send_message("You already rolled your dice for this escape attempt!", ephemeral=True)
            return

        # Roll a dice (1-6)
        roll = random.randint(1, 6)
        rolls[user_id] = roll
        save_jailbreak(jailbreak_data)

        await interaction.response.send_message(f"You rolled a **{roll}** for the escape!", ephemeral=False)

        # Check if all jailed members have rolled
        all_jailed = list(jail.keys())
        if all(uid in rolls for uid in all_jailed):
            # Announce warden is coming
            channel = interaction.guild.get_channel(GENERAL_CHANNEL_ID)
            if channel:
                await channel.send("🚨 All inmates have rolled! The warden is on his way to roll the dice...")
            await asyncio.sleep(120)  # 2 minutes

            # Warden rolls
            warden_rolls = {}
            for uid in all_jailed:
                warden_rolls[uid] = random.randint(1, 6)
            total_inmates = sum(rolls[uid] for uid in all_jailed)
            total_warden = sum(warden_rolls.values())

            # Prepare names
            names = []
            for uid in all_jailed:
                member = interaction.guild.get_member(int(uid))
                if member:
                    names.append(member.display_name)
                else:
                    names.append(f"User {uid}")

            # Outcome
            if total_inmates > total_warden:
                # Escape! Remove jail role and jail status
                for uid in all_jailed:
                    member = interaction.guild.get_member(int(uid))
                    if member:
                        jail_role = interaction.guild.get_role(JAIL_ROLE_ID)
                        if jail_role and jail_role in member.roles:
                            await member.remove_roles(jail_role)
                for uid in all_jailed:
                    jail.pop(uid, None)
                save_bankrobber(bankrobber_data)

                # Story posting logic
                stories_used = jailbreak_data.setdefault("stories_used", [])
                available = [i for i in range(6) if i not in stories_used]
                if available:
                    story_idx = random.choice(available)
                    stories_used.append(story_idx)
                    channel_id = GENERAL_CHANNEL_ID
                else:
                    story_idx = random.randint(0, 5)
                    channel_id = BOT_COMMANDS_CHANNEL_ID
                jailbreak_data["stories_used"] = stories_used
                save_jailbreak(jailbreak_data)

                story = get_story(story_idx, names)
                post_channel = interaction.guild.get_channel(channel_id)
                if post_channel:
                    await post_channel.send(f"🏃‍♂️ **Jailbreak Success!**\n\n{story}")
            else:
                # Isolation for 24h
                for uid in all_jailed:
                    jail[uid] = datetime.utcnow().timestamp() + 24 * 60 * 60
                save_bankrobber(bankrobber_data)
                channel = interaction.guild.get_channel(GENERAL_CHANNEL_ID)
                if channel:
                    await channel.send("🚨 The warden rolled higher! All inmates are sent to the isolation unit for 24 hours.")

            # Reset jailbreak rolls for next attempt
            jailbreak_data["rolls"] = {}
            save_jailbreak(jailbreak_data)

async def setup(bot):
    await bot.add_cog(BankRobber(bot))