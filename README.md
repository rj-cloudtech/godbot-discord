# GodBot — Custom Discord Bot

A fully custom Discord bot built in Python, developed specifically for my 
own Discord server. GodBot is the sixth iteration of a bot that started 
with basic functionality and grew into a full-featured community platform 
through continuous development and complete rebuilds.

---

## Background

Development started with a simple reputation system and expanded over 
multiple versions. Each version introduced new features or was rebuilt 
from scratch to improve the codebase and architecture.

**Version history:**
- v1 — ReputationBot: reputation points between members
- v2 — PixelBot: expanded features
- v3 — PixelBot 2.0: improved version
- v4 — LanPartyBot: community features
- v5 — LanPartyBot 2.0: improved version
- v6 — GodBot: full rebuild with all features combined

---

## Features

### Moderation
- Warning system
- Welcome messages for new members
- Embedded message creation
- Poll creation and management
- Button interactions

### XP & Leveling System
- XP earned through activity (messages, voice, reactions, polls)
- Level progression with role rewards
- Higher levels unlock additional permissions
- Members can boost each other to level faster
- Configurable XP multipliers and event multipliers

### Economy System
- Custom in-server currency: **Gamer God Gold**
- Shop with purchasable items and perks
- Tax bracket system on earnings
- Inventory management

### Games & Activities
**Resource Games (with leveling and AFK progression):**
- Fishing
- Archaeology
- Gold Mining

**Casual Games:**
- Flip a Coin
- Rock Paper Scissors
- Bank Robbery (with arrest and jail mechanics)

**Multiplayer & Social:**
- Quiz: Guess the Music, Guess the TV Show, Guess the Game, 
  Guess the Movie (audio fragments played by the bot)
- Courtroom: members can sue each other, with roles assigned 
  for judge, jury, and other participants
- Jail system: arrested members can play dice with guards 
  and the warden to escape
- Random events in text chat (e.g. coin showers members can react to)

---

## Technical Overview

- **Language:** Python
- **Architecture:** Modular — features split across sections
- **Sections:**
  - `economy/` — currency, shop, all games
  - `moderation/` — warnings, embeds, polls, welcome, profiles
  - `xp/` — XP tracking, leveling, rank roles
  - `music/` — audio playback for quiz games
- **Configuration:** All sensitive IDs and tokens stored in `.env`
- **Data storage:** JSON files (not included — see `.env.example`)

---

## Project Structure
```
godbot-discord/
├── main.py
├── settings.py
├── .env.example
├── .gitignore
└── sections/
    ├── economy/
    │   ├── economy.py
    │   ├── shop.py
    │   └── game_*.py
    ├── moderation/
    ├── music/
    └── xp/
```

---

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install discord.py python-dotenv
```
3. Copy `.env.example` to `.env` and fill in your values
4. Run the bot:
```bash
python main.py
```

---
