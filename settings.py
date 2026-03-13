import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Set log file path to the current directory
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("Loading settings.py configuration.")

# Guild (Server) ID
GUILD_ID = int(os.getenv("GUILD_ID"))
logger.info(f"GUILD_ID set to {GUILD_ID}")

# Owner ID
OWNER_ID = int(os.getenv("OWNER_ID"))
logger.info(f"OWNER_ID set to {OWNER_ID}")

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID"))
logger.info(f"BOT_OWNER_ID set to {BOT_OWNER_ID}")

# Moderator Role IDs
Moderator_role_ID = int(os.getenv("MODERATOR_ROLE_ID"))
logger.info(f"Moderator_role_ID set to {Moderator_role_ID}")

# LOG Channel IDs
BOT_LOG_CHANNEL_ID = int(os.getenv("BOT_LOG_CHANNEL_ID"))
logger.info(f"BOT_LOG_CHANNEL_ID set to {BOT_LOG_CHANNEL_ID}")

# LEADERBOARD Channel IDs
LEADERBOARD_CHANNEL_ID = int(os.getenv("LEADERBOARD_CHANNEL_ID"))
logger.info(f"LEADERBOARD_CHANNEL_ID set to {LEADERBOARD_CHANNEL_ID}")

# CHANNELS
RULES_CHANNEL_ID = int(os.getenv("RULES_CHANNEL_ID"))
logger.info(f"RULES_CHANNEL_ID set to {RULES_CHANNEL_ID}")

GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID"))
logger.info(f"GENERAL_CHANNEL_ID set to {GENERAL_CHANNEL_ID}")

BOT_COMMANDS_CHANNEL_ID = int(os.getenv("BOT_COMMANDS_CHANNEL_ID"))
logger.info(f"BOT_COMMANDS_CHANNEL_ID set to {BOT_COMMANDS_CHANNEL_ID}")

SHOP_CHANNEL_ID = int(os.getenv("SHOP_CHANNEL_ID"))
logger.info(f"SHOP_CHANNEL_ID set to {SHOP_CHANNEL_ID}")

# Birthday role ID
BIRTHDAY_ROLE_ID = int(os.getenv("BIRTHDAY_ROLE_ID"))
logger.info(f"BIRTHDAY_ROLE_ID set to {BIRTHDAY_ROLE_ID}")

# Economy settings
CURRENCY_NAME = os.getenv("CURRENCY_NAME", "Gamer God Gold")
logger.info(f"CURRENCY_NAME set to {CURRENCY_NAME}")

# XP settings
XP_for_message = 10
logger.info(f"XP_for_message set to {XP_for_message}")

XP_for_emoji_reaction = 5
logger.info(f"XP_for_emoji_reaction set to {XP_for_emoji_reaction}")

XP_for_voice = 10
logger.info(f"XP_for_voice set to {XP_for_voice}")

XP_for_poll = 100
logger.info(f"XP_for_poll set to {XP_for_poll}")

XP_MULTIPLIER = 1.0
logger.info(f"XP_MULTIPLIER set to {XP_MULTIPLIER}")

XP_EVENT_MULTIPLIER = 2.0
logger.info(f"XP_EVENT_MULTIPLIER set to {XP_EVENT_MULTIPLIER}")

# Tax brackets (income thresholds and corresponding tax rates)
TAX_BRACKETS = [
    (0, 0.01),      # 1%
    (100, 0.02),
    (200, 0.03),
    (500, 0.04),
    (1000, 0.05),
    (10000, 0.06),
    (50000, 0.07),
]
logger.info(f"TAX_BRACKETS set to {TAX_BRACKETS}")

# XP rank promotion settings
xp_new_rank_remove_old = False
logger.info(f"xp_new_rank_remove_old set to {xp_new_rank_remove_old}")

# XP ranks
CONNECTED_RANKS = [
    (10, int(os.getenv("RANK_GODS_ROLE_ID"))),
    (1000, int(os.getenv("RANK_GAMERGODS_ROLE_ID"))),
]
logger.info(f"CONNECTED_RANKS set to {CONNECTED_RANKS}")
