import discord
from discord.ext import commands
import random
import time
import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=5000)


def keep_alive():
    t = Thread(target=run)
    t.start()


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True


def case_insensitive_prefix(bot, message):
    prefixes = ["sq "]
    msg = message.content.lower()
    for prefix in prefixes:
        if msg.startswith(prefix):
            # Return the actual prefix length from the original message (to preserve case)
            return message.content[:len(prefix)]
    return None  # No prefix matched


def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)

def format_bait_name(bait_key, amount):
    singular = baits[bait_key].get("singular", bait_key)
    plural = bait_key
    return singular.title() if amount == 1 else plural.title()


def normalize_treasure_lookup_name(name):
    return " ".join(name.lower().replace("'", "").split())

def get_treasure_sell_value(treasure_name):
    treasure = treasure_index.get(treasure_name, {})
    min_value = int(treasure.get("min_value", treasure.get("value", 0)))
    max_value = int(treasure.get("max_value", min_value))
    if max_value < min_value:
        max_value = min_value
    return random.randint(min_value, max_value)


def chunk_lines_for_embed(lines, max_chars=1024):
    """Split a list of lines into embed-safe chunks."""
    chunks = []
    current = []
    current_len = 0

    for line in lines:
        line_len = len(line) + (1 if current else 0)  # account for join newline

        # If a single line is somehow too long, hard-split it to stay safe.
        if len(line) > max_chars:
            if current:
                chunks.append("\n".join(current))
                current = []
                current_len = 0

            start = 0
            while start < len(line):
                chunks.append(line[start:start + max_chars])
                start += max_chars
            continue

        if current_len + line_len > max_chars:
            chunks.append("\n".join(current))
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += line_len

    if current:
        chunks.append("\n".join(current))

    return chunks

cooldowns_file = "cooldowns.json"

cooldowns_file = "cooldowns.json"

def load_cooldowns():
    if os.path.exists(cooldowns_file):
        with open(cooldowns_file, "r") as f:
            data = json.load(f)
            cast = {}
            adventure = {}
            net = {}
            dig = {}

            for uid, ts in data.get("cast", {}).items():
                if isinstance(ts, (int, float)):
                    cast[uid] = float(ts)

            for uid, ts in data.get("adventure", {}).items():
                if isinstance(ts, (int, float)):
                    adventure[uid] = float(ts)

            for uid, ts in data.get("net", {}).items():
                if isinstance(ts, (int, float)):
                    net[uid] = float(ts)

            for uid, ts in data.get("dig", {}).items():
                if isinstance(ts, (int, float)):
                    dig[uid] = float(ts)

            return cast, adventure, net, dig
    return {}, {}, {}, {}

def save_cooldowns():
    cast_clean = {uid: float(ts) for uid, ts in cooldowns.items()}
    adventure_clean = {uid: float(ts) for uid, ts in adventure_cooldowns.items()}
    net_clean = {uid: float(ts) for uid, ts in net_cooldowns.items()}
    dig_clean = {uid: float(ts) for uid, ts in dig_cooldowns.items()}

    with open(cooldowns_file, "w") as f:
        json.dump(
            {
                "cast": cast_clean,
                "adventure": adventure_clean,
                "net": net_clean,
                "dig": dig_clean
            }, f)


global cooldowns, adventure_cooldowns, net_cooldowns, dig_cooldowns
cooldowns, adventure_cooldowns, net_cooldowns, dig_cooldowns = load_cooldowns()

bot = commands.Bot(
    command_prefix=case_insensitive_prefix,
    intents=intents,
    help_command=None,
    case_insensitive=True
)

bot_state_file = "bot_state.json"


def load_bot_state():
    if os.path.exists(bot_state_file):
        with open(bot_state_file, "r") as f:
            data = json.load(f)
            lockdown = bool(data.get("lockdown", False))
            allowed_user_id = data.get("allowed_user_id")
            if isinstance(allowed_user_id, str) and allowed_user_id.isdigit():
                allowed_user_id = int(allowed_user_id)
            elif not isinstance(allowed_user_id, int):
                allowed_user_id = None

            return {"lockdown": lockdown, "allowed_user_id": allowed_user_id}

    return {"lockdown": False, "allowed_user_id": None}


def save_bot_state():
    with open(bot_state_file, "w") as f:
        json.dump(bot_state, f)


bot_state = load_bot_state()


@bot.check
async def lockdown_guard(ctx):
    if not bot_state.get("lockdown"):
        return True

    if ctx.author.id == bot_state.get("allowed_user_id"):
        return True

    if await bot.is_owner(ctx.author):
        return True

    await ctx.send("🔒 Bot is in private testing mode right now.")
    return False

users_file = "users.json"

fish_pool = [{
    "name": "fish",
    "emoji": "<:fish:1399192790797127861>",
    "xp": 1,
    "chance": 53.685
}, {
    "name": "chad fish",
    "emoji": "<:chadfish:1399043761413292103>",
    "xp": 20,
    "chance": 9.054
}, {
    "name": "bebeto bass",
    "emoji": "<:bebeto_bass:1399043708879376405>",
    "xp": 35,
    "chance": 7.243
}, {
    "name": "superman shark",
    "emoji": "<:superman_shark:1399164285657022566>",
    "xp": 45,
    "chance": 6.338
}, {
    "name": "benjafish",
    "emoji": "<:benjafish:1399050676063043594>",
    "xp": 60,
    "chance": 4.526
}, {
    "name": "star-fishman",
    "emoji": "<:star_fishman:1478913913805340883>",
    "xp": 60,
    "chance": 4.526
}, {
    "name": "puffer sid",
    "emoji": "<:sid_pufferfish:1399144009175138426>",
    "xp": 69,
    "chance": 3.622
}, {
    "name": "sussy fish",
    "emoji": "<:sussy_fish:1478545128795668540>",
    "xp": 80,
    "chance": 3.622
}, {
    "name": "slamuel sunny",
    "emoji": "<:slamuel_sunny:1399043599445790800>",
    "xp": 90,
    "chance": 2.716
}, {
    "name": "nateinator",
    "emoji": "<:nateinator:1399043897044369440>",
    "xp": 150,
    "chance": 1.811
}, {
    "name": "kermit lefish",
    "emoji": "<:kermit_lefish:1399158630023954452>",
    "xp": 200,
    "chance": 0.905
}, {
    "name": "mojicuslitus",
    "emoji": "<:mojicuslitus:1399194815517688052>",
    "xp": 275,
    "chance": 0.815
}, {
    "name": "bunnie hatchling",
    "emoji": "<:bunnie_hatchling:1478913958823071826>",
    "xp": 420,
    "chance": 0.64
}, {
    "name": "sushi fish",
    "emoji": "<:sushi_fish:1478545129588654190>",
    "xp": 600,
    "chance": 0.397
}, {
    "name": "SUPER RARE LAM CHAD FISH EXTREME",
    "emoji": "<:slam_extreme:1399043820884066344>",
    "xp": 2000,
    "chance": 0.081
}, {
    "name": "fih",
    "emoji": "<:fih:1399044570888671262>",
    "xp": 7500,
    "chance": 0.011
}, {
    "name": "nemo",
    "emoji": "<:nemo:1478545130624647208>",
    "xp": 10000,
    "chance": 0.008
}, {
    "name": "mario judah",
    "emoji": "<:mario_judah:1479711689015300106>",
    "xp": 200000,
    "chance": 0.004
}]

TROPHY_REQUIREMENTS = {
    "fish": 1000,
    "chad fish": 10,
    "bebeto bass": 10,
    "superman shark": 10,
    "benjafish": 10,
    "star-fishman": 10,
    "puffer sid": 10,
    "sussy fish": 10,
    "slamuel sunny": 10,
    "nateinator": 10,
    "kermit lefish": 10,
    "mojicuslitus": 10,
    "bunnie hatchling": 10,
    "sushi fish": 10,
    "SUPER RARE LAM CHAD FISH EXTREME": 5,
    "fih": 1,
    "nemo": 1,
    "mario judah": 1,
}

TROPHY_DISPLAY_NAMES = {
    "SUPER RARE LAM CHAD FISH EXTREME": "SRLCFE",
}

MASTER_OF_THE_SEA_BADGE = {
    "name": "Master of the Sea",
    "emoji": "<:masterofthesea:1479708010766012546>",
}

LEGENDARY_TREASURE_SEEKER_BADGE = {
    "name": "Legendary Treasure Seeker",
    "emoji": "<:legendarytreasureseeker:1479708227791753297>",
}
MASTER_TREASURE_SEEKER_ALIAS = "Master Treasure Seeker"

ONE_PIECE_NAME = "the one piece"

EXCLUDED_TROPHY_TREASURES = {ONE_PIECE_NAME}

TIME_TRAVEL_BASE_COST = 100000
TIME_TRAVEL_COST_STEP = 25000

FISH_TROPHY_INCREMENT_PER_TT = {
    "fish": 250,
    "chad fish": 10,
    "bebeto bass": 10,
    "superman shark": 10,
    "benjafish": 10,
    "star-fishman": 10,
    "puffer sid": 10,
    "sussy fish": 10,
    "slamuel sunny": 10,
    "nateinator": 10,
    "kermit lefish": 10,
    "mojicuslitus": 10,
    "bunnie hatchling": 10,
    "sushi fish": 10,
    "SUPER RARE LAM CHAD FISH EXTREME": 1,
    "fih": 1,
    "nemo": 1,
    "mario judah": 1,
}

TREASURE_TROPHY_REQUIREMENTS_BY_TIER = {
    1: 10,
    2: 10,
    3: 5,
    4: 5,
    5: 1,
    6: 1,
}

rods = {
    "wooden rod": {
        "emoji": "<:wooden_rod:1399044497068920912>",
        "price": 0,
        "bonus": 0.00
    },
    "golden rod": {
        "emoji": "<:golden_rod:1399160694536146954>",
        "price": 750,
        "bonus": 0.10,
    },
    "diamond rod": {
        "emoji": "<:diamond_rod:1399162231962341466>",
        "price": 1500,
        "bonus": 0.20,
    },
    "brick rod": {
        "emoji": "<:brick_rod:1399163039781228607>",
        "price": 3000,
        "bonus": 0.35,
    },
    "the henry fancy rod": {
        "emoji": "<:henry_rod:1399168206412841011>",
        "price": 7500,
        "bonus": 0.50,
    },
    "godly rod": {
        "emoji": "<:godly_rod:1399163746626043946>",
        "price": 12000,
        "bonus": 0.70,
    },
    "tryhard rod": {
        "emoji": "<:tryhard_rod:1399176725283471411>",
        "price": 20000,
        "bonus": 1.00,
    },
    "brumin rod": {
        "emoji": "<:brumin_rod:1478909374964433144>",
        "price": 30000,
        "bonus": 1.25,
    },
    "tilda rod": {
        "emoji": "<:tilda_rod:1478909423169568970>",
        "price": 37500,
        "bonus": 1.50,
    },
    "backwards rod": {
        "emoji": "<:backwards_rod:1478909451724390410>",
        "price": 50000,
        "bonus": 1.75,
    },
    "cupid rod": {
        "emoji": "<:cupid_rod:1478909535845482569>",
        "price": 70000,
        "bonus": 2.00,
        "double_cast_chance": 0.10,
    },
    "deep sea rod": {
        "emoji": "<:deep_sea_rod:1478909563938930878>",
        "price": 70000,
        "bonus": 2.00,
        "treasure_cast_chance": 0.10,
    },
}

boosts = {
    "double cast": {
        "emoji": "<:double_cast:1399044646700716154>",
        "price": 1000,
        "duration": 60 * 60 * 2,
        "description": "Casts twice per 'sq cast' command for 2 hours"
    },
    "autosell": {
        "emoji":
        "<:autosell:1399198067533680741>",
        "price":
        100,
        "duration":
        60 * 60,
        "description":
        "Automatically sell any fish you catch from 'sq cast' for 1 hour"
    },
    "extra love": {
        "emoji": "<:cupid_rod:1478909535845482569>",
        "price": 500,
        "duration": 60 * 60 * 2,
        "description": "Cupid Rod extra-fish chance from 10% → 15% for 2 hours"
    },
    "deeper casts": {
        "emoji": "<:deep_sea_rod:1478909563938930878>",
        "price": 750,
        "duration": 60 * 60 * 2,
        "description": "Deep Sea Rod treasure chance 10%→15% and tier 1-3 → 1-4 for 2 hours"
    }
}

treasure_index = {
    "amber pendant": {
        "emoji": "<:amber_pendant:1400307044514533386>",
        "min_value": 100,
        "max_value": 200,
        "tier": 1
    },
    "ruby ring": {
        "emoji": "<:ruby_ring:1400307346093117624>",
        "min_value": 150,
        "max_value": 300,
        "tier": 1
    },
    "apatite shard": {
        "emoji": "<:apatite_shard:1400306918634819604>",
        "min_value": 300,
        "max_value": 400,
        "tier": 2
    },
    "cobalt gem": {
        "emoji": "<:cobalt_gem:1478545122470789120>",
        "min_value": 400,
        "max_value": 500,
        "tier": 2
    },
    "pearl necklace": {
        "emoji": "<:pearl_necklace:1400306812435300393>",
        "min_value": 500,
        "max_value": 600,
        "tier": 3
    },
    "ruby gem": {
        "emoji": "<:ruby_gem:1478545123922153613>",
        "min_value": 650,
        "max_value": 750,
        "tier": 3
    },
    "ancient vase": {
        "emoji": "<:ancient_vase:1478545127768330342>",
        "min_value": 850,
        "max_value": 950,
        "tier": 3
    },
    "golden chalice": {
        "emoji": "<:golden_chalice:1400306658995081247>",
        "min_value": 1900,
        "max_value": 2100,
        "tier": 4
    },
    "amethyst gem": {
        "emoji": "<:amethyst_gem:1478545125264195718>",
        "min_value": 2350,
        "max_value": 2600,
        "tier": 4
    },
    "glass eye": {
        "emoji": "<:glass_eye:1400306719275487322>",
        "min_value": 3500,
        "max_value": 4500,
        "tier": 5
    },
    "emerald gem": {
        "emoji": "<:emerald_gem:1478545125977231552>",
        "min_value": 4750,
        "max_value": 5250,
        "tier": 5
    },
    "soup dumpling": {
        "emoji": "<:soup_dumpling:1477453212868018450>",
        "min_value": 12500,
        "max_value": 15000,
        "tier": 6
    },
    "golden hook": {
        "emoji": "<:golden_hook:1478915008241864837>",
        "min_value": 5000,
        "max_value": 5500,
        "tier": 5
    },
    "bottle o' rum": {
        "emoji": "<:rum_bottle:1478915109412667413>",
        "min_value": 200,
        "max_value": 250,
        "tier": 1
    },
    "bottle o' flint water": {
        "emoji": "<:flint_water:1478915354897158155>",
        "min_value": 800,
        "max_value": 900,
        "tier": 3
    },
    "crate o' rum": {
        "emoji": "<:rum_crate:1478915492172271798>",
        "min_value": 2400,
        "max_value": 2600,
        "tier": 4
    },
    "skull of cannonball": {
        "emoji": "<:skull_cannonball:1478917065338261644>",
        "min_value": 150,
        "max_value": 200,
        "tier": 1
    },
    "skull of the overboard pirate": {
        "emoji": "<:skull_overboard:1478916126795763908>",
        "min_value": 750,
        "max_value": 900,
        "tier": 3
    },
    "skull of the banished": {
        "emoji": "<:skull_banished:1478915919026585650>",
        "min_value": 850,
        "max_value": 1000,
        "tier": 3
    },
    "skull of wisdom": {
        "emoji": "<:skull_wisdom:1478919962289639595>",
        "min_value": 2100,
        "max_value": 2500,
        "tier": 4
    },
    "ashen skull": {
        "emoji": "<:ashen_skull:1478915638318600202>",
        "min_value": 2500,
        "max_value": 3000,
        "tier": 4
    },
    "skull of betrayal": {
        "emoji": "<:skull_betray:1478919810749300870>",
        "min_value": 6500,
        "max_value": 7500,
        "tier": 5
    },
    "skull of destiny": {
        "emoji": "<:skull_destiny:1478919385841143952>",
        "min_value": 12000,
        "max_value": 13000,
        "tier": 6
    },
    "skull of the golden king": {
        "emoji": "<:skull_king:1478916456141033513>",
        "min_value": 14000,
        "max_value": 16000,
        "tier": 6
    },
    "the one piece": {
        "emoji": "<:one_piece:1479927612104249569>",
        "min_value": 1,
        "max_value": 1,
        "tier": 7,
        "sellable": False
    }
}

chests = {
    "chest": {
        "emoji": "<:chest:1399491916978192406>",
        "rewards": {
            "gold": (50, 100),
            "xp": (75, 150),
            "treasures": {
                "count": (1, 1),
                "max_tier": 2,
                "rarity_bias": 1.9
            }
        },
    },
    "silver chest": {
        "emoji": "<:silver_chest:1399491978835660881>",
        "rewards": {
            "gold": (150, 350),
            "xp": (225, 500),
            "treasures": {
                "count": (1, 2),
                "max_tier": 3,
                "rarity_bias": 1.4
            }
        },
    },
    "ruby chest": {
        "emoji": "<:ruby_chest:1399492078593118239>",
        "rewards": {
            "gold": (425, 750),
            "xp": (525, 775),
            "treasures": {
                "count": (1, 2),
                "max_tier": 4,
                "rarity_bias": 0.9
            }
        },
    },
    "diamond chest": {
        "emoji": "<:diamond_chest:1399492027607027732>",
        "rewards": {
            "gold": (1000, 2000),
            "xp": (1000, 2000),
            "treasures": {
                "count": (2, 2),
                "max_tier": 5,
                "rarity_bias": 0.5
            }
        },
    },
    "godly chest": {
        "emoji": "<:godly_chest:1399492135769739336>",
        "rewards": {
            "gold": (2500, 3500),
            "xp": (2500, 3500),
            "treasures": {
                "count": (2, 3),
                "max_tier": 6,
                "rarity_bias": 0.3
            }
        },
    },
    "deep sea chest": {
        "emoji": "<:deep_sea_chest:1479889415374377161>",
        "rewards": {
            "gold": (5000, 9000),
            "xp": (5000, 9000),
            "treasures": {
                "count": (3, 3),
                "max_tier": 6,
                "rarity_bias": 0.18
            },
            "one_piece_chance": 0.01
        },
    },
}

baits = {
    "worms": {
        "emoji": "<:worm_bait:1477701918573990030>",
        "price": 100,
        "multiplier": 1.02,
        "singular": "worm"
    },
    "leeches": {
        "emoji": "<:leech_bait:1477701943483957431>",
        "price": 250,
        "multiplier": 1.04,
        "singular": "leech"
    },
    "ramen noodles": {
        "emoji": "<:ramen_bait:1478547233220595844>",
        "price": 350,
        "multiplier": 1.06,
        "singular": "ramen noodle"
    },
    "trippa snippas": {
        "emoji": "<:trippa_snippa_bait:1477701970063134850>",
        "price": 500,
        "multiplier": 1.08,
        "singular": "trippa snippa"
    }
}

treasure_index.update({
    #"red gem": {"emoji": "<:red_gem:1400305184525258926>", "value": 100, "tier": 3},
    #"green gem": {"emoji": "<:green_gem:1400305261578817637>", "value": 120, "tier": 3},
    #"blue gem": {"emoji": "<:blue_gem:1400305224131805226>", "value": 140, "tier": 4},
    #"purple gem": {"emoji": "<:purple_gem:1400305310823878786>", "value": 160, "tier": 5},
})


def load_users():
    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            return json.load(f)
    return {}


def save_users():
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)


users = load_users()


def get_user_data(user):
    global users
    uid = str(user.id)

    if uid not in users:
        users[uid] = {
            "xp": 0,
            "gold": 0,
            "level": 1,
            "inventory": {},
            "rods": {
                "wooden rod": 1
            },
            "rod": "wooden rod",
            "total_fish": 0,
            "boosts": {},
            "chests": {},
            "treasures": {},
            "bait": None,
            "bait_uses": 0,
            "bait_amount": 0,
            "fish_bowl": None,
            "trophy_room": [],
            "treasure_trophy_room": {},
            "badges": [],
            "time_travels": 0,
            "contract": None,
            "contracts_meta": {},
            "tt_confirm": 0,
        }
    else:

        if "chests" not in users[uid]:
            users[uid]["chests"] = {}
        if "treasures" not in users[uid]:
            users[uid]["treasures"] = {}
        if "bait_amount" not in users[uid]:
            users[uid]["bait_amount"] = 0
        if "fish_bowl" not in users[uid]:
            users[uid]["fish_bowl"] = None
        if "trophy_room" not in users[uid]:
            users[uid]["trophy_room"] = []
        if "treasure_trophy_room" not in users[uid]:
            users[uid]["treasure_trophy_room"] = {}


    save_users()
    return users[uid]


def normalize_trophy_room(user_data):
    """Convert old trophy room list format into a count dictionary."""
    trophy_room = user_data.get("trophy_room", {})

    if isinstance(trophy_room, list):
        converted = {}
        for fish_name in trophy_room:
            converted[fish_name] = converted.get(fish_name, 0) + 1
        trophy_room = converted
        user_data["trophy_room"] = trophy_room

    if not isinstance(trophy_room, dict):
        trophy_room = {}
        user_data["trophy_room"] = trophy_room

    return trophy_room


def normalize_treasure_trophy_room(user_data):
    room = user_data.get("treasure_trophy_room", {})
    if not isinstance(room, dict):
        room = {}
        user_data["treasure_trophy_room"] = room
    return room


def has_badge(user_data, badge_name):
    return badge_name in user_data.get("badges", [])


def grant_badge(user_data, badge_name):
    badges = user_data.setdefault("badges", [])
    if badge_name not in badges:
        badges.append(badge_name)
        return True
    return False


def get_cast_cooldown_seconds(user_data):
    return 22 if has_badge(user_data, MASTER_OF_THE_SEA_BADGE["name"]) else 30


def get_net_cooldown_seconds(user_data):
    return 45 * 60 if has_badge(user_data, MASTER_OF_THE_SEA_BADGE["name"]) else 60 * 60


def get_adventure_cooldown_seconds(user_data):
    return 90 * 60 if has_badge(user_data, LEGENDARY_TREASURE_SEEKER_BADGE["name"]) else 120 * 60


def get_rare_fish_multiplier(user_data):
    return 1.0 + (0.10 * int(user_data.get("time_travels", 0)))


def get_level_info(xp):
    level = 1
    required_xp = 100
    while xp >= required_xp:
        xp -= required_xp
        level += 1
        required_xp = 100 * level
    return level, xp, required_xp

def get_fishbowl_multiplier(user_data):
    """
    Returns a multiplier (>1) that boosts rare fish odds based on the fish in the bowl.
    Lower 'chance' fish = bigger boost.
    """
    bowl = normalize_fish_bowl(user_data)
    fish_entries = bowl.get("fish", [])
    if not fish_entries:
        return 1.0

    total_bonus = 0.0
    for entry in fish_entries:
        fish_name = entry.get("fish")
        fish = next((f for f in fish_pool if f["name"] == fish_name), None)
        if fish:
            total_bonus += fishbowl_fish_bonus(float(fish.get("chance", 0))) - 1.0

    # Cap overall fish bowl bonus at +30% (e.g. 10 nemos in bowl).
    return min(1.30, 1.0 + total_bonus)


def fishbowl_fish_bonus(c):
    # Stronger boosts for rarer bowl fish, with diminishing value for common fish.
    # Tuned so 10x nemo (0.008%) gives +30% total odds boost.
    nemo_chance = 0.008
    chance = max(float(c), nemo_chance)
    rarity_ratio = (nemo_chance / chance)**0.5
    bonus_percent = 0.03 * rarity_ratio
    return 1.0 + bonus_percent


def normalize_fish_bowl(user_data):
    bowl = user_data.get("fish_bowl")

    # Old format: {"fish": "name", "nick": "nickname"}
    if bowl is None:
        normalized = {"slots": 1, "fish": []}
    elif isinstance(bowl, dict) and "slots" not in bowl and isinstance(bowl.get("fish"), str):
        fish_name = bowl.get("fish")
        nick = bowl.get("nick") or "Unnamed"
        entries = [{"fish": fish_name, "nick": nick}] if fish_name else []
        normalized = {"slots": 1, "fish": entries}
    elif isinstance(bowl, dict):
        slots = int(bowl.get("slots", 1) or 1)
        slots = max(1, min(10, slots))
        entries = []
        for entry in bowl.get("fish", []):
            if not isinstance(entry, dict):
                continue
            fish_name = entry.get("fish")
            nick = (entry.get("nick") or "Unnamed").strip()
            if fish_name and nick:
                entries.append({"fish": fish_name, "nick": nick})
        normalized = {"slots": slots, "fish": entries[:slots]}
    else:
        normalized = {"slots": 1, "fish": []}

    user_data["fish_bowl"] = normalized
    return normalized


def rarity_weight(base_chance, rarity_mult):
    """
    Turns your base chance into a weight that increases odds of rarer fish
    when rarity_mult > 1.0.
    """
    base_chance = max(float(base_chance), 0.000001)
    rarity_mult = max(float(rarity_mult), 1.0)

    # Inverse-weight method:
    # rarer fish (lower chance) get boosted more as rarity_mult increases
    return (1.0 / base_chance) ** (rarity_mult - 1.0)


def build_personal_fish_odds(user_data):
    """
    Build per-fish catch odds after personal rare-fish modifiers.
    Rods are intentionally excluded from rare-fish weighting.
    """
    rarity_mult = 1.0

    if user_data.get("bait") and user_data.get("bait_uses", 0) > 0:
        bait_name = user_data["bait"]
        rarity_mult *= float(baits[bait_name]["multiplier"])

    rarity_mult *= get_fishbowl_multiplier(user_data)
    rarity_mult *= get_rare_fish_multiplier(user_data)

    weights = []
    for f in fish_pool:
        base = f["chance"]
        weights.append(base * rarity_weight(base, rarity_mult))

    total_weight = sum(weights) or 1.0
    return [(fish, (weight / total_weight) * 100.0) for fish, weight in zip(fish_pool, weights)]


def choose_treasures(max_tier, count_range, rarity_bias):
    # Filter treasures by max tier
    eligible = [
        name for name, info in treasure_index.items()
        if info["tier"] <= max_tier
    ]
    count = random.randint(*count_range)
    selected = []

    # Calculate weights so higher tier = rarer (lower weight)
    weights = []
    for name in eligible:
        tier = treasure_index[name]["tier"]
        # Weight inversely proportional to tier ^ rarity_bias
        weight = 1 / (tier**rarity_bias)
        weights.append(weight)

    for _ in range(count):
        chosen = random.choices(eligible, weights=weights, k=1)[0]
        selected.append(chosen)

    return selected


def choose_equal_tier_treasure(min_tier, max_tier):
    eligible_tiers = [
        tier for tier in range(min_tier, max_tier + 1)
        if any(info["tier"] == tier for info in treasure_index.values())
    ]
    if not eligible_tiers:
        return None

    chosen_tier = random.choice(eligible_tiers)
    tier_items = [
        name for name, info in treasure_index.items() if info["tier"] == chosen_tier
    ]
    if not tier_items:
        return None
    return random.choice(tier_items)


def roll_fish():
    roll = random.uniform(0, 100)
    total = 0
    for fish in fish_pool:
        total += fish["chance"]
        if roll <= total:
            return fish
    return fish_pool[0]


save_users()


def has_boost(user_data, boost_name):
    if boost_name in user_data.get("boosts", {}):
        try:
            boost_time = float(user_data["boosts"][boost_name])
            return time.time() < boost_time
        except (ValueError, TypeError):
            # If the value in JSON is corrupted, remove the boost
            del user_data["boosts"][boost_name]
            return False
    return False

def make_contract_catalog_for_user(user_data, user_id=None):
    now_est = datetime.now(ZoneInfo("America/New_York"))
    slot_hour = (now_est.hour // 6) * 6
    rotation = now_est.replace(hour=slot_hour, minute=0, second=0, microsecond=0)
    user_seed_id = str(user_id if user_id is not None else user_data.get("user_id", "anon"))
    seed = (
        f"{rotation.isoformat()}:{user_seed_id}:"
        f"{int(user_data.get('time_travels', 0))}:{user_data.get('level', 1)}"
    )
    rng = random.Random(seed)

    fish_by_xp = sorted(fish_pool, key=lambda f: int(f.get("xp", 0)))
    slamuel_sunny = next((f for f in fish_pool if f.get("name") == "slamuel sunny"), None)
    max_contract_rarity = float(slamuel_sunny.get("chance", 0)) if slamuel_sunny else 0.0
    bait_by_price = sorted(baits.keys(), key=lambda name: int(baits[name].get("price", 0)))

    def pick_fish(min_xp, max_xp):
        pool = [
            f["name"]
            for f in fish_by_xp
            if min_xp <= int(f.get("xp", 0)) <= max_xp
            and float(f.get("chance", 0)) >= max_contract_rarity
        ]
        if not pool:
            pool = [f["name"] for f in fish_by_xp if float(f.get("chance", 0)) >= max_contract_rarity]
        return rng.choice(pool)

    def pick_bait(min_price, max_price):
        pool = [name for name in bait_by_price if min_price <= int(baits[name].get("price", 0)) <= max_price]
        if not pool:
            pool = bait_by_price
        return rng.choice(pool)

    contract_scoring = {
        "difficulty": {
            "A": (8, 14),
            "B": (18, 28),
            "C": (28, 44),
        },
        "reward": {
            "A": (6, 14),
            "B": (12, 22),
            "C": (18, 30),
            "max_spread_per_tier": 4,
        },
    }

    chest_reward_scores = {
        "chest": 4,
        "silver chest": 6,
        "ruby chest": 8,
        "diamond chest": 10,
        "deep sea chest": 12,
    }

    fish_index = {fish["name"]: fish for fish in fish_pool}

    def clamp_score_range(min_score, max_score):
        if max_score < min_score:
            max_score = min_score
        return min_score, max_score

    def estimate_goal_difficulty(goal):
        goal_type = goal.get("type")
        target = int(goal.get("target", 0))

        if goal_type == "cast":
            return target * 0.7

        if goal_type == "dig_bait":
            return target * 1.2

        if goal_type == "dig_specific_bait":
            bait_name = goal.get("bait", "")
            bait_price = int(baits.get(bait_name, {}).get("price", 0))
            bait_factor = 1.0 + min(1.0, bait_price / 500)
            return target * 1.1 * bait_factor

        if goal_type == "catch_fish":
            fish_name = goal.get("fish", "")
            fish_info = fish_index.get(fish_name, {})
            fish_xp = int(fish_info.get("xp", 1))
            rarity = float(fish_info.get("chance", 100))
            rarity_factor = 1.0 + min(2.0, (100 - rarity) / 100)
            xp_factor = 1.0 + min(1.2, fish_xp / 100)
            return target * rarity_factor * xp_factor

        if goal_type == "sell_treasure":
            return target * 1.5

        return float(target)

    def estimate_reward_score(reward):
        total = 0.0

        for chest_name, amount in reward.get("chests", {}).items():
            total += chest_reward_scores.get(chest_name, 5) * int(amount)

        for bait_name, amount in reward.get("baits", {}).items():
            bait_price = int(baits.get(bait_name, {}).get("price", 0))
            total += max(1.0, bait_price / 100) * int(amount)

        for treasure_name, amount in reward.get("treasures", {}).items():
            treasure = treasure_index.get(treasure_name, {})
            treasure_tier = int(treasure.get("tier", 1))
            total += (treasure_tier * 2) * int(amount)

        return total

    def score_in_range(score, score_range):
        min_score, max_score = clamp_score_range(score_range[0], score_range[1])
        return min_score <= score <= max_score

    def estimate_contract_reward_value(reward):
        total = 0.0

        for chest_name, amount in reward.get("chests", {}).items():
            chest = chests.get(chest_name, {})
            rewards_cfg = chest.get("rewards", {})
            gold_min, gold_max = rewards_cfg.get("gold", (0, 0))
            xp_min, xp_max = rewards_cfg.get("xp", (0, 0))

            chest_value = ((gold_min + gold_max) / 2) + ((xp_min + xp_max) / 2)

            treasure_cfg = rewards_cfg.get("treasures")
            if treasure_cfg:
                min_count, max_count = treasure_cfg.get("count", (0, 0))
                avg_count = (min_count + max_count) / 2
                max_tier = int(treasure_cfg.get("max_tier", 0))
                possible_values = []
                for info in treasure_index.values():
                    if int(info.get("tier", 0)) <= max_tier:
                        min_value = int(info.get("min_value", info.get("value", 0)))
                        max_value = int(info.get("max_value", min_value))
                        possible_values.append((min_value + max_value) / 2)
                if possible_values:
                    chest_value += avg_count * (sum(possible_values) / len(possible_values))

            total += chest_value * int(amount)

        for bait_name, amount in reward.get("baits", {}).items():
            total += int(baits.get(bait_name, {}).get("price", 0)) * int(amount)

        for treasure_name, amount in reward.get("treasures", {}).items():
            info = treasure_index.get(treasure_name, {})
            min_value = int(info.get("min_value", info.get("value", 0)))
            max_value = int(info.get("max_value", min_value))
            total += ((min_value + max_value) / 2) * int(amount)

        return total

    def build_contract_reward(label):
        chest_options = {
            "A": ["chest", "silver chest"],
            "B": ["silver chest", "ruby chest"],
            "C": ["ruby chest", "diamond chest"],
        }
        treasure_drop_chance = {
            "A": 0.70,
            "B": 1.00,
            "C": 1.00,
        }
        treasure_tier_caps = {
            "A": 2,
            "B": 3,
            "C": 4,
        }
        treasure_count_ranges = {
            "A": (1, 2),
            "B": (1, 3),
            "C": (2, 4),
        }
        reward = {
            "chests": {rng.choice(chest_options[label]): 1},
            "baits": {},
            "treasures": {},
        }

        if rng.random() < 0.45:
            bait_pool = list(baits.keys())
            for bait_name in rng.sample(bait_pool, k=rng.randint(1, 2)):
                reward["baits"][bait_name] = rng.randint(1, 3)

        if rng.random() < treasure_drop_chance[label]:
            max_tier = treasure_tier_caps[label]
            tier_pool = [
                name for name, info in treasure_index.items()
                if int(info.get("tier", 0)) <= max_tier
            ]
            if tier_pool:
                min_count, max_count = treasure_count_ranges[label]
                treasure_pick_count = rng.randint(min_count, max_count)
                for treasure_name in rng.sample(tier_pool, k=min(len(tier_pool), treasure_pick_count)):
                    reward["treasures"][treasure_name] = rng.randint(1, 2)

        # Keep contract rewards visibly tied to contract tier by guaranteeing
        # at least one treasure on higher tiers.
        if label in {"B", "C"} and not reward["treasures"]:
            guaranteed_pool = [
                name for name, info in treasure_index.items()
                if int(info.get("tier", 0)) <= treasure_tier_caps[label]
            ]
            if guaranteed_pool:
                reward["treasures"][rng.choice(guaranteed_pool)] = 1

        return reward

    def build_goal_for_tier(label):
        # Each tier gets random goal types, but with difficulty scaled by tier.
        # "Cast X times" goals are intentionally less common to avoid overly easy rolls.
        weighted_options = {
            "A": [
                ({"type": "cast", "target": rng.randint(8, 14)}, 1),
                ({"type": "catch_fish", "fish": pick_fish(1, 45), "target": rng.randint(2, 5)}, 2),
                ({"type": "dig_bait", "target": rng.randint(3, 5)}, 2),
                ({"type": "dig_specific_bait", "bait": pick_bait(100, 250), "target": rng.randint(2, 4)}, 2),
            ],
            "B": [
                ({"type": "cast", "target": rng.randint(24, 38)}, 1),
                ({"type": "catch_fish", "fish": pick_fish(35, 95), "target": rng.randint(3, 7)}, 2),
                ({"type": "dig_bait", "target": rng.randint(5, 7)}, 2),
                ({"type": "dig_specific_bait", "bait": pick_bait(250, 350), "target": rng.randint(3, 6)}, 2),
            ],
            "C": [
                ({"type": "cast", "target": rng.randint(40, 60)}, 1),
                ({"type": "catch_fish", "fish": pick_fish(80, 1000), "target": rng.randint(4, 9)}, 2),
                ({"type": "dig_bait", "target": rng.randint(6, 10)}, 2),
                ({"type": "dig_specific_bait", "bait": pick_bait(350, 500), "target": rng.randint(4, 8)}, 2),
            ],
        }
        goals, weights = zip(*weighted_options[label])
        return rng.choices(goals, weights=weights, k=1)[0]

    def build_scored_goal(label, attempts=120):
        min_score, max_score = contract_scoring["difficulty"][label]
        fallback_goal = build_goal_for_tier(label)
        fallback_score = estimate_goal_difficulty(fallback_goal)

        for _ in range(attempts):
            goal = build_goal_for_tier(label)
            score = estimate_goal_difficulty(goal)
            fallback_goal, fallback_score = goal, score
            if score_in_range(score, (min_score, max_score)):
                return goal, score

        return fallback_goal, fallback_score

    def build_scored_reward(label, attempts=120):
        min_score, max_score = contract_scoring["reward"][label]
        fallback_reward = build_contract_reward(label)
        fallback_score = estimate_reward_score(fallback_reward)

        for _ in range(attempts):
            reward = build_contract_reward(label)
            score = estimate_reward_score(reward)
            fallback_reward, fallback_score = reward, score
            if score_in_range(score, (min_score, max_score)):
                return reward, score

        return fallback_reward, fallback_score

    templates = {
        "A": {
            "label": "A",
            "price": 500,
            "goal": None,
            "reward": None,
        },
        "B": {
            "label": "B",
            "price": 1000,
            "goal": None,
            "reward": None,
        },
        "C": {
            "label": "C",
            "price": 2000,
            "goal": None,
            "reward": None,
        },
    }

    contract_scores = {
        "A": {"difficulty": 0.0, "reward": 0.0},
        "B": {"difficulty": 0.0, "reward": 0.0},
        "C": {"difficulty": 0.0, "reward": 0.0},
    }

    for label in ("A", "B", "C"):
        goal, difficulty_score = build_scored_goal(label)
        reward, reward_score = build_scored_reward(label)
        templates[label]["goal"] = goal
        templates[label]["reward"] = reward
        contract_scores[label]["difficulty"] = difficulty_score
        contract_scores[label]["reward"] = reward_score

    def reroll_goal(label):
        goal, difficulty_score = build_scored_goal(label)
        templates[label]["goal"] = goal
        contract_scores[label]["difficulty"] = difficulty_score

    def reroll_reward(label):
        reward, reward_score = build_scored_reward(label)
        templates[label]["reward"] = reward
        contract_scores[label]["reward"] = reward_score

    # Keep A <= B <= C for both hidden difficulty and reward scores.
    # Also cap adjacent reward jumps to avoid runaway value spikes.
    max_reward_spread = contract_scoring["reward"].get("max_spread_per_tier", 4)
    for _ in range(180):
        a_diff = contract_scores["A"]["difficulty"]
        b_diff = contract_scores["B"]["difficulty"]
        c_diff = contract_scores["C"]["difficulty"]

        a_reward_score = contract_scores["A"]["reward"]
        b_reward_score = contract_scores["B"]["reward"]
        c_reward_score = contract_scores["C"]["reward"]

        rerolled = False

        if a_diff > b_diff:
            reroll_goal("A")
            rerolled = True
        if b_diff > c_diff:
            reroll_goal("B")
            rerolled = True

        if a_reward_score > b_reward_score:
            reroll_reward("A")
            rerolled = True
        if b_reward_score > c_reward_score:
            reroll_reward("B")
            rerolled = True

        if (b_reward_score - a_reward_score) > max_reward_spread:
            reroll_reward("B")
            rerolled = True
        if (c_reward_score - b_reward_score) > max_reward_spread:
            reroll_reward("C")
            rerolled = True

        if not rerolled:
            break

    # Preserve the existing economic estimate guardrail as a final safety net.
    for _ in range(100):
        a_value = estimate_contract_reward_value(templates["A"]["reward"])
        b_value = estimate_contract_reward_value(templates["B"]["reward"])
        c_value = estimate_contract_reward_value(templates["C"]["reward"])

        rerolled = False
        if a_value > b_value:
            reroll_reward("A")
            rerolled = True
        if b_value > c_value:
            reroll_reward("B")
            rerolled = True

        if not rerolled:
            break

    return rotation.timestamp(), templates


def format_contract_goal(goal):
    goal_type = goal.get("type")
    if goal_type == "cast":
        return f"Cast {goal['target']} times"
    if goal_type == "dig_bait":
        return f"Find {goal['target']} bait from digging"
    if goal_type == "dig_specific_bait":
        bait_name = goal.get("bait", "bait")
        bait_label = format_bait_name(bait_name, goal['target']) if bait_name in baits else bait_name.title()
        return f"Find {goal['target']} {baits.get(bait_name, {}).get('emoji', '')} {bait_label} from digging"
    if goal_type == "catch_fish":
        fish = next((f for f in fish_pool if f["name"] == goal["fish"]), None)
        fish_txt = f"{fish['emoji']} {goal['fish'].title()}" if fish else goal['fish'].title()
        return f"Catch {goal['target']} {fish_txt}"
    if goal_type == "sell_treasure":
        return f"Sell {goal['target']} treasures"
    return "Unknown"


def format_contract_reward(reward):
    if not reward:
        return "No reward"

    parts = []

    for chest_name, amount in reward.get("chests", {}).items():
        emoji = chests.get(chest_name, {}).get("emoji", "")
        parts.append(f"{emoji} {amount} {chest_name.title()}")

    for bait_name, amount in reward.get("baits", {}).items():
        emoji = baits.get(bait_name, {}).get("emoji", "")
        parts.append(f"{emoji} {amount} {format_bait_name(bait_name, amount)}")

    for treasure_name, amount in reward.get("treasures", {}).items():
        emoji = treasure_index.get(treasure_name, {}).get("emoji", "")
        parts.append(f"{emoji} {amount} {treasure_name.title()}")

    return " + ".join(parts) if parts else "No reward"


def update_contract_progress(user_data, event_type, amount=1, fish_name=None):
    contract = user_data.get("contract")
    if not contract:
        return

    if time.time() > float(contract.get("expires_at", 0)):
        user_data["contract"] = None
        return

    goal = contract.get("goal", {})
    progress = int(contract.get("progress", 0))

    if goal.get("type") == "cast" and event_type == "cast":
        progress += amount
    elif goal.get("type") == "dig_bait" and event_type == "dig_bait":
        progress += amount
    elif goal.get("type") == "dig_specific_bait" and event_type == "dig_specific_bait" and fish_name == goal.get("bait"):
        progress += amount
    elif goal.get("type") == "sell_treasure" and event_type == "sell_treasure":
        progress += amount
    elif goal.get("type") == "catch_fish" and event_type == "catch_fish" and fish_name == goal.get("fish"):
        progress += amount
    else:
        return None

    contract["progress"] = progress
    if progress >= int(goal.get("target", 1)):
        reward = contract.get("reward", {})

        for chest_name, amount in reward.get("chests", {}).items():
            user_data.setdefault("chests", {})[chest_name] = int(user_data.setdefault("chests", {}).get(chest_name, 0)) + int(amount)

        inventory = user_data.setdefault("inventory", {})
        for bait_name, amount in reward.get("baits", {}).items():
            inventory[bait_name] = int(inventory.get(bait_name, 0)) + int(amount)

        treasures = user_data.setdefault("treasures", {})
        for treasure_name, amount in reward.get("treasures", {}).items():
            treasures[treasure_name] = int(treasures.get(treasure_name, 0)) + int(amount)

        # Backward compatibility for contracts accepted before this update.
        reward_gold = int(contract.get("reward_gold", 0))
        if reward_gold > 0:
            user_data["gold"] = int(user_data.get("gold", 0)) + reward_gold

        completion = {
            "label": contract.get("label", "?"),
            "goal": goal,
            "reward": reward,
        }

        user_data["contract"] = None
        return completion

    return None


async def send_contract_completion_embed(ctx, completion):
    if not completion:
        return

    embed = discord.Embed(
        title="✅ Contract Complete!",
        color=discord.Color.green(),
        description=(
            f"{ctx.author.display_name} completed contract **{completion.get('label', '?')}**.\n"
            f"Goal: {format_contract_goal(completion.get('goal', {}))}"
        )
    )
    embed.add_field(
        name="Rewards Granted",
        value=format_contract_reward(completion.get("reward", {})),
        inline=False
    )
    await ctx.send(embed=embed)


@bot.command()
async def dig(ctx):
    user_id = str(ctx.author.id)
    user_data = get_user_data(ctx.author)
    now = time.time()

    # ⏳ Cooldown check (10 minutes)
    if user_id in dig_cooldowns and now - dig_cooldowns[user_id] < 600:
        remaining = 600 - (now - dig_cooldowns[user_id])
        await ctx.send(
            f"🕓 You must wait {format_duration(remaining)} before digging again."
        )
        return

    dig_cooldowns[user_id] = now
    save_cooldowns()

    # 🎯 Roll main outcome
    outcomes = ["nothing", "worms", "leeches", "ramen noodles", "trippa snippas"]
    weights = [30, 35, 18, 11, 6]
    result = random.choices(outcomes, weights=weights, k=1)[0]

    # 💀 Dirt outcome
    if result == "nothing":
        await ctx.send(f"{ctx.author.display_name} dug up... **dirt!** 💀")
        return

    inv = user_data.setdefault("inventory", {})

    # Always give 1 bait from main roll
    first = result
    inv[first] = inv.get(first, 0) + 1

    # 🎯 50% chance to get a second bait (can be same or different)
    got_second = random.random() < 0.5
    second = None

    if got_second:
        second = random.choice(["worms", "leeches", "ramen noodles", "trippa snippas"])
        inv[second] = inv.get(second, 0) + 1

    completion = update_contract_progress(user_data, "dig_bait", 2 if got_second else 1)
    if first:
        completion = completion or update_contract_progress(user_data, "dig_specific_bait", 1, first)
    if second:
        completion = completion or update_contract_progress(user_data, "dig_specific_bait", 1, second)
    save_users()

    # 📦 Message formatting
    if got_second:
        message = (
            f"<:dig_shovel:1477878571057020938> {ctx.author.display_name} dug up a "
            f"{baits[first]['emoji']} **{format_bait_name(first, 1)}** and a"
            f"{baits[second]['emoji']} **{format_bait_name(second, 1)}**!"
        )
    else:
        message = (
            f"<:dig_shovel:1477878571057020938> {ctx.author.display_name} dug up a "
            f"{baits[first]['emoji']} **{format_bait_name(first, 1)}**!"
        )

    await ctx.send(message)
    await send_contract_completion_embed(ctx, completion)

@bot.group(invoke_without_command=True)
async def fish(ctx):
    await ctx.send(
        "Use `sq fish bowl` to view, `sq fish bowl <fish> <nickname>` to add, "
        "or `sq fish bowl remove <fish nickname>` to remove."
    )


@fish.command(name="bowl")
async def fish_bowl(ctx, *, args: str = None):
    user_data = get_user_data(ctx.author)
    inv = user_data.setdefault("inventory", {})
    bowl = normalize_fish_bowl(user_data)

    # VIEW current bowl
    if not args:
        fish_entries = bowl.get("fish", [])
        if not fish_entries:
            await ctx.send("Your fish bowl is empty. Use `sq fish bowl <fish> <nickname>`.")
            return

        mult = get_fishbowl_multiplier(user_data)
        percent = int(round((mult - 1) * 100))
        lines = []
        for i in range(bowl.get("slots", 1)):
            if i < len(fish_entries):
                entry = fish_entries[i]
                fish_obj = next((f for f in fish_pool if f["name"] == entry.get("fish")), None)
                if fish_obj:
                    lines.append(f"`{i + 1}.` {fish_obj['emoji']} **{entry.get('nick', 'Unnamed')}**")
                else:
                    lines.append(f"`{i + 1}.` ❓ **Unknown Fish**")
            else:
                lines.append(f"`{i + 1}.` ▫️ *Empty slot*")

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Fishbowl",
            description="\n".join(lines) + f"\n\n+{percent}% Rare Fish Odds",
            color=discord.Color.from_rgb(255, 255, 255)
        )
        embed.set_footer(text=f"Slots Used: {len(fish_entries)}/{bowl.get('slots', 1)}")
        await ctx.send(embed=embed)
        return

    raw = args.strip()
    if raw.lower().startswith("remove "):
        target_nick = raw[7:].strip().lower()
        if not target_nick:
            await ctx.send("❌ Format: `sq fish bowl remove <fish nickname>`")
            return

        fish_entries = bowl.get("fish", [])
        for i, entry in enumerate(fish_entries):
            if (entry.get("nick") or "").strip().lower() == target_nick:
                removed = fish_entries.pop(i)
                fish_name = removed.get("fish")
                if fish_name:
                    inv[fish_name] = inv.get(fish_name, 0) + 1
                save_users()
                await ctx.send(f"✅ Removed **{removed.get('nick', 'Unnamed')}** from your fish bowl.")
                return

        await ctx.send("❌ No fish in your bowl has that nickname.")
        return

    parts = args.split()
    if len(parts) < 2:
        await ctx.send("❌ Format: `sq fish bowl <fish> <nickname>`")
        return

    # Find the fish name by taking the longest prefix that matches a fish name
    args = " ".join(args.split())
    lower = args.lower()
    chosen_fish = None
    chosen_nick = ""

    # Try longest-first match against fish_pool names
    fish_names = sorted([f["name"] for f in fish_pool], key=len, reverse=True)
    for fname in fish_names:
        fname_l = fname.lower()
        if lower.startswith(fname_l + " "):
            chosen_fish = fname
            chosen_nick = args[len(fname):].strip()  # slice original args using original length
            break

    if not chosen_fish or not chosen_nick:
        await ctx.send("❌ That fish doesn’t exist, or you forgot the nickname.")
        return

    if len(bowl.get("fish", [])) >= bowl.get("slots", 1):
        await ctx.send("❌ Your fish bowl is full. Buy more slots in `sq shop`.")
        return

    # Must own the fish in inventory to put it in bowl
    if inv.get(chosen_fish, 0) < 1:
        await ctx.send("❌ You don’t have that fish in your inventory.")
        return

    # Move 1 fish into the bowl
    inv[chosen_fish] -= 1
    if inv[chosen_fish] <= 0:
        del inv[chosen_fish]

    bowl["fish"].append({"fish": chosen_fish, "nick": chosen_nick})
    mult = get_fishbowl_multiplier(user_data)
    percent = int(round((mult - 1) * 100))

    embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Fishbowl",
        description=(
            f"Added **{chosen_nick}** to your bowl.\n"
            f"Slots Used: {len(bowl.get('fish', []))}/{bowl.get('slots', 1)}\n"
            f"+{percent}% Rare Fish Odds"
        ),
        color=discord.Color.from_rgb(255, 255, 255)
    )

    save_users()
    await ctx.send(embed=embed)


@bot.group(name="trophy", aliases=["tr"], invoke_without_command=True)
async def trophy_room(ctx):
    await send_trophy_room(ctx)


@trophy_room.command(name="room")
async def trophy_room_view(ctx):
    await send_trophy_room(ctx)


@bot.command(name="trophyroom", aliases=["trroom", "trophy-room"])
async def trophy_room_direct(ctx):
    """Fallback direct command in case grouped subcommands fail to route."""
    await send_trophy_room(ctx)


def get_fish_trophy_requirement(fish_name, user_data):
    base_amount = int(TROPHY_REQUIREMENTS.get(fish_name, 1))
    increment = int(FISH_TROPHY_INCREMENT_PER_TT.get(fish_name, 0))
    time_travels = int(user_data.get("time_travels", 0))
    return base_amount + (increment * time_travels)


def get_treasure_trophy_requirements(user_data):
    req = {}
    for name, info in treasure_index.items():
        if name in EXCLUDED_TROPHY_TREASURES:
            continue
        tier = int(info.get("tier", 0))
        req[name] = int(TREASURE_TROPHY_REQUIREMENTS_BY_TIER.get(tier, 1))
    return req


async def send_trophy_room(ctx):
    user_data = get_user_data(ctx.author)
    fish_collected = normalize_trophy_room(user_data)
    treasure_collected = normalize_treasure_trophy_room(user_data)

    fish_completed = all(
        int(fish_collected.get(f["name"], 0)) >= get_fish_trophy_requirement(f["name"], user_data)
        for f in fish_pool
    )
    if fish_completed:
        grant_badge(user_data, MASTER_OF_THE_SEA_BADGE["name"])

    treasure_requirements = get_treasure_trophy_requirements(user_data)
    treasure_completed = all(
        int(treasure_collected.get(name, 0)) >= needed
        for name, needed in treasure_requirements.items()
    ) if treasure_requirements else False
    if treasure_completed:
        grant_badge(user_data, LEGENDARY_TREASURE_SEEKER_BADGE["name"])
        grant_badge(user_data, MASTER_TREASURE_SEEKER_ALIAS)

    save_users()

    def split_embed_lines(lines, max_length=1024):
        chunks = []
        current = []
        current_length = 0

        for line in lines:
            line_length = len(line) + (1 if current else 0)
            if current and current_length + line_length > max_length:
                chunks.append("\n".join(current))
                current = [line]
                current_length = len(line)
            else:
                current.append(line)
                current_length += line_length

        if current:
            chunks.append("\n".join(current))

        return chunks or ["No entries yet."]

    def build_fish_embed():
        normal_fish_lines = []
        specialty_fish_lines = []

        specialty_fish_names = {
            "SUPER RARE LAM CHAD FISH EXTREME",
            "fih",
            "nemo",
            "mario judah",
        }

        for fish in fish_pool:
            fish_name = fish["name"]
            needed = get_fish_trophy_requirement(fish_name, user_data)
            count = int(fish_collected.get(fish_name, 0))
            count = max(0, min(count, needed))
            marker = "✅" if count >= needed else "⬜"
            display_name = TROPHY_DISPLAY_NAMES.get(fish_name, fish_name.title())
            line = f"{marker} {fish['emoji']} **{display_name}** ({count}/{needed})"

            if fish_name in specialty_fish_names:
                specialty_fish_lines.append(line)
            else:
                normal_fish_lines.append(line)

        total_needed = sum(get_fish_trophy_requirement(f["name"], user_data) for f in fish_pool)
        total_collected = sum(min(int(fish_collected.get(f["name"], 0)), get_fish_trophy_requirement(f["name"], user_data)) for f in fish_pool)

        embed = discord.Embed(
            title=f"🏆 {ctx.author.display_name}'s Fish Trophy Room",
            description="Add fish with `sq trophy add <fish> <amount>`.",
            color=discord.Color.green() if fish_completed else discord.Color.gold()
        )
        normal_chunks = split_embed_lines(normal_fish_lines)
        specialty_chunks = split_embed_lines(specialty_fish_lines)

        for index, chunk in enumerate(normal_chunks, start=1):
            field_name = "Normal Fish" if len(normal_chunks) == 1 else f"Normal Fish ({index}/{len(normal_chunks)})"
            embed.add_field(name=field_name, value=chunk, inline=False)

        for index, chunk in enumerate(specialty_chunks, start=1):
            field_name = "Specialty Fish" if len(specialty_chunks) == 1 else f"Specialty Fish ({index}/{len(specialty_chunks)})"
            embed.add_field(name=field_name, value=chunk, inline=False)

        embed.add_field(name="Progress", value=f"{total_collected}/{total_needed} fish placed", inline=False)
        if fish_completed:
            embed.add_field(
                name="Badge Earned",
                value=f"{MASTER_OF_THE_SEA_BADGE['emoji']} **{MASTER_OF_THE_SEA_BADGE['name']}**\nCast cooldown 30s → 22s\nNet cooldown 1h → 45m",
                inline=False,
            )
        return embed

    def build_treasure_embed():
        tier_collections = {tier: [] for tier in range(1, 7)}

        for treasure_name, needed in treasure_requirements.items():
            info = treasure_index[treasure_name]
            tier = int(info.get("tier", 0))
            if tier not in tier_collections:
                continue
            tier_collections[tier].append((treasure_name, info, needed))

        total_needed = sum(treasure_requirements.values())
        total_collected = sum(min(int(treasure_collected.get(name, 0)), needed) for name, needed in treasure_requirements.items())
        embed = discord.Embed(
            title=f"🏆 {ctx.author.display_name}'s Treasure Trophy Room",
            description="Add treasures with `sq trophy add treasure <treasure> <amount>`.",
            color=discord.Color.green() if treasure_completed else discord.Color.gold(),
        )
        for tier in range(1, 7):
            sorted_entries = sorted(
                tier_collections[tier],
                key=lambda item: (item[1].get("min_value", item[1].get("value", 0)), item[0])
            )

            if not sorted_entries:
                embed.add_field(name=f"Tier {tier} Treasures", value="No treasures configured.", inline=False)
                continue

            tier_lines = []
            for treasure_name, info, needed in sorted_entries:
                count = int(treasure_collected.get(treasure_name, 0))
                count = max(0, min(count, needed))
                marker = "✅" if count >= needed else "⬜"
                tier_lines.append(f"{marker} {info['emoji']} **{treasure_name.title()}** ({count}/{needed})")

            tier_chunks = split_embed_lines(tier_lines)
            for index, chunk in enumerate(tier_chunks, start=1):
                field_name = f"Tier {tier} Treasures" if len(tier_chunks) == 1 else f"Tier {tier} Treasures ({index}/{len(tier_chunks)})"
                embed.add_field(name=field_name, value=chunk, inline=False)

        embed.add_field(name="Progress", value=f"{total_collected}/{total_needed} treasures placed", inline=False)
        if treasure_completed:
            embed.add_field(
                name="Badge Earned",
                value=f"{LEGENDARY_TREASURE_SEEKER_BADGE['emoji']} **{LEGENDARY_TREASURE_SEEKER_BADGE['name']}**\nAdventure cooldown 2h → 1h 30m",
                inline=False,
            )
        return embed

    class TrophyView(discord.ui.View):
        def __init__(self, author_id):
            super().__init__(timeout=180)
            self.author_id = author_id

        async def interaction_check(self, interaction: discord.Interaction):
            if interaction.user.id != self.author_id:
                await interaction.response.send_message("❌ This trophy room menu isn't for you.", ephemeral=True)
                return False
            return True

    view = TrophyView(ctx.author.id)

    async def show_page(interaction, page_name):
        embed = build_fish_embed() if page_name == "fish" else build_treasure_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    fish_button = discord.ui.Button(label="Fish Trophy Room", style=discord.ButtonStyle.primary)
    treasure_button = discord.ui.Button(label="Treasure Trophy Room", style=discord.ButtonStyle.secondary)

    async def fish_callback(interaction):
        await show_page(interaction, "fish")

    async def treasure_callback(interaction):
        await show_page(interaction, "treasure")

    fish_button.callback = fish_callback
    treasure_button.callback = treasure_callback
    view.add_item(fish_button)
    view.add_item(treasure_button)

    await ctx.send(embed=build_fish_embed(), view=view)


@trophy_room.command(name="add")
async def trophy_add(ctx, *, fish_input: str):
    user_data = get_user_data(ctx.author)
    inv = user_data.setdefault("inventory", {})
    fish_trophy = normalize_trophy_room(user_data)
    treasure_trophy = normalize_treasure_trophy_room(user_data)

    parts = fish_input.strip().rsplit(" ", 1)
    amount = 1
    item_name = fish_input.strip()
    if len(parts) == 2 and parts[1].isdigit():
        item_name = parts[0].strip()
        amount = int(parts[1])

    if amount < 1:
        await ctx.send("❌ Amount must be at least 1.")
        return

    lower = item_name.lower().strip()
    is_treasure_mode = False
    if lower.startswith("treasure "):
        is_treasure_mode = True
        item_name = item_name[9:].strip()

    if is_treasure_mode:
        lookup_name = normalize_treasure_lookup_name(item_name)
        chosen_treasure = next(
            (t for t in treasure_index if normalize_treasure_lookup_name(t) == lookup_name),
            None,
        )
        if not chosen_treasure or chosen_treasure in EXCLUDED_TROPHY_TREASURES:
            await ctx.send("❌ That treasure can't be added to the trophy room.")
            return

        required = get_treasure_trophy_requirements(user_data).get(chosen_treasure, 1)
        current = int(treasure_trophy.get(chosen_treasure, 0))
        if current >= required:
            await ctx.send(f"❌ You already reached the trophy goal for **{chosen_treasure.title()}** ({current}/{required}).")
            return

        available = int(inv.get(chosen_treasure, 0))
        if available < 1:
            await ctx.send("❌ You need that treasure in your inventory to place it in the trophy room.")
            return

        add_amount = min(amount, required - current, available)
        inv[chosen_treasure] -= add_amount
        if inv[chosen_treasure] <= 0:
            del inv[chosen_treasure]

        treasure_trophy[chosen_treasure] = current + add_amount
        if treasure_trophy[chosen_treasure] >= required:
            completed = all(int(treasure_trophy.get(name, 0)) >= need for name, need in get_treasure_trophy_requirements(user_data).items())
            if completed:
                grant_badge(user_data, LEGENDARY_TREASURE_SEEKER_BADGE["name"])
                grant_badge(user_data, MASTER_TREASURE_SEEKER_ALIAS)

        save_users()
        await ctx.send(f"✅ Added **{add_amount} {chosen_treasure.title()}** to your treasure trophy room! ({treasure_trophy[chosen_treasure]}/{required})")
        return

    chosen_fish = next((f["name"] for f in fish_pool if f["name"].lower() == item_name.lower().strip()), None)
    if not chosen_fish:
        await ctx.send("❌ That fish doesn't exist.")
        return

    required = get_fish_trophy_requirement(chosen_fish, user_data)
    current = int(fish_trophy.get(chosen_fish, 0))
    if current >= required:
        shown_name = TROPHY_DISPLAY_NAMES.get(chosen_fish, chosen_fish.title())
        await ctx.send(f"❌ You already reached the trophy goal for **{shown_name}** ({current}/{required}).")
        return

    available = int(inv.get(chosen_fish, 0))
    if available < 1:
        await ctx.send("❌ You need that fish in your inventory to place it in the trophy room.")
        return

    add_amount = min(amount, required - current, available)
    inv[chosen_fish] -= add_amount
    if inv[chosen_fish] <= 0:
        del inv[chosen_fish]

    fish_trophy[chosen_fish] = current + add_amount

    if fish_trophy[chosen_fish] >= required:
        fish_completed = all(int(fish_trophy.get(f["name"], 0)) >= get_fish_trophy_requirement(f["name"], user_data) for f in fish_pool)
        if fish_completed:
            grant_badge(user_data, MASTER_OF_THE_SEA_BADGE["name"])

    save_users()
    shown_name = TROPHY_DISPLAY_NAMES.get(chosen_fish, chosen_fish.title())
    await ctx.send(f"✅ Added **{add_amount} {shown_name}** to your trophy room! ({fish_trophy[chosen_fish]}/{required})")


@bot.command()
async def net(ctx):
    user_id = str(ctx.author.id)
    user_data = get_user_data(ctx.author)
    now = time.time()

    net_cd = get_net_cooldown_seconds(user_data)
    if user_id in net_cooldowns and now - net_cooldowns[user_id] < net_cd:
        remaining = net_cd - (now - net_cooldowns[user_id])
        await ctx.send(
            f"🕓 You must wait {format_duration(remaining)} before throwing your net to sea again."
        )
        return

    net_cooldowns[user_id] = now
    save_cooldowns()

    equipped_rod = user_data.get("rod", "wooden rod")
    rod_data = rods.get(equipped_rod, {})
    gold_bonus = rod_data.get("bonus", 0)
    rarity_bonus = rod_data.get("rarity_bonus", 0)

    catch_amount = random.randint(10, 15)

    rarity_mult = get_fishbowl_multiplier(user_data) * get_rare_fish_multiplier(user_data)
    adjusted_chances = [
        (f["chance"] * (1 + rarity_bonus)) * rarity_weight((f["chance"] * (1 + rarity_bonus)), rarity_mult)
        for f in fish_pool
    ]

    total_xp = 0
    total_gold = 0
    caught_summary = {}

    for _ in range(catch_amount):
        fish = random.choices(fish_pool, weights=adjusted_chances)[0]
        name = fish["name"]
        xp = fish["xp"]

        total_xp += xp
        user_data["xp"] += xp
        user_data["total_fish"] += 1

        if has_boost(user_data, "autosell"):
            gold = int(xp * (1 + gold_bonus))
            total_gold += gold
            user_data["gold"] += gold
        else:
            user_data["inventory"][name] = user_data["inventory"].get(name,
                                                                      0) + 1

        caught_summary[name] = caught_summary.get(name, 0) + 1

    new_level, xp_into_level, next_level_xp = get_level_info(user_data["xp"])
    level_text = ""
    if new_level > user_data.get("level", 1):
        level_text = f"\n🎉 You leveled up to **Level {new_level}**!"
        user_data["level"] = new_level

    summary_lines = []
    for fish in fish_pool:
        name = fish["name"]
        emoji = fish["emoji"]
        count = caught_summary.get(name, 0)
        if count > 0:
            summary_lines.append(f"{emoji} {name.title()} — {count}")

    embed = discord.Embed(
        description=
        f"<:net:1478917596807172126> {ctx.author.display_name} threw out a fishing net and caught **{catch_amount} fish!**\n\n"
        + "\n".join(summary_lines),
        color=discord.Color.teal())

    reward_text = f"<:level:1399200622779302004> XP: +{total_xp}\n"

    if has_boost(user_data, "autosell"):
        reward_text += f"<:moneysack:1478545126732333187> Sold with Autosell for {total_gold} Gold <:coin:1399146146315894825>\n"

    if level_text:
        reward_text += level_text

    embed.add_field(name="Rewards", value=reward_text, inline=False)

    await ctx.send(embed=embed)
    save_users()


@bot.command()
async def debug_inventory(ctx):
    user_data = get_user_data(ctx.author)
    await ctx.send(f"```{json.dumps(user_data['inventory'], indent=2)}```")

@bot.command()
async def remove(ctx, member: discord.Member, *, args: str):
    # 🔒 Only YOU can use this command
    if ctx.author.id != 544495887582494720:
        await ctx.send("❌ You cannot use this command.")
        return

    parts = args.lower().split()
    if not parts:
        await ctx.send("❌ Please specify an item and amount.")
        return

    # Quantity at end (optional)
    qty = 1
    if parts[-1].isdigit():
        qty = int(parts[-1])
        parts = parts[:-1]

    if qty < 1:
        await ctx.send("bro you can't remove negative items 💀")
        return

    item_name = " ".join(parts).strip()
    target_data = get_user_data(member)
    inv = target_data.setdefault("inventory", {})

    # ── COINS / GOLD ──
    if item_name in ["coin", "coins", "gold"]:
        owned = int(target_data.get("gold", 0))
        if owned <= 0:
            await ctx.send("❌ They don't have any coins.")
            return

        removed = min(qty, owned)
        target_data["gold"] = owned - removed

        await ctx.send(
            f"✅ Removed {removed} coin(s) from {member.display_name}."
        )
        save_users()
        return

    # ── FISH ──
    # ── FISH ── (case-insensitive)
    fish = next((f for f in fish_pool if f["name"].lower() == item_name), None)
    if fish:
        key = fish["name"]  # ✅ canonical casing from fish_pool
        owned = int(inv.get(key, 0))
        if owned <= 0:
            await ctx.send("❌ They don't have that fish.")
            return

        removed = min(qty, owned)
        inv[key] = owned - removed
        if inv[key] <= 0:
            del inv[key]

        await ctx.send(f"✅ Removed {removed} {key.title()} from {member.display_name}.")
        save_users()
        return

    # ── TREASURES ──
    if item_name in treasure_index:
        owned = int(inv.get(item_name, 0))
        owned_t = int(target_data.get("treasures", {}).get(item_name, 0))

        if owned <= 0 and owned_t <= 0:
            await ctx.send("❌ They don't have that treasure.")
            return

        removed = min(qty, max(owned, owned_t))

        # Inventory entry
        if owned > 0:
            inv[item_name] = owned - removed
            if inv[item_name] <= 0:
                inv.pop(item_name, None)

        # Treasures tracker entry
        if "treasures" not in target_data:
            target_data["treasures"] = {}
        if owned_t > 0:
            target_data["treasures"][item_name] = owned_t - removed
            if target_data["treasures"][item_name] <= 0:
                target_data["treasures"].pop(item_name, None)

        await ctx.send(f"✅ Removed {removed} {item_name.title()} from {member.display_name}.")
        save_users()
        return

    # ── BAITS (singular allowed) ──
    if item_name not in baits:
        for bait_key, bait_data in baits.items():
            singular = (bait_data.get("singular") or "").lower().strip()
            if singular and item_name == singular:
                item_name = bait_key
                break

    if item_name in baits:
        owned = int(inv.get(item_name, 0))
        if owned <= 0:
            await ctx.send("❌ They don't have that bait in inventory.")
            return

        removed = min(qty, owned)
        inv[item_name] = owned - removed
        if inv[item_name] <= 0:
            del inv[item_name]

        await ctx.send(
            f"✅ Removed {removed} {format_bait_name(item_name, removed)} from {member.display_name}."
        )
        save_users()
        return

    # ── CHESTS ──
    if item_name in chests:
        owned = int(target_data.get("chests", {}).get(item_name, 0))
        if owned <= 0:
            await ctx.send("❌ They don't have that chest.")
            return

        removed = min(qty, owned)
        target_data["chests"][item_name] = owned - removed
        if target_data["chests"][item_name] <= 0:
            target_data["chests"].pop(item_name, None)

        await ctx.send(f"✅ Removed {removed} {item_name.title()} from {member.display_name}.")
        save_users()
        return

    await ctx.send("❌ Item not found.")

@bot.command(name="goon")
async def goon_corner(ctx, *, arg=None):
    if arg == "corner":
        await ctx.send(f"no {ctx.author.display_name}, you a freak")


@bot.command(name="fuck")
async def fuck_andy(ctx, *, arg=None):
    if arg == "andy":
        await ctx.send(f"Boys, {ctx.author.display_name} wants to fuck andy..."
                       )


@bot.command(aliases=["adv"])
async def adventure(ctx):
    user = ctx.author
    user_id = str(user.id)
    user_data = get_user_data(user)
    now = time.time()

    adv_cd = get_adventure_cooldown_seconds(user_data)
    if user_id in adventure_cooldowns:
        elapsed = now - adventure_cooldowns[user_id]
        if elapsed < adv_cd:
            remaining = int((adv_cd - elapsed) // 60)
            await ctx.send(
                "🕓 You can not adventure again yet, check cooldown with 'sq cd'"
            )
            return

    adventure_cooldowns[user_id] = time.time()
    save_cooldowns()

    chest_names = ["chest", "silver chest", "ruby chest", "diamond chest", "godly chest", "deep sea chest"]
    weights = [49.75, 20, 15, 10, 4.75, 0.5]

    chest_amount = 2 if random.random() < 0.20 else 1

    rolled_chests = random.choices(chest_names, weights=weights, k=chest_amount)
    chest_counts = {}
    for chest_name in rolled_chests:
        chest_counts[chest_name] = chest_counts.get(chest_name, 0) + 1
        user_data["chests"][chest_name] = user_data["chests"].get(chest_name, 0) + 1

    rewards_text = " and ".join(
        [f"{count}x {chests[name]['emoji']} **{name.title()}**" for name, count in chest_counts.items()]
    )

    embed = discord.Embed(
        title="🗺️ Adventure Complete!",
        description=f"{ctx.author.display_name} found {rewards_text}!",
        color=discord.Color.orange())
    await ctx.send(embed=embed)
    save_users()

@bot.command()
async def cast(ctx):
    user_id = str(ctx.author.id)
    user_data = get_user_data(ctx.author)
    now = time.time()

    cast_cd = get_cast_cooldown_seconds(user_data)
    if user_id in cooldowns and now - cooldowns[user_id] < cast_cd:
        remaining = round(cast_cd - (now - cooldowns[user_id]), 1)
        await ctx.send(
            f"⏳ {ctx.author.display_name}, you need to wait {remaining}s before fishing again."
        )
        return

    base_casts = 2 if has_boost(user_data, "double cast") else 1
    cooldowns[user_id] = time.time()
    save_cooldowns()

    equipped_rod = user_data.get("rod", "wooden rod")
    rod_data = rods.get(equipped_rod, {})
    gold_bonus = rod_data.get("bonus", 0)
    rarity_bonus = rod_data.get("rarity_bonus", 0)
    cupid_extra_cast = rod_data.get("double_cast_chance", 0)
    deep_sea_treasure_chance = rod_data.get("treasure_cast_chance", 0)

    if equipped_rod == "cupid rod" and has_boost(user_data, "extra love"):
        cupid_extra_cast = 0.15

    deep_sea_min_tier = 1
    deep_sea_max_tier = 3
    if equipped_rod == "deep sea rod" and has_boost(user_data, "deeper casts"):
        deep_sea_treasure_chance = 0.15
        deep_sea_max_tier = 4

    deep_sea_bonus_treasure = None
    if deep_sea_treasure_chance > 0 and random.random() < deep_sea_treasure_chance:
        deep_sea_bonus_treasure = choose_equal_tier_treasure(deep_sea_min_tier, deep_sea_max_tier)

    casts = base_casts
    if cupid_extra_cast > 0 and random.random() < cupid_extra_cast:
        casts += 1
        results = ["💘 **Cupid Rod bonus:** You got an extra fish this cast!"]
    else:
        results = []

    contract_completion = None

    for _ in range(casts):
        rarity_mult = 1.0

        if user_data.get("bait") and user_data.get("bait_uses", 0) > 0:
            bait_name = user_data["bait"]
            rarity_mult *= float(baits[bait_name]["multiplier"])

        rarity_mult *= get_fishbowl_multiplier(user_data)
        rarity_mult *= get_rare_fish_multiplier(user_data)

        weights = []
        for f in fish_pool:
            base = f["chance"] * (1 + rarity_bonus)
            weights.append(base * rarity_weight(base, rarity_mult))

        fish = random.choices(fish_pool, weights=weights)[0]

        name = fish["name"]
        emoji = fish["emoji"]
        xp = fish["xp"]

        user_data["xp"] += xp
        user_data["total_fish"] += 1

        if has_boost(user_data, "autosell"):
            gold_earned = int(xp * (1 + gold_bonus))
            user_data["gold"] += gold_earned
        else:
            user_data["inventory"][name] = user_data["inventory"].get(name, 0) + 1
            gold_earned = int(xp * (1 + gold_bonus))

        contract_completion = contract_completion or update_contract_progress(user_data, "catch_fish", 1, name)
        contract_completion = contract_completion or update_contract_progress(user_data, "gain_xp", xp)

        new_level, xp_into_level, next_level_xp = get_level_info(user_data["xp"])
        if new_level > user_data.get("level", 1):
            user_data["level"] = new_level
            results.append(
                f"🎉 {ctx.author.display_name} leveled up to **Level {new_level}**!"
            )

        result = f"<:cast_bobber:1399044610684096726> {ctx.author.display_name} caught a **{emoji} {name}**!\n<:level:1399200622779302004> XP: +{xp}"
        if has_boost(user_data, "autosell"):
            result += f"\n<:moneysack:1478545126732333187> Sold instantly for {gold_earned} <:coin:1399146146315894825> (Autosell Active)"
        results.append(result)

    contract_completion = contract_completion or update_contract_progress(user_data, "cast", 1)


    if deep_sea_bonus_treasure:
        user_data.setdefault("treasures", {})
        user_data.setdefault("inventory", {})
        user_data["inventory"][deep_sea_bonus_treasure] = user_data["inventory"].get(
            deep_sea_bonus_treasure, 0) + 1
        user_data["treasures"][deep_sea_bonus_treasure] = user_data["treasures"].get(
            deep_sea_bonus_treasure, 0) + 1
        results.append(
            f"🌊 **Deep Sea Rod bonus:** You pulled up {treasure_index[deep_sea_bonus_treasure]['emoji']} **{deep_sea_bonus_treasure.title()}**!"
        )

    if user_data.get("bait") and user_data.get("bait_uses", 0) > 0:
        user_data["bait_uses"] -= 1

        if user_data["bait_uses"] <= 0:
            expired_bait = user_data["bait"]
            equipped_amt = int(user_data.get("bait_amount", 0) or 0)
            if equipped_amt > 0:
                equipped_amt -= 1
                user_data["bait_amount"] = equipped_amt

            if user_data.get("bait_amount", 0) > 0:
                user_data["bait_uses"] = random.randint(4, 7)
                results.append(
                    f"Your {baits[expired_bait]['emoji']} **{expired_bait.title()}** fell off the hook!"
                )
            else:
                user_data["bait"] = None
                user_data["bait_uses"] = 0
                results.append(
                    f"Your {baits[expired_bait]['emoji']} last **{expired_bait.title()}** fell off the hook!"
                )

    embed = discord.Embed(color=discord.Color.yellow())
    embed.description = "\n".join(results)
    await ctx.send(embed=embed)
    await send_contract_completion_embed(ctx, contract_completion)
    save_users()

import os

@bot.command()
async def give(ctx, member: discord.Member, *, args: str):

    # 🔒 Only YOU can use this command
    if ctx.author.id != 544495887582494720:
        await ctx.send("❌ You cannot use this command.")
        return

    parts = args.lower().split()
    if not parts:
        await ctx.send("❌ Please specify an item and amount.")
        return

    # Quantity at end
    qty = 1
    if parts[-1].isdigit():
        qty = int(parts[-1])
        parts = parts[:-1]

    if qty < 1:
        await ctx.send("bro you can't give negative items 💀")
        return

    item_name = " ".join(parts).strip()

    target_data = get_user_data(member)

    # ── COINS / GOLD ──
    if item_name in ["coin", "coins", "gold"]:
        target_data["gold"] = int(target_data.get("gold", 0)) + qty
        await ctx.send(
            f"✅ Gave {qty} coin(s) to {member.display_name}."
        )
        save_users()
        return

    # ── FISH ──
    # ── FISH ── (case-insensitive)
    fish = next((f for f in fish_pool if f["name"].lower() == item_name), None)
    if fish:
        key = fish["name"]  # ✅ canonical casing from fish_pool
        target_data["inventory"][key] = target_data["inventory"].get(key, 0) + qty
        await ctx.send(f"✅ Gave {qty} {key.title()} to {member.display_name}.")
        save_users()
        return

    # ── TREASURES ──
    if item_name in treasure_index:
        target_data["inventory"][item_name] = target_data["inventory"].get(item_name, 0) + qty
        target_data["treasures"][item_name] = target_data["treasures"].get(item_name, 0) + qty
        await ctx.send(f"✅ Gave {qty} {item_name.title()} to {member.display_name}.")
        save_users()
        return

    # ── BAITS (singular allowed) ──
    if item_name not in baits:
        for bait_key, bait_data in baits.items():
            singular = (bait_data.get("singular") or "").lower().strip()
            if singular and item_name == singular:
                item_name = bait_key
                break

    if item_name in baits:
        target_data["inventory"][item_name] = target_data["inventory"].get(item_name, 0) + qty
        await ctx.send(
            f"✅ Gave {qty} {format_bait_name(item_name, qty)} to {member.display_name}."
        )
        save_users()
        return

    # ── CHESTS ──
    if item_name in chests:
        target_data["chests"][item_name] = target_data["chests"].get(item_name, 0) + qty
        await ctx.send(
            f"✅ Gave {qty} {item_name.title()} to {member.display_name}."
        )
        save_users()
        return

    await ctx.send("❌ Item not found.")

@bot.command(aliases=["open"])
async def open_chest(ctx, *, args: str):
    args_list = args.lower().split()

    if not args_list:
        await ctx.send("❌ Please specify a chest name")
        return

    user_data = get_user_data(ctx.author)
    user_chests = user_data.get("chests", {})

    # Support: sq open all / sq open all chest (opens every chest type the user owns)
    if (len(args_list) == 1 and args_list[0] == "all") or args_list == ["all", "chest"]:
        owned_chests = {
            name: int(user_chests.get(name, 0))
            for name in chests
            if int(user_chests.get(name, 0)) > 0
        }

        if not owned_chests:
            await ctx.send("❌ You don't have any chests to open.")
            return

        total_gold = 0
        total_xp = 0
        found_treasures = []

        for chest_name, to_open in owned_chests.items():
            rewards = chests[chest_name]["rewards"]

            for _ in range(to_open):
                gold = random.randint(*rewards.get("gold", (0, 0)))
                xp = random.randint(*rewards.get("xp", (0, 0)))
                total_gold += gold
                total_xp += xp

                treasure_config = rewards.get("treasures")
                if treasure_config:
                    count_range = treasure_config["count"]
                    max_tier = treasure_config["max_tier"]
                    rarity_bias = treasure_config["rarity_bias"]
                    selected = choose_treasures(max_tier, count_range, rarity_bias)

                    if "treasures" not in user_data:
                        user_data["treasures"] = {}
                    user_data.setdefault("inventory", {})

                    for name in selected:
                        user_data["inventory"][name] = user_data["inventory"].get(name, 0) + 1
                        user_data["treasures"][name] = user_data["treasures"].get(name, 0) + 1
                        found_treasures.append(name)

                    if chest_name == "deep sea chest" and random.random() < rewards.get("one_piece_chance", 0):
                        user_data["inventory"][ONE_PIECE_NAME] = user_data["inventory"].get(ONE_PIECE_NAME, 0) + 1
                        user_data["treasures"][ONE_PIECE_NAME] = user_data["treasures"].get(ONE_PIECE_NAME, 0) + 1
                        found_treasures.append(ONE_PIECE_NAME)

            user_chests[chest_name] -= to_open

        user_data["gold"] += total_gold
        user_data["xp"] += total_xp

        new_level, xp_into_level, next_level_xp = get_level_info(user_data["xp"])
        level_up_text = ""
        if new_level > user_data.get("level", 1):
            level_up_text = f"\n🎉 You leveled up to **Level {new_level}**!"
            user_data["level"] = new_level

        opened_lines = [
            f"{chests[name]['emoji']} **{name.title()}** x{count}"
            for name, count in owned_chests.items()
        ]

        embed = discord.Embed(
            title=f"{ctx.author.display_name} opened all their chests!",
            color=discord.Color.gold())

        lines = []
        lines.extend(opened_lines)
        lines.append("")

        if found_treasures:
            treasure_lines = [
                f"{treasure_index[t]['emoji']} **{t.title()}**"
                for t in found_treasures
            ]
            lines.extend(treasure_lines)
            lines.append("")

        lines.append(f"<:coin:1399146146315894825> Gold: +{total_gold}")
        lines.append("")
        lines.append(
            f"<:level:1399200622779302004> XP: +{total_xp}{level_up_text}")

        embed.description = "\n".join(lines)
        await ctx.send(embed=embed)
        save_users()
        return

    if args_list[-1] == "all":
        amount = "all"
        chest_name_words = args_list[:-1]
    else:
        try:
            amount = int(args_list[-1])
            chest_name_words = args_list[:-1]
        except ValueError:
            amount = 1
            chest_name_words = args_list

    chest_name = " ".join(chest_name_words).strip()
    if not chest_name:
        await ctx.send("❌ Please specify a chest name")
        return

    if chest_name not in chests:
        await ctx.send("❌ Not a valid chest type")
        return

    user_chest_count = user_chests.get(chest_name, 0)

    if user_chest_count <= 0:
        await ctx.send(f"❌ You don't have any **{chest_name.title()}** to open"
                       )
        return

    if amount == "all":
        to_open = user_chest_count
    else:
        to_open = amount
        if to_open < 1:
            await ctx.send(
                "bro, you can't have a negative or decimal amount of chests")
            return
        if to_open > user_chest_count:
            await ctx.send(
                f"❌ You only have {user_chest_count} **{chest_name.title()}** to open, don't get ahead of yourself"
            )
            return

    chest = chests[chest_name]
    emoji = chest["emoji"]
    rewards = chest["rewards"]

    total_gold = 0
    total_xp = 0
    found_treasures = []

    for _ in range(to_open):
        gold = random.randint(*rewards.get("gold", (0, 0)))
        xp = random.randint(*rewards.get("xp", (0, 0)))
        total_gold += gold
        total_xp += xp

        treasure_config = rewards.get("treasures")
        if treasure_config:
            count_range = treasure_config["count"]
            max_tier = treasure_config["max_tier"]
            rarity_bias = treasure_config["rarity_bias"]
            selected = choose_treasures(max_tier, count_range, rarity_bias)

            if "treasures" not in user_data:
                user_data["treasures"] = {}
            inventory = user_data.setdefault("inventory", {})

            for name in selected:
                user_data["inventory"][name] = user_data["inventory"].get(
                    name, 0) + 1
                user_data["treasures"][name] = user_data["treasures"].get(
                    name, 0) + 1
                found_treasures.append(name)

            if chest_name == "deep sea chest" and random.random() < rewards.get("one_piece_chance", 0):
                user_data["inventory"][ONE_PIECE_NAME] = user_data["inventory"].get(ONE_PIECE_NAME, 0) + 1
                user_data["treasures"][ONE_PIECE_NAME] = user_data["treasures"].get(ONE_PIECE_NAME, 0) + 1
                found_treasures.append(ONE_PIECE_NAME)

    user_data["gold"] += total_gold
    user_data["xp"] += total_xp
    user_chests[chest_name] -= to_open

    new_level, xp_into_level, next_level_xp = get_level_info(user_data["xp"])
    level_up_text = ""
    if new_level > user_data.get("level", 1):
        level_up_text = f"\n🎉 You leveled up to **Level {new_level}**!"
        user_data["level"] = new_level

    opened_line = f"{ctx.author.display_name} opened {to_open} {chest_name.title()}{'s' if to_open > 1 else ''}!"

    embed = discord.Embed(
        title=f"{emoji} {opened_line}",
        color=discord.Color.gold())

    lines = []
    lines.append(opened_line)

    if chest_name == "deep sea chest" and ONE_PIECE_NAME in found_treasures:
        lines.append("**YOU FOUND THE ONE PIECE!!**")

    if found_treasures:
        treasure_lines = [
            f"{treasure_index[t]['emoji']} **{t.title()}**"
            for t in found_treasures
        ]
        lines.extend(treasure_lines)

    lines.append("")

    lines.append(f"<:coin:1399146146315894825> Gold: +{total_gold}")
    lines.append("")
    lines.append(
        f"<:level:1399200622779302004> XP: +{total_xp}{level_up_text}")

    embed.description = "\n".join(lines)

    await ctx.send(embed=embed)
    save_users()


@bot.command(aliases=["cd", "cooldown"])
async def cooldown_check(ctx):
    user_id = str(ctx.author.id)
    now = time.time()
    user_data = get_user_data(ctx.author)

    cast_remaining = 0
    cast_cd = get_cast_cooldown_seconds(user_data)
    if user_id in cooldowns and now - cooldowns[user_id] < cast_cd:
        cast_remaining = cast_cd - (now - cooldowns[user_id])

    adventure_remaining = 0
    adv_cd = get_adventure_cooldown_seconds(user_data)
    if user_id in adventure_cooldowns and now - adventure_cooldowns[
            user_id] < adv_cd:
        adventure_remaining = adv_cd - (now - adventure_cooldowns[user_id])

    net_remaining = 0
    net_cd = get_net_cooldown_seconds(user_data)
    if user_id in net_cooldowns and now - net_cooldowns[user_id] < net_cd:
        net_remaining = net_cd - (now - net_cooldowns[user_id])

    dig_remaining = 0
    if user_id in dig_cooldowns and now - dig_cooldowns[user_id] < 600:
        dig_remaining = 600 - (now - dig_cooldowns[user_id])

    contract_buy_remaining = max(
        0,
        (float(user_data.get("contracts_meta", {}).get("last_bought", 0)) + 4 * 3600) - now,
    )

    active_boosts = []
    emoji_map = {
        "double cast": "<:double_cast:1399044646700716154>",
        "autosell": "<:autosell:1399198067533680741>",
        "extra love": "💘",
        "deeper casts": "🌊",
    }

    for boost in user_data.get("boosts", {}):
        remaining = user_data["boosts"][boost] - time.time()
        if remaining > 0:
            boost_name = boost.title() if boost != "autosell" else "Autosell"
            emoji = emoji_map.get(boost, "")
            active_boosts.append(
                f"{emoji} {boost_name} ({format_duration(remaining)} left)")

    if has_badge(user_data, MASTER_OF_THE_SEA_BADGE["name"]):
        active_boosts.append(
            f"{MASTER_OF_THE_SEA_BADGE['emoji']} Master of the Sea\n• Cast cooldown: 30s → 22s\n• Net cooldown: 1h → 45m"
        )

    if has_badge(user_data, LEGENDARY_TREASURE_SEEKER_BADGE["name"]):
        active_boosts.append(
            f"{LEGENDARY_TREASURE_SEEKER_BADGE['emoji']} Legendary Treasure Seeker\n• Adventure cooldown: 2h → 1h 30m"
        )

    boost_text = "\n".join(active_boosts) if active_boosts else "No boosts active"

    desc_lines = [
        f"{'✅ -- Cast' if cast_remaining == 0 else f'🕓 -- Cast ({format_duration(cast_remaining)})'}",
        f"{'✅ -- Dig' if dig_remaining == 0 else f'🕓 -- Dig ({format_duration(dig_remaining)})'}",
        f"{'✅ -- Net' if net_remaining == 0 else f'🕓 -- Net ({format_duration(net_remaining)})'}",
        f"{'✅ -- Adventure' if adventure_remaining == 0 else f'🕓 -- Adventure ({format_duration(adventure_remaining)})'}",
        f"{'✅ -- Buy Contract' if contract_buy_remaining == 0 else f'🕓 -- Buy Contract ({format_duration(contract_buy_remaining)})'}",
    ]

    embed = discord.Embed(title="━━━━ Cooldown Check ━━━━",
                          description="\n".join(desc_lines),
                          color=discord.Color.purple())

    embed.add_field(
        name="━━━━ <:boosts:1399198567486197791> Active Boosts ━━━━",
        value=boost_text,
        inline=False)

    await ctx.send(embed=embed)


@bot.command(aliases=["p"])
async def profile(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_data = get_user_data(member)
    level, xp_into_level, next_level_xp = get_level_info(user_data["xp"])
    percent = int((xp_into_level / next_level_xp) * 100) if next_level_xp > 0 else 0

    title_badges = []
    if has_badge(user_data, MASTER_OF_THE_SEA_BADGE["name"]):
        title_badges.append(MASTER_OF_THE_SEA_BADGE["emoji"])
    if has_badge(user_data, LEGENDARY_TREASURE_SEEKER_BADGE["name"]):
        title_badges.append(LEGENDARY_TREASURE_SEEKER_BADGE["emoji"])
    suffix = (" " + " ".join(title_badges)) if title_badges else ""

    embed = discord.Embed(
        title=f"{member.display_name}'s Profile{suffix}",
        color=discord.Color.blue()
    )
    embed.description = f"Time Travels: **{int(user_data.get('time_travels', 0))}**"

    # ✅ Always safe avatar (discord.py v2+)
    embed.set_thumbnail(url=member.display_avatar.url)

    # Gold
    rod = user_data.get("rod", "wooden rod")
    rod_data = rods.get(rod, rods["wooden rod"])
    gold_bonus = int(rod_data.get("bonus", 0) * 100)
    gold = user_data.get("gold", 0)

    embed.add_field(
        name="<:coin:1399146146315894825> Gold",
        value=f"{gold} (+{gold_bonus}% boost)",
        inline=False
    )

    # XP
    embed.add_field(
        name="<:level:1399200622779302004> XP",
        value=f"Level {level} | {xp_into_level}/{next_level_xp} XP ({percent}%)",
        inline=False
    )

    # Equipped Rod
    gold_bonus_percent = int(rod_data.get("bonus", 0) * 100)
    rarity_bonus_percent = int(rod_data.get("rarity_bonus", 0) * 100)
    rarity_text = f"\n*+ {rarity_bonus_percent}% rarity chance*" if rarity_bonus_percent > 0 else ""
    abilities = []
    if rod_data.get("double_cast_chance", 0) > 0:
        abilities.append(f"{int(rod_data['double_cast_chance'] * 100)}% chance for an extra fish")
    if rod_data.get("treasure_cast_chance", 0) > 0:
        abilities.append(f"{int(rod_data['treasure_cast_chance'] * 100)}% chance to pull a tier 1-3 treasure")
    ability_text = f"\n*Ability: {' | '.join(abilities)}*" if abilities else ""

    embed.add_field(
        name="━━━━━ Equipped Rod ━━━━━",
        value=f"{rod_data['emoji']} {rod.title()}\n*+ {gold_bonus_percent}% gold*{rarity_text}{ability_text}",
        inline=False
    )

    # Fishing stats
    total_fish = user_data.get("total_fish", 0)
    bait_mult = 1.0
    if user_data.get("bait") and user_data.get("bait_uses", 0) > 0:
        bait_name = user_data["bait"]
        bait_mult = float(baits[bait_name]["multiplier"])

    bowl_mult = get_fishbowl_multiplier(user_data)
    combined_rare_odds_increase = (bait_mult * bowl_mult * get_rare_fish_multiplier(user_data) - 1.0) * 100

    embed.add_field(
        name="━━ <:wooden_rod:1399044497068920912> Fishing Stats ━━",
        value=(
            f"Fish caught: <:fish:1399192790797127861> *{total_fish}*\n"
            f"Total rare fish odds: +*{combined_rare_odds_increase:.1f}%*"
        ),
        inline=False
    )

    # Equipped bait (singular/plural)
    bait_key = (user_data.get("bait") or "").lower().strip()
    equipped_amt = int(user_data.get("bait_amount", 0) or 0)

    if bait_key and bait_key in baits and equipped_amt > 0:
        bait_disp = format_bait_name(bait_key, equipped_amt)
        bait_text = f"{baits[bait_key]['emoji']} {bait_disp} — {equipped_amt} Equipped"
    else:
        bait_text = "None"

    embed.add_field(
        name="━━━━ Equipped Bait ━━━━",
        value=bait_text,
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command()
async def shop(ctx):
    user_data = get_user_data(ctx.author)
    user_gold = user_data.get("gold", 0)
    gold_display = f"{user_gold} <:coin:1399146146315894825>"
    equipped_rod = user_data.get("rod", "wooden rod")

    def build_shop_embed(title):
        embed = discord.Embed(title=title, color=discord.Color.red())
        embed.add_field(name="Your Gold", value=gold_display, inline=False)
        return embed

    rods_embed = build_shop_embed("🛍️ Shop — Rods")

    # ━━━ RODS PAGE ━━━
    rod_lines = []
    for name, data in rods.items():
        bonus_percent = int(data.get("bonus", 0) * 100)
        tag = " *(Equipped)*" if name == equipped_rod else ""
        abilities = []

        if data.get("double_cast_chance", 0) > 0:
            double_cast_percent = int(data["double_cast_chance"] * 100)
            abilities.append(f"{double_cast_percent}% chance for an extra fish")

        if data.get("treasure_cast_chance", 0) > 0:
            treasure_cast_percent = int(data["treasure_cast_chance"] * 100)
            tier_text = "tier 1-4" if name == "deep sea rod" and has_boost(user_data, "deeper casts") else "tier 1-3"
            abilities.append(f"{treasure_cast_percent}% chance to pull a tier 1-3 treasure")

        ability_text = ""
        if abilities:
            ability_text = f"\n*Ability: {' | '.join(abilities)}*"

        rod_lines.append(
            f"**{data['emoji']} {name.title()}** — {data['price']} <:coin:1399146146315894825>{tag}\n"
            f"*+ {bonus_percent}% gold on fish sell*{ability_text}"
        )
    for rod_chunk in chunk_lines_for_embed(rod_lines):
        rods_embed.add_field(
            name="",
            value=rod_chunk,
            inline=False
        )
    while len(rods_embed.fields)%3 != 0:
        rods_embed.add_field(name="\u200b", value="\u200b", inline=True)

    other_embed = build_shop_embed("🛍️ Shop — Boosts, Bait & Fish Bowl")

    # ━━━ BOOSTS ━━━
    boost_lines = []
    for name, data in boosts.items():
        tag = " *(Active)*" if has_boost(user_data, name) else ""
        boost_lines.append(
            f"**{data['emoji']} {name.title()}** — {data['price']} <:coin:1399146146315894825>{tag}\n"
            f"*{data['description']}*"
        )
    for idx, boost_chunk in enumerate(chunk_lines_for_embed(boost_lines), start=1):
        title_suffix = "" if idx == 1 else f" (Page {idx})"
        other_embed.add_field(
            name=f"━━━━ <:boosts:1399198567486197791> Boosts{title_suffix} ━━━━",
            value=boost_chunk,
            inline=False
        )

    # ━━━ BAITS ━━━
    bait_lines = []
    for name, data in baits.items():
        tag = " *(Equipped)*" if user_data.get("bait") == name else ""

        mult = data.get("multiplier", 1)
        percent = round((mult - 1) * 100)

        bait_lines.append(
            f"**{data['emoji']} {name.title()}** — {data['price']} <:coin:1399146146315894825>{tag}\n"
            f"*+{percent}% rare fish odds*"
        )
    for idx, bait_chunk in enumerate(chunk_lines_for_embed(bait_lines), start=1):
        title_suffix = "" if idx == 1 else f" (Page {idx})"
        other_embed.add_field(
            name=f"━━━━ Bait{title_suffix} ━━━━",
            value=bait_chunk,
            inline=False
        )

    bowl = normalize_fish_bowl(user_data)
    slots = bowl.get("slots", 1)
    if slots < 10:
        other_embed.add_field(
            name="━━━━ Fish Bowl Upgrades ━━━━",
            value=(
                "**Fish Bowl Slot** — 2500 <:coin:1399146146315894825>\n"
                f"*Current slots: {slots}/10*\n"
                "Use `sq buy fish bowl slot` to buy +1 slot."
            ),
            inline=False
        )
    else:
        other_embed.add_field(
            name="━━━━ Fish Bowl Upgrades ━━━━",
            value="**Maxed out!** Your fish bowl is already at 10/10 slots.",
            inline=False
        )

    class ShopView(discord.ui.View):
        def __init__(self, author_id):
            super().__init__(timeout=180)
            self.author_id = author_id

        async def interaction_check(self, interaction: discord.Interaction):
            if interaction.user.id != self.author_id:
                await interaction.response.send_message(
                    "❌ This shop menu isn't for you.", ephemeral=True)
                return False
            return True

    view = ShopView(ctx.author.id)

    async def show_page(interaction, page_name):
        if page_name == "rods":
            await interaction.response.edit_message(embed=rods_embed, view=view)
        else:
            await interaction.response.edit_message(embed=other_embed, view=view)

    rods_button = discord.ui.Button(label="Rods", style=discord.ButtonStyle.primary)
    other_button = discord.ui.Button(label="Boosts + Bait + Fish Bowl", style=discord.ButtonStyle.secondary)

    async def rods_callback(interaction):
        await show_page(interaction, "rods")

    async def other_callback(interaction):
        await show_page(interaction, "other")

    rods_button.callback = rods_callback
    other_button.callback = other_callback

    view.add_item(rods_button)
    view.add_item(other_button)

    await ctx.send(embed=rods_embed, view=view)


@bot.command()
async def buy(ctx, *, item: str):
    user_data = get_user_data(ctx.author)

    parts = item.lower().split()
    qty = 1

    # if last word is a number, treat it as quantity
    if parts and parts[-1].isdigit():
        qty = int(parts[-1])
        parts = parts[:-1]

    item_name = " ".join(parts).strip()

    if qty < 1:
        await ctx.send("bro you can't buy a negative amount 💀")
        return

    # Fish bowl slot upgrade
    if item_name in {"fish bowl slot", "fishbowl slot", "bowl slot", "fish bowl"}:
        bowl = normalize_fish_bowl(user_data)
        if bowl.get("slots", 1) >= 10:
            await ctx.send("❌ Your fish bowl already has the max 10 slots.")
            return

        cost = 2500 * qty
        possible_slots = min(10, bowl.get("slots", 1) + qty)
        actual_bought = possible_slots - bowl.get("slots", 1)
        actual_cost = 2500 * actual_bought

        if user_data.get("gold", 0) < actual_cost:
            await ctx.send("❌ Not enough gold.")
            return

        user_data["gold"] -= actual_cost
        bowl["slots"] = possible_slots
        save_users()
        await ctx.send(
            f"✅ Bought **{actual_bought} fish bowl slot(s)** for {actual_cost} <:coin:1399146146315894825>. "
            f"Your bowl is now **{bowl['slots']}/10** slots."
        )
        return

    # ✅ Allow singular bait names (worm -> worms, leech -> leeches, etc.)
    if item_name not in baits:
        for bait_key, bait_data in baits.items():
            singular = (bait_data.get("singular") or "").lower().strip()
            if singular and item_name == singular:
                item_name = bait_key
                break

    # ── BOOSTS ──
    if item_name in boosts:
        required_rod_for_boost = {
            "extra love": "cupid rod",
            "deeper casts": "deep sea rod",
        }
        required_rod = required_rod_for_boost.get(item_name)
        equipped_rod = user_data.get("rod", "wooden rod")

        if required_rod and equipped_rod != required_rod:
            await ctx.send(
                f"❌ You can only buy **{item_name.title()}** while **{required_rod.title()}** is equipped."
            )
            return

        boost = boosts[item_name]
        cost = boost["price"] * qty

        if user_data.get("gold", 0) >= cost:
            user_data["gold"] -= cost
            # buying multiple boosts just extends the duration
            now = time.time()
            current_end = float(user_data["boosts"].get(item_name, 0) or 0)
            start_from = current_end if current_end > now else now
            user_data["boosts"][item_name] = start_from + (boost["duration"] * qty)

            qty_text = f" x{qty}" if qty > 1 else ""
            await ctx.send(
                f"✅ {ctx.author.display_name} bought **{item_name.title()}{qty_text}**!"
            )
        else:
            await ctx.send("❌ Not enough gold.")

    # ── RODS ──
    elif item_name in rods:
        rod = rods[item_name]
        cost = rod["price"] * qty

        if user_data.get("gold", 0) >= cost:
            user_data["gold"] -= cost
            user_data["rods"][item_name] = user_data["rods"].get(item_name, 0) + qty
            user_data["rod"] = item_name  # still equips it

            qty_text = f" x{qty}" if qty > 1 else ""
            await ctx.send(
                f"✅ {ctx.author.display_name} bought **{item_name.title()}{qty_text}** and equipped it!"
            )
        else:
            await ctx.send("❌ Not enough gold.")

    # ── BAITS ──
    elif item_name in baits:
        bait = baits[item_name]
        cost = bait["price"] * qty

        if user_data.get("gold", 0) < cost:
            await ctx.send("❌ Not enough gold.")
        else:
            user_data["gold"] -= cost
            inv = user_data.setdefault("inventory", {})
            inv[item_name] = inv.get(item_name, 0) + qty

            qty_text = f" x{qty}" if qty > 1 else ""
            bait_disp = format_bait_name(item_name, qty)

            await ctx.send(
                f"✅ {ctx.author.display_name} bought {bait['emoji']} **{bait_disp}{qty_text}**!\n"
                "• Use `sq bait <bait/none> <amount>` to equip it for fishing boosts."
            )

    else:
        await ctx.send("❌ Item not found.")

    save_users()


@bot.command(aliases=["boostoff", "disableboost"])
async def disable(ctx, *, boost_name: str):
    user_data = get_user_data(ctx.author)
    requested_boost = boost_name.lower().strip()

    if requested_boost not in boosts:
        await ctx.send(
            "❌ That boost doesn’t exist. Try `sq disable double cast` or `sq disable autosell`."
        )
        return

    active_boosts = user_data.get("boosts", {})
    if requested_boost not in active_boosts:
        await ctx.send(
            f"❌ You don’t have **{requested_boost.title()}** active right now."
        )
        return

    del active_boosts[requested_boost]
    save_users()

    await ctx.send(
        f"✅ {ctx.author.display_name} disabled **{requested_boost.title()}**."
    )

@bot.command(aliases=["bait"])
async def sq_bait(ctx, *, bait_name: str):
    user_data = get_user_data(ctx.author)
    parts = bait_name.lower().split()

    # ✅ Unequip bait
    if parts and parts[0] in ["none", "off", "remove", "unequip"]:
        old = user_data.get("bait")
        amt = int(user_data.get("bait_amount", 0) or 0)
        if old and amt > 0:
            inv = user_data.setdefault("inventory", {})
            inv[old] = inv.get(old, 0) + amt

        user_data["bait"] = None
        user_data["bait_uses"] = 0
        user_data["bait_amount"] = 0
        save_users()
        await ctx.send(f"✅ {ctx.author.display_name} unequipped their bait.")
        return

    # quantity at end (sq bait trippa snippa 10)
    qty = 1
    if parts and parts[-1].isdigit():
        qty = int(parts[-1])
        parts = parts[:-1]

    raw_name = " ".join(parts).strip()

    if qty < 1:
        await ctx.send("bro you can't equip a negative amount 💀")
        return

    # ✅ Map singular -> plural key in baits (worm -> worms, trippa snippa -> trippa snippas)
    bait_key = raw_name
    if bait_key not in baits:
        for k, data in baits.items():
            singular = (data.get("singular") or "").lower().strip()
            if singular and bait_key == singular:
                bait_key = k
                break

    if bait_key not in baits:
        await ctx.send("❌ That bait doesn’t exist.")
        return

    inv = user_data.setdefault("inventory", {})
    owned = int(inv.get(bait_key, 0))

    if owned < qty:
        await ctx.send(f"❌ You only own {owned} of that bait.")
        return

    # if switching bait types, return old equipped stack back to inventory first
    current = user_data.get("bait")
    if current and current != bait_key:
        old_amt = int(user_data.get("bait_amount", 0) or 0)
        if old_amt > 0:
            inv[current] = inv.get(current, 0) + old_amt

        user_data["bait_amount"] = 0
        user_data["bait_uses"] = 0

    # move from inventory -> equipped stack
    inv[bait_key] = owned - qty
    if inv[bait_key] <= 0:
        del inv[bait_key]

    user_data["bait"] = bait_key
    user_data["bait_amount"] = int(user_data.get("bait_amount", 0) or 0) + qty

    # if no active uses (first equip or after swap), roll uses
    if user_data.get("bait_uses", 0) <= 0:
        user_data["bait_uses"] = random.randint(5, 8)

    save_users()

    qty_text = f" x{qty}" if qty > 1 else ""
    bait_disp = format_bait_name(bait_key, qty)

    await ctx.send(
        f"✅ {ctx.author.display_name} equipped {baits[bait_key]['emoji']} **{bait_disp}{qty_text}**!\n"
        f"• Stack remaining: **{user_data['bait_amount']}**"
    )

@bot.command()
async def sell(ctx, *, args: str):
    user_data = get_user_data(ctx.author)
    parts = args.lower().split()
    inv = user_data["inventory"]

    total = 0
    sold_message = ""
    contract_completion = None

    # ✅ special case: "sq sell all fish"
    if parts == ["all", "fish"]:
        sold_fish = []
        for fish in fish_pool:
            name = fish["name"]
            count = inv.get(name, 0)
            if count > 0:
                gold = int(
                    fish["xp"] * count * (1 + rods.get(user_data.get("rod", "wooden rod"), {}).get("bonus", 0))
                )
                total += gold
                inv[name] = 0
                sold_fish.append(f"{count} {name.title()}")

        if not sold_fish:
            await ctx.send("❌ You have no fish to sell.")
            return

        sold_message = (
            f"{ctx.author.display_name} sold {', '.join(sold_fish)} to the fisherman for "
            f"{total} gold <:coin:1399146146315894825>"
        )

    # ✅ special case: "sq sell all treasure"
    elif parts == ["all", "treasure"]:
        sold_treasures = []
        for treasure_name, treasure_data in treasure_index.items():
            if treasure_name == ONE_PIECE_NAME:
                continue
            count = inv.get(treasure_name, 0)
            if count > 0:
                gold = sum(get_treasure_sell_value(treasure_name) for _ in range(count))
                total += gold
                inv[treasure_name] = 0

                user_data.setdefault("treasures", {})
                if treasure_name in user_data["treasures"]:
                    user_data["treasures"][treasure_name] = max(
                        0, user_data["treasures"][treasure_name] - count
                    )
                    if user_data["treasures"][treasure_name] <= 0:
                        user_data["treasures"].pop(treasure_name, None)

                sold_treasures.append(f"{count} {treasure_name.title()}")
                contract_completion = contract_completion or update_contract_progress(user_data, "sell_treasure", count)

        if not sold_treasures:
            await ctx.send("❌ You have no treasure to sell.")
            return

        sold_message = (
            f"{ctx.author.display_name} sold {', '.join(sold_treasures)} to the treasure hoarder for "
            f"{total} gold <:coin:1399146146315894825>"
        )

    else:
        if not parts:
            await ctx.send(
                "❌ Please specify an item name. Example: `sq sell chad fish` or `sq sell amber pendant all`"
            )
            return

        # ✅ amount is OPTIONAL
        amount_arg = None
        name_parts = parts

        last = parts[-1]
        if last == "all" or last.isdigit():
            amount_arg = last
            name_parts = parts[:-1]

        name = " ".join(name_parts).strip()

        # ✅ Allow singular bait names (worm -> worms etc)
        if name not in inv:
            for bait_key, bait_data in baits.items():
                singular = (bait_data.get("singular") or "").lower().strip()
                if singular and name == singular:
                    name = bait_key
                    break

        if not name:
            await ctx.send("❌ Please specify an item name.")
            return

        # default amount
        if amount_arg is None:
            count = 1
        elif amount_arg == "all":
            count = inv.get(name, 0)
        else:
            count = int(amount_arg)

        if name not in inv or inv[name] < count or count <= 0:
            await ctx.send("❌ Check the amount of that item you have.")
            return

        # ── FISH ──
        fish = next((f for f in fish_pool if f["name"] == name), None)
        if fish:
            gold = int(
                fish["xp"] * count * (1 + rods.get(user_data.get("rod", "wooden rod"), {}).get("bonus", 0))
            )
            total = gold
            inv[name] -= count
            sold_message = (
                f"{ctx.author.display_name} sold {count} {name.title()} to the fisherman for "
                f"{total} gold <:coin:1399146146315894825>"
            )

        # ── TREASURES ──
        elif name in treasure_index:
            if name == ONE_PIECE_NAME or not treasure_index[name].get("sellable", True):
                await ctx.send("❌ You can't sell that treasure.")
                return
            total = sum(get_treasure_sell_value(name) for _ in range(count))
            inv[name] -= count
            if inv[name] <= 0:
                del inv[name]

            user_data.setdefault("treasures", {})
            if name in user_data["treasures"]:
                user_data["treasures"][name] -= count
                if user_data["treasures"][name] <= 0:
                    user_data["treasures"].pop(name, None)

            sold_message = (
                f"{ctx.author.display_name} sold {count} {name.title()} to the treasure hoarder for "
                f"{total} gold <:coin:1399146146315894825>"
            )
            contract_completion = contract_completion or update_contract_progress(user_data, "sell_treasure", count)

        # ── BAITS ── (75% resale value)
        elif name in baits:
            price = baits[name]["price"]
            sell_price = int(price * 0.75)
            total = sell_price * count
            inv[name] -= count

            if inv[name] <= 0:
                del inv[name]

            sold_message = (
                f"{ctx.author.display_name} sold {count} {format_bait_name(name, count)} to the fisherman for "
                f"{total} gold <:coin:1399146146315894825>"
            )

        else:
            await ctx.send("❌ That item can't be sold here.")
            return

    user_data["gold"] = user_data.get("gold", 0) + total
    await ctx.send(sold_message)
    await send_contract_completion_embed(ctx, contract_completion)
    save_users()

@bot.command(name="use")
async def use_item(ctx, *, item_name: str):
    user_data = get_user_data(ctx.author)
    inv = user_data.setdefault("inventory", {})
    key = item_name.lower().strip()

    if key != ONE_PIECE_NAME:
        await ctx.send("❌ You can't use that item.")
        return

    if int(inv.get(ONE_PIECE_NAME, 0)) < 1:
        await ctx.send("❌ You don't have The One Piece.")
        return

    inv[ONE_PIECE_NAME] -= 1
    if inv[ONE_PIECE_NAME] <= 0:
        del inv[ONE_PIECE_NAME]

    if ONE_PIECE_NAME in user_data.get("treasures", {}):
        user_data["treasures"][ONE_PIECE_NAME] -= 1
        if user_data["treasures"][ONE_PIECE_NAME] <= 0:
            user_data["treasures"].pop(ONE_PIECE_NAME, None)

    user_data["time_travels"] = int(user_data.get("time_travels", 0)) + 1
    save_users()
    await ctx.send(f"🏴‍☠️ You used **The One Piece**. Time Travels are now **{user_data['time_travels']}**.")


async def attempt_time_travel(ctx):
    user_data = get_user_data(ctx.author)
    has_mots = has_badge(user_data, MASTER_OF_THE_SEA_BADGE["name"])
    has_lts = has_badge(user_data, LEGENDARY_TREASURE_SEEKER_BADGE["name"]) or has_badge(user_data, MASTER_TREASURE_SEEKER_ALIAS)

    if not (has_mots and has_lts):
        await ctx.send("You can't do that yet! Check the time travel guide to check out why.")
        return

    current_time_travels = int(user_data.get("time_travels", 0))
    time_travel_cost = TIME_TRAVEL_BASE_COST + (TIME_TRAVEL_COST_STEP * current_time_travels)

    if int(user_data.get("gold", 0)) < time_travel_cost:
        await ctx.send(f"❌ Time travel costs **{time_travel_cost}** gold.")
        return

    now = time.time()
    if now - float(user_data.get("tt_confirm", 0)) > 20:
        user_data["tt_confirm"] = now
        save_users()
        await ctx.send("⚠️ Time travel will reset your items, valuables, and progression. Run the command again within 20 seconds to confirm.")
        return

    user_data["gold"] -= time_travel_cost
    user_data["xp"] = 0
    user_data["level"] = 1
    user_data["inventory"] = {}
    user_data["rods"] = {"wooden rod": 1}
    user_data["rod"] = "wooden rod"
    user_data["total_fish"] = 0
    user_data["boosts"] = {}
    user_data["chests"] = {}
    user_data["treasures"] = {}
    user_data["bait"] = None
    user_data["bait_uses"] = 0
    user_data["bait_amount"] = 0
    user_data["fish_bowl"] = None
    user_data["trophy_room"] = {}
    user_data["treasure_trophy_room"] = {}
    user_data["badges"] = []
    user_data["contract"] = None
    user_data["contracts_meta"] = {}
    user_data["time_travels"] = int(user_data.get("time_travels", 0)) + 1
    user_data["tt_confirm"] = 0

    uid = str(ctx.author.id)
    cooldowns.pop(uid, None)
    adventure_cooldowns.pop(uid, None)
    net_cooldowns.pop(uid, None)
    dig_cooldowns.pop(uid, None)
    save_cooldowns()
    save_users()
    await ctx.send(f"🕒 {ctx.author.display_name} time traveled! Permanent rare fish odds increased. Total Time Travels: **{user_data['time_travels']}**.")


@bot.command(name="tt")
async def tt(ctx):
    await attempt_time_travel(ctx)


@bot.group(name="time", invoke_without_command=True)
async def time_group(ctx):
    await attempt_time_travel(ctx)


@time_group.command(name="travel")
async def time_travel_sub(ctx):
    await attempt_time_travel(ctx)


@bot.command(name="contracts")
async def contracts_cmd(ctx):
    user_data = get_user_data(ctx.author)
    rotation_ts, catalog = make_contract_catalog_for_user(user_data, ctx.author.id)
    now = time.time()

    last_bought = float(user_data.get("contracts_meta", {}).get("last_bought", 0))
    can_buy_in = max(0, (last_bought + 4 * 3600) - now)

    contract_lines = []
    for key in ["A", "B", "C"]:
        c = catalog[key]
        goal_text = format_contract_goal(c["goal"])
        contract_lines.append(
            f"**{key}.** {c['price']} <:coin:1399146146315894825>\n"
            f"Goal: {goal_text}\n"
            f"Reward: {format_contract_reward(c.get('reward', {}))}"
        )

    if user_data.get("contract"):
        active = user_data["contract"]
        time_left = max(0, active['expires_at'] - now)
        active_line = (
            f"**{active['label']}** ({active['progress']}/{active['goal']['target']})\n"
            f"Goal: {format_contract_goal(active['goal'])}\n"
            f"Expires in {format_duration(time_left)}"
        )
    else:
        active_line = "None"

    cd_line = "Ready to buy a contract" if can_buy_in <= 0 else f"Next purchase in {format_duration(can_buy_in)}"

    embed = discord.Embed(
        title="📜 Faction Contracts",
        description="Do `sq contract accept <A/B/C>` to buy a contract. You can buy one contract every 4 hours. Each contract expires after 1 hour.",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="Available Contracts", value="\n\n".join(contract_lines), inline=False)
    embed.add_field(name="Active Contract", value=active_line, inline=False)
    embed.add_field(name="Purchase Cooldown", value=cd_line, inline=False)
    await ctx.send(embed=embed)


@bot.group(name="contract", invoke_without_command=True)
async def contract_group(ctx):
    await contracts_cmd(ctx)


@contract_group.command(name="accept")
async def contract_accept(ctx, contract_letter: str):
    user_data = get_user_data(ctx.author)
    letter = contract_letter.upper().strip()
    if letter not in {"A", "B", "C"}:
        await ctx.send("❌ Contract must be A, B, or C.")
        return

    now = time.time()
    meta = user_data.setdefault("contracts_meta", {})
    last_bought = float(meta.get("last_bought", 0))
    if now < last_bought + 4 * 3600:
        await ctx.send(f"❌ You can buy another contract in {format_duration((last_bought + 4*3600) - now)}.")
        return

    if user_data.get("contract"):
        await ctx.send("❌ Finish your current contract first.")
        return

    _, catalog = make_contract_catalog_for_user(user_data, ctx.author.id)
    picked = catalog[letter]
    price = int(picked["price"])
    if int(user_data.get("gold", 0)) < price:
        await ctx.send("❌ Not enough gold.")
        return

    user_data["gold"] -= price
    user_data["contract"] = {
        "label": letter,
        "goal": picked["goal"],
        "progress": 0,
        "reward": picked.get("reward", {}),
        "expires_at": now + 3600,
    }
    meta["last_bought"] = now
    save_users()
    await ctx.send(
        f"✅ Accepted contract **{letter}**. You have 1 hour to finish it.\n"
        f"Goal: {format_contract_goal(picked['goal'])}"
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def clear_all_stats(ctx):
    global users
    users = {}
    save_users()
    await ctx.send("✅ All user stats cleared.")


@bot.command(name="down")
@commands.is_owner()
async def down(ctx):
    bot_state["lockdown"] = True
    bot_state["allowed_user_id"] = ctx.author.id
    save_bot_state()
    await ctx.send("🔒 Private testing mode enabled. Only you can use commands now.")


@bot.command(name="up")
@commands.is_owner()
async def up(ctx):
    bot_state["lockdown"] = False
    bot_state["allowed_user_id"] = None
    save_bot_state()
    await ctx.send("🔓 Private testing mode disabled. Everyone can use commands now.")


@bot.command(aliases=["i", "inv"])
async def inventory(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_data = get_user_data(member)
    inventory = user_data.get("inventory", {})
    avatar = member.avatar.url if member.avatar else None

    fish_lines = []
    for fish in fish_pool:
        name = fish["name"]
        emoji = fish["emoji"]
        count = inventory.get(name, 0)
        if count > 0:
            fish_lines.append(f"{emoji} {name} — {count}")

    treasure_lines = []
    for treasure_name, treasure_data in treasure_index.items():
        count = inventory.get(treasure_name, 0)
        if count > 0:
            treasure_lines.append(
                f"{treasure_data['emoji']} {treasure_name.title()} — {count}"
            )

    bait_lines = []
    equipped_bait = (user_data.get("bait") or "").lower().strip()
    equipped_amt = int(user_data.get("bait_amount", 0) or 0)

    for bait_name in baits:
        owned = int(inventory.get(bait_name, 0))

        if bait_name == equipped_bait and equipped_amt > 0:
            total_amt = owned + equipped_amt  # ✅ use total for correct singular/plural
            bait_lines.append(
                f"{baits[bait_name]['emoji']} {format_bait_name(bait_name, total_amt)} — {owned} *(+{equipped_amt} Equipped)*"
            )
        else:
            if owned > 0:
                bait_lines.append(
                    f"{baits[bait_name]['emoji']} {format_bait_name(bait_name, owned)} — {owned}"
                )

    chest_lines = []
    for name, data in chests.items():
        count = user_data.get("chests", {}).get(name, 0)
        if count > 0:
            chest_lines.append(f"{data['emoji']} {name.title()} — {count}")

    embed = discord.Embed(title=f"{member.display_name}'s Inventory",
                          color=discord.Color.green())
    if avatar:
        embed.set_thumbnail(url=avatar)

    embed.add_field(
        name="━━━━ <:backpack:1399064953239109723> Backpack ━━━━",
        value="\n".join(fish_lines) if fish_lines else "Inventory is empty.",
        inline=False
    )

    if treasure_lines:
        embed.add_field(
            name="━━━━ Treasures ━━━━",
            value="\n".join(treasure_lines),
            inline=False
        )

    if chest_lines:
        embed.add_field(
            name="━━━━ Chests ━━━━",
            value="\n".join(chest_lines),
            inline=False
        )

    if bait_lines:
        embed.add_field(
            name="━━━━ Baits ━━━━",
            value="\n".join(bait_lines),
            inline=False
        )

    await ctx.send(embed=embed)


@bot.command(aliases=["fishindex", "fi"])
async def fish_index(ctx, *, mode: str = None):
    mode = (mode or "").strip().lower()
    user_data = get_user_data(ctx.author)

    show_personal = mode == "me"
    personal_odds = build_personal_fish_odds(user_data) if show_personal else []

    lines = []
    for idx, fish in enumerate(fish_pool):
        emoji = fish["emoji"]
        name = fish["name"].title()
        rarity = personal_odds[idx][1] if show_personal else fish["chance"]
        base_gold = fish["xp"]  # or multiply if you want
        lines.append(
            f"{emoji} **{name}** — {rarity:.3f}% chance — {base_gold} <:coin:1399146146315894825>"
        )

    title = "Fish Index (Personal Odds)" if show_personal else "Fish Index"
    embed = discord.Embed(title=title,
                          description="\n".join(lines),
                          color=discord.Color.blue())

    if show_personal:
        bait_name = user_data.get("bait")
        bait_active = bait_name and user_data.get("bait_uses", 0) > 0
        bait_text = bait_name.title() if bait_active else "None"
        bowl_mult = get_fishbowl_multiplier(user_data)
        embed.set_footer(
            text=(
                f"Personal odds shown using your active bait ({bait_text}) and fish bowl bonus ({((bowl_mult - 1) * 100):.1f}%). "
                "Fishing rods do not affect rare fish odds."
            ))
    else:
        embed.set_footer(
            text=(
                "*Coins represent base selling price before boosts. XP values are equivalent to base gold price. "
                "Use `sq fi me` to view your personal fish odds.*"
            ))

    await ctx.send(embed=embed)


@bot.command(aliases=["ti", "treasureindex"])
async def treasure_list_index(ctx):
    sorted_treasures = sorted(
        (
            (name, data)
            for name, data in treasure_index.items()
            if name != ONE_PIECE_NAME
        ),
        key=lambda item: (item[1].get("min_value", item[1].get("value", 0)), item[0])
    )

    lines = []
    for name, data in sorted_treasures:
        min_value = int(data.get("min_value", data.get("value", 0)))
        max_value = int(data.get("max_value", min_value))
        value_text = f"{min_value}-{max_value}" if max_value != min_value else f"{min_value}"
        lines.append(
            f"{data['emoji']} **{name.title()}** — {value_text} <:coin:1399146146315894825>"
        )

    embed = discord.Embed(
        title="Treasure Index",
        description="\n".join(lines),
        color=discord.Color.gold()
    )
    embed.set_footer(text="Treasures are listed from lowest to highest minimum sell price.")
    await ctx.send(embed=embed)


@bot.command(aliases=["ci", "chestindex"])
async def chest_index(ctx):
    lines = []
    previous_max_tier = 0

    for name, chest in chests.items():
        emoji = chest["emoji"]
        rewards = chest["rewards"]

        gold_min, gold_max = rewards["gold"]
        xp_min, xp_max = rewards["xp"]

        treasure_config = rewards.get("treasures")
        treasure_text = ""

        if treasure_config:
            max_tier = treasure_config["max_tier"]
            min_tier = previous_max_tier + 1

            possible = [
                f"{treasure_index[t]['emoji']} {t.title()}"
                for t, data in treasure_index.items()
                if min_tier <= data["tier"] <= max_tier
            ]

            if possible:
                if min_tier <= 1:
                    treasure_text = "\n**Tier 1 & 2 Treasures:**\n" + ", ".join(possible)
                else:
                    treasure_text = f"\n**+ Tier {min_tier} Treasures:**\n" + ", ".join(possible)

            previous_max_tier = max_tier
        extra_text = ""
        if name == "deep sea chest":
            extra_text = "\n**Special:** <:one_piece:1479927612104249569> The One Piece"

        lines.append(
            f"{emoji} __**{name.title()}**__\n"
            f"<:coin:1399146146315894825> Gold: {gold_min}–{gold_max} | "
            f"<:level:1399200622779302004> XP: {xp_min}–{xp_max}"
            f"{treasure_text}{extra_text}"
        )

    embed = discord.Embed(
        title="Chest Index",
        description="\n\n".join(lines),
        color=discord.Color.gold()
    )

    embed.set_footer(text="Treasures listed are based on chest tier limits")
    await ctx.send(embed=embed)


@bot.command()
async def guide(ctx):
    def build_guide_embed(title, description, fields):
        embed = discord.Embed(title=title, description=description, color=discord.Color.green())
        for field_name, field_value in fields:
            embed.add_field(name=field_name, value=field_value, inline=False)
        return embed

    home_embed = build_guide_embed("📘 Ship Quest Guide", None, [])

    fishing_cmds = [
        "sq cast – Cast your rod for a fish",
        "sq net - Throw out a fishing net for a big catch",
        "sq adv / sq adventure – Go on an adventure to find chests",
        "sq bait <bait/none> <amount> – Equip bait to increase odds of catching better fish",
        "sq dig – Dig for a chance to find bait in the ground",
        "sq fi / sq fish index – View list of fish and their stats (use sq fi me for personal, weighted odds)",
        "sq ci / sq chest index – View list of chests and their possible contents",
        "sq ti / sq treasure index – View treasures sorted by minimum sell value",
        "sq open <chest/all> – Open a specific chest type or all chests from your inventory",
        "sq open all chest – Open every chest in your inventory",
        "sq sell <item> – Sell fish, treasures, or bait for gold",
        "sq disable <boost> - Disable an active boost",
    ]
    home_embed.add_field(
        name=
        "━━━━ <:wooden_rod:1399044497068920912> Fishing & Loot Commands <:chest:1399491916978192406> ━━━━",
        value="\n".join(fishing_cmds),
        inline=False)

    inventory_cmds = [
        "sq p / sq profile – View profile",
        "sq i / sq inventory – View Inventory",
        "sq fish bowl – View fish bowl guide for details!",
        "sq tr / sq trophy / sq trophy room / sq trophyroom – View your trophy room fish collection",
        "sq trophy room – View trophy room guide for details!",
        "sq shop – Where you can buy rods, boosts, and more",
        "sq buy <item> – Buy rods, boosts, bait, and fish bowl upgrades",
        "sq cd / sq cooldown – Check cooldowns & see active boosts",
        "sq contracts – View rotating faction contracts",
        "sq contract accept <A/B/C> – Buy & accept a listed contract",
        "sq tt / sq time travel – Reset progress for permanent rare fish odds"
    ]
    home_embed.add_field(name="━━━━ Inventory & Shops ━━━━",
                    value="\n".join(inventory_cmds),
                    inline=False)

    misc_cmds = ["sq guide – You're already here brev so idk what to tell u"]
    home_embed.add_field(name="━━━━ Miscellaneous ━━━━",
                    value="\n".join(misc_cmds),
                    inline=False)

    tutorial_pages = {
        "Fish Bowls": build_guide_embed(
            "📘 Guide Tutorial: Fish Bowls",
            "\n".join([
                "-Having fish in a bowl allows players to increase their odds of finding rarer fish!",
                "-You can enter a fish into your bowl by using `sq fish bowl <fish> <nickname>`.",
                "-The rarer the fish that a player has in their bowl, the more of a % boost they'll be given.",
                "-Players can have up to 10 fish in their bowl at once, and can name them to make them unique!",
                "-You start with 1 free slot, and can buy up to 9 more from the shop with `sq buy fish bowl slot` for 2500 gold each.",
                "-Do `sq fish bowl remove <nickname>` to remove a fish from your bowl. This fish will return to your inventory.",
            ]),
            []),
        "Trophy Rooms": build_guide_embed(
            "📘 Guide Tutorial: Trophy Rooms",
            "\n".join([
                "-Trophy rooms now have 2 pages: fish trophy room and treasure trophy room.",
                "-To add fish to your trophy room, use `sq trophy add <fish> <amount>`",
                "-Use `sq trophy` or `sq trophy room` then switch pages with the buttons at the bottom.",
                "Use `sq trophy add treasure <treasure> <amount>` to add treasures to the treasure room.",
            ]),
            []),
                "Time Travel": build_guide_embed(
            "📘 Guide Tutorial: Time Travel",
            "\n".join([
                "-Time travel unlocks when you own both badge rewards from the two trophy rooms.",
                "-Required badges: Master of the Sea + Legendary Treasure Seeker.",
                "-Use `sq tt` or `sq time travel` to time travel.",
                "-Time travel cost starts at 100000 gold and increases by 25000 per time travel.",
                "-Time travel resets your items, valuables, rods, trophies, and progression.",
                "-Each time travel gives a permanent +10% rare fish odds boost.",
            ]),
            []),
    }

    class GuideView(discord.ui.View):
        def __init__(self, author_id):
            super().__init__(timeout=180)
            self.author_id = author_id

        async def interaction_check(self, interaction: discord.Interaction):
            if interaction.user.id != self.author_id:
                await interaction.response.send_message(
                    "❌ This guide menu isn't for you.", ephemeral=True)
                return False
            return True

    view = GuideView(ctx.author.id)

    async def show_page(interaction, page_name):
        if page_name == "home":
            await interaction.response.edit_message(embed=home_embed, view=view)
        else:
            await interaction.response.edit_message(embed=tutorial_pages[page_name], view=view)

    home_button = discord.ui.Button(label="Main Guide", style=discord.ButtonStyle.primary)

    async def home_callback(interaction):
        await show_page(interaction, "home")

    home_button.callback = home_callback
    view.add_item(home_button)

    for page_name in tutorial_pages:
        button = discord.ui.Button(label=page_name, style=discord.ButtonStyle.secondary)

        async def page_callback(interaction, selected_page=page_name):
            await show_page(interaction, selected_page)

        button.callback = page_callback
        view.add_item(button)

    await ctx.send(embed=home_embed, view=view)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("❌ Only the bot owner can use this command.")
        return

    raise error


keep_alive()

bot.run(TOKEN)
