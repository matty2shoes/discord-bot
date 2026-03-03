import discord
from discord.ext import commands
import random
import time
import os
import json
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

app = Flask('')

 
@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


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

users_file = "users.json"

fish_pool = [{
    "name": "fish",
    "emoji": "<:fish:1399192790797127861>",
    "xp": 1,
    "chance": 59.00
}, {
    "name": "chad fish",
    "emoji": "<:chadfish:1399043761413292103>",
    "xp": 30,
    "chance": 10.00
}, {
    "name": "bebeto bass",
    "emoji": "<:bebeto_bass:1399043708879376405>",
    "xp": 50,
    "chance": 8.00
}, {
    "name": "superman shark",
    "emoji": "<:superman_shark:1399164285657022566>",
    "xp": 60,
    "chance": 7.00
}, {
    "name": "benjafish",
    "emoji": "<:benjafish:1399050676063043594>",
    "xp": 70,
    "chance": 5.00
}, {
    "name": "puffer sid",
    "emoji": "<:sid_pufferfish:1399144009175138426>",
    "xp": 80,
    "chance": 4.00
}, {
    "name": "slamuel sunny",
    "emoji": "<:slamuel_sunny:1399043599445790800>",
    "xp": 100,
    "chance": 3.00
}, {
    "name": "nateinator",
    "emoji": "<:nateinator:1399043897044369440>",
    "xp": 150,
    "chance": 2.00
}, {
    "name": "kermit lefish",
    "emoji": "<:kermit_lefish:1399158630023954452>",
    "xp": 200,
    "chance": 1.00
}, {
    "name": "mojicuslitus",
    "emoji": "<:mojicuslitus:1399194815517688052>",
    "xp": 300,
    "chance": 0.90
}, {
    "name": "SUPER RARE LAM CHAD FISH EXTREME",
    "emoji": "<:slam_extreme:1399043820884066344>",
    "xp": 2500,
    "chance": 0.09
}, {
    "name": "fih",
    "emoji": "<:fih:1399044570888671262>",
    "xp": 7500,
    "chance": 0.01
}]

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
    }
}

treasure_index = {
    "amber pendant": {
        "emoji": "<:amber_pendant:1400307044514533386>",
        "value": 150,
        "tier": 1
    },
    "ruby ring": {
        "emoji": "<:ruby_ring:1400307346093117624>",
        "value": 200,
        "tier": 1
    },
    "apatite shard": {
        "emoji": "<:apatite_shard:1400306918634819604>",
        "value": 350,
        "tier": 2
    },
    "pearl necklace": {
        "emoji": "<:pearl_necklace:1400306812435300393>",
        "value": 500,
        "tier": 3
    },
    "golden chalice": {
        "emoji": "<:golden_chalice:1400306658995081247>",
        "value": 2000,
        "tier": 4
    },
    "glass eye": {
        "emoji": "<:glass_eye:1400306719275487322>",
        "value": 4000,
        "tier": 5
    },
    "soup dumpling": {
        "emoji": "<:soup_dumpling:1477453212868018450>",
        "value": 15000,
        "tier": 6
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
                "count": (2, 2),
                "max_tier": 6,
                "rarity_bias": 0.3
            }
        },
    },
}

baits = {
    "worms": {
        "emoji": "<:worm_bait:1477701918573990030>",
        "price": 75,
        "multiplier": 1.06,
        "singular": "worm"
    },
    "leeches": {
        "emoji": "<:leech_bait:1477701943483957431>",
        "price": 200,
        "multiplier": 1.12,
        "singular": "leech"
    },
    "trippa snippas": {
        "emoji": "<:trippa_snippa_bait:1477701970063134850>",
        "price": 300,
        "multiplier": 1.18,
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
    

    save_users()
    return users[uid]


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
    bowl = user_data.get("fish_bowl")
    if not bowl:
        return 1.0

    fish_name = bowl.get("fish")
    if not fish_name:
        return 1.0

    fish = next((f for f in fish_pool if f["name"] == fish_name), None)
    if not fish:
        return 1.0

    c = float(fish.get("chance", 0))

    # Stronger boosts for rarer bowl fish
    # (tweak these numbers anytime)
    if c <= 0.01:
        return 1.12  # fih tier
    if c <= 0.10:
        return 1.10
    if c <= 1.00:
        return 1.06
    if c <= 5.00:
        return 1.03
    if c <= 15.00:
        return 1.01
    return 1.02


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
    outcomes = ["nothing", "worms", "leeches", "trippa snippas"]
    weights = [30, 40, 20, 10]
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
        second = random.choice(["worms", "leeches", "trippa snippas"])
        inv[second] = inv.get(second, 0) + 1

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

@bot.group(invoke_without_command=True)
async def fish(ctx):
    await ctx.send("Use `sq fish bowl <fish> <nickname>` (or `sq fish bowl` to view).")


@fish.command(name="bowl")
async def fish_bowl(ctx, *, args: str = None):
    user_data = get_user_data(ctx.author)
    inv = user_data.setdefault("inventory", {})

    # VIEW current bowl
    if not args:
        bowl = user_data.get("fish_bowl")
        if not bowl:
            await ctx.send("Your fish bowl is empty. Use `sq fish bowl <fish> <nickname>`.")
            return

        fish_name = bowl.get("fish")
        nick = bowl.get("nick") or "Unnamed"
        fish_obj = next((f for f in fish_pool if f["name"] == fish_name), None)

        if not fish_obj:
            await ctx.send("Your fish bowl has an invalid fish saved (tell Matt to fix 💀).")
            return

        mult = get_fishbowl_multiplier(user_data)
        percent = int(round((mult - 1) * 100))

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Fishbowl",
            description=f"{fish_obj['emoji']} **{nick}**\n+{percent}% Rare Fish Odds",
            color=discord.Color.from_rgb(255, 255, 255)
        )
        await ctx.send(embed=embed)
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

    # Must own the fish in inventory to put it in bowl
    if inv.get(chosen_fish, 0) < 1:
        await ctx.send("❌ You don’t have that fish in your inventory.")
        return

    # If they already had a bowl fish, return it to inventory first
    old = user_data.get("fish_bowl")
    if old and old.get("fish"):
        old_fish = old["fish"]
        inv[old_fish] = inv.get(old_fish, 0) + 1

    # Move 1 fish into the bowl
    inv[chosen_fish] -= 1
    if inv[chosen_fish] <= 0:
        del inv[chosen_fish]

    user_data["fish_bowl"] = {"fish": chosen_fish, "nick": chosen_nick}

    fish_obj = next((f for f in fish_pool if f["name"] == chosen_fish), None)
    mult = get_fishbowl_multiplier(user_data)
    percent = int(round((mult - 1) * 100))

    embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Fishbowl",
        description=f"{fish_obj['emoji']} **{chosen_nick}**\n+{percent}% Rare Fish Odds",
        color=discord.Color.from_rgb(255, 255, 255)
    )

    save_users()
    await ctx.send(embed=embed)

@bot.command()
async def net(ctx):
    user_id = str(ctx.author.id)
    user_data = get_user_data(ctx.author)
    now = time.time()

    if user_id in net_cooldowns and now - net_cooldowns[user_id] < 3600:
        remaining = 3600 - (now - net_cooldowns[user_id])
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

    rarity_mult = get_fishbowl_multiplier(user_data)
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
        f"{ctx.author.display_name} threw out a fishing net and caught **{catch_amount} fish!**\n\n"
        + "\n".join(summary_lines),
        color=discord.Color.teal())

    reward_text = f"<:level:1399200622779302004> XP: +{total_xp}\n"

    if has_boost(user_data, "autosell"):
        reward_text += f"💰 Sold with Autosell for {total_gold} Gold <:coin:1399146146315894825>\n"

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

    if user_id in adventure_cooldowns:
        elapsed = now - adventure_cooldowns[user_id]
        if elapsed < 7200:
            remaining = int((7200 - elapsed) // 60)
            await ctx.send(
                "🕓 You can not adventure again yet, check cooldown with 'sq cd'"
            )
            return

    adventure_cooldowns[user_id] = time.time()
    save_cooldowns()

    chest_names = list(chests.keys())
    weights = [50, 20, 15, 10, 5]

    chosen_name = random.choices(chest_names, weights=weights)[0]
    chest_data = chests[chosen_name]
    emoji = chest_data["emoji"]

    user_data["chests"][chosen_name] = user_data["chests"].get(chosen_name,
                                                               0) + 1

    embed = discord.Embed(
        title="🗺️ Adventure Complete!",
        description=
        f"{ctx.author.display_name} found a {emoji} **{chosen_name.title()}**!",
        color=discord.Color.orange())
    await ctx.send(embed=embed)
    save_users()

@bot.command()
async def cast(ctx):
    user_id = str(ctx.author.id)
    user_data = get_user_data(ctx.author)
    now = time.time()

    if user_id in cooldowns and now - cooldowns[user_id] < 30:
        remaining = round(30 - (now - cooldowns[user_id]), 1)
        await ctx.send(
            f"⏳ {ctx.author.display_name}, you need to wait {remaining}s before fishing again."
        )
        return

    casts = 2 if has_boost(user_data, "double cast") else 1
    cooldowns[user_id] = time.time()
    save_cooldowns()
    level_ups = 0

    equipped_rod = user_data.get("rod", "wooden rod")
    rod_data = rods.get(equipped_rod, {})
    gold_bonus = rod_data.get("bonus", 0)
    rarity_bonus = rod_data.get("rarity_bonus", 0)

    results = []
    for _ in range(casts):

        rarity_mult = 1.0

        # bait rarity boost
        if user_data.get("bait") and user_data.get("bait_uses", 0) > 0:
            bait_name = user_data["bait"]
            rarity_mult *= float(baits[bait_name]["multiplier"])

        # fish bowl rarity boost
        rarity_mult *= get_fishbowl_multiplier(user_data)

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

        gold_earned = 0

        if has_boost(user_data, "autosell"):
            gold_earned = int(xp * (1 + gold_bonus))
            user_data["gold"] += gold_earned
        else:
            user_data["inventory"][name] = user_data["inventory"].get(name, 0) + 1
            gold_earned = int(xp * (1 + gold_bonus))

        new_level, xp_into_level, next_level_xp = get_level_info(user_data["xp"])
        if new_level > user_data.get("level", 1):
            level_ups += new_level - user_data.get("level", 1)
            user_data["level"] = new_level
            results.append(
                f"🎉 {ctx.author.display_name} leveled up to **Level {new_level}**!"
            )

        result = f"<:cast_bobber:1399044610684096726> {ctx.author.display_name} caught a **{emoji} {name}**!\n<:level:1399200622779302004> XP: +{xp}"
        if has_boost(user_data, "autosell"):
            result += f"\n💰 Sold instantly for {gold_earned} <:coin:1399146146315894825> (Autosell Active)"
        results.append(result)

    # ✅ STACKED BAIT LOGIC (auto-load next one)
    if user_data.get("bait") and user_data.get("bait_uses", 0) > 0:
        user_data["bait_uses"] -= 1

        if user_data["bait_uses"] <= 0:
            expired_bait = user_data["bait"]
            inv = user_data.setdefault("inventory", {})

            equipped_amt = int(user_data.get("bait_amount", 0) or 0)
            if equipped_amt > 0:
                equipped_amt -= 1
                user_data["bait_amount"] = equipped_amt

            # If they still have more of that bait equipped, instantly refresh uses
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

    # Support: sq open all (opens every chest type the user owns)
    if len(args_list) == 1 and args_list[0] == "all":
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
            title=f"🎁 {ctx.author.display_name} opened all their chests!",
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

    user_data["gold"] += total_gold
    user_data["xp"] += total_xp
    user_chests[chest_name] -= to_open

    new_level, xp_into_level, next_level_xp = get_level_info(user_data["xp"])
    level_up_text = ""
    if new_level > user_data.get("level", 1):
        level_up_text = f"\n🎉 You leveled up to **Level {new_level}**!"
        user_data["level"] = new_level

    embed = discord.Embed(
        title=
        f"{emoji} {ctx.author.display_name} opened {to_open} {chest_name.title()}{'s' if to_open > 1 else ''}!",
        color=discord.Color.gold())

    lines = []
    if found_treasures:
        treasure_lines = [
            f"{treasure_index[t]['emoji']} **{t.title()}**"
            for t in found_treasures
        ]
        lines.extend(treasure_lines)

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
    if user_id in cooldowns and now - cooldowns[user_id] < 30:
        cast_remaining = 30 - (now - cooldowns[user_id])

    adventure_remaining = 0
    if user_id in adventure_cooldowns and now - adventure_cooldowns[
            user_id] < 7200:
        adventure_remaining = 7200 - (now - adventure_cooldowns[user_id])

    net_remaining = 0
    if user_id in net_cooldowns and now - net_cooldowns[user_id] < 3600:
        net_remaining = 3600 - (now - net_cooldowns[user_id])

    dig_remaining = 0
    if user_id in dig_cooldowns and now - dig_cooldowns[user_id] < 600:
        dig_remaining = 600 - (now - dig_cooldowns[user_id])

    active_boosts = []
    emoji_map = {
        "double cast": "<:double_cast:1399044646700716154>",
        "autosell": "<:autosell:1399198067533680741>",
    }

    for boost in user_data.get("boosts", {}):
        remaining = user_data["boosts"][boost] - time.time()
        if remaining > 0:
            boost_name = boost.title() if boost != "autosell" else "Autosell"
            emoji = emoji_map.get(boost, "")
            active_boosts.append(
                f"{emoji} {boost_name} ({format_duration(remaining)} left)")

    boost_text = "\n".join(
        active_boosts) if active_boosts else "No boosts active"

    desc_lines = [
        f"{'✅ -- Cast' if cast_remaining == 0 else f'🕓 -- Cast ({format_duration(cast_remaining)})'}",
        f"{'✅ -- Dig' if dig_remaining == 0 else f'🕓 -- Dig ({format_duration(dig_remaining)})'}",
        f"{'✅ -- Net' if net_remaining == 0 else f'🕓 -- Net ({format_duration(net_remaining)})'}",
        f"{'✅ -- Adventure' if adventure_remaining == 0 else f'🕓 -- Adventure ({format_duration(adventure_remaining)})'}",
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

    embed = discord.Embed(
        title=f"{member.display_name}'s Profile",
        color=discord.Color.blue()
    )

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

    embed.add_field(
        name="━━━━━ Equipped Rod ━━━━━",
        value=f"{rod_data['emoji']} {rod.title()}\n*+ {gold_bonus_percent}% gold*{rarity_text}",
        inline=False
    )

    # Total fish
    total_fish = user_data.get("total_fish", 0)
    embed.add_field(
        name="━━ <:wooden_rod:1399044497068920912> Total Fish Caught ━━",
        value=f"{total_fish} <:fish:1399192790797127861>",
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

    equipped_rod = user_data.get("rod", "wooden")
    active_boosts = user_data.get("boosts", [])

    embed = discord.Embed(
        title="🛍️ Ship Quest Shop",
        color=discord.Color.red()
    )

    embed.add_field(
        name="Your Gold",
        value=gold_display,
        inline=False
    )

    # ━━━ RODS ━━━
    rod_lines = []
    for name, data in rods.items():
        bonus_percent = int(data.get("bonus", 0) * 100)

        tag = " *(Equipped)*" if name == equipped_rod else ""

        rod_lines.append(
            f"**{data['emoji']} {name.title()}** — {data['price']} <:coin:1399146146315894825>{tag}\n"
            f"*+ {bonus_percent}% gold on fish sell*"
        )

    embed.add_field(
        name="━━━━ Rods ━━━━",
        value="\n".join(rod_lines),
        inline=False
    )

    # ━━━ BOOSTS ━━━
    boost_lines = []
    for name, data in boosts.items():
        tag = " *(Active)*" if has_boost(user_data, name) else ""

        boost_lines.append(
            f"**{data['emoji']} {name.title()}** — {data['price']} <:coin:1399146146315894825>{tag}\n"
            f"*{data['description']}*"
        )

    embed.add_field(
        name="━━━━ <:boosts:1399198567486197791> Boosts ━━━━",
        value="\n".join(boost_lines),
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

    embed.add_field(
        name="━━━━ Bait ━━━━",
        value="\n".join(bait_lines),
        inline=False
    )

    await ctx.send(embed=embed)


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

    # ✅ Allow singular bait names (worm -> worms, leech -> leeches, etc.)
    if item_name not in baits:
        for bait_key, bait_data in baits.items():
            singular = (bait_data.get("singular") or "").lower().strip()
            if singular and item_name == singular:
                item_name = bait_key
                break

    # ── BOOSTS ──
    if item_name in boosts:
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
        user_data["bait_uses"] = random.randint(4, 7)

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
            value = treasure_index[name]["value"]
            total = value * count
            inv[name] -= count
            if inv[name] <= 0:
                del inv[name]
            sold_message = (
                f"{ctx.author.display_name} sold {count} {name.title()} to the treasure trader for "
                f"{total} gold <:coin:1399146146315894825>"
            )

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
    save_users()

@bot.command()
@commands.has_permissions(administrator=True)
async def clear_all_stats(ctx):
    global users
    users = {}
    save_users()
    await ctx.send("✅ All user stats cleared.")


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
async def fish_index(ctx):
    lines = []
    for fish in fish_pool:
        emoji = fish["emoji"]
        name = fish["name"].title()
        rarity = fish["chance"]
        base_gold = fish["xp"]  # or multiply if you want
        lines.append(
            f"{emoji} **{name}** — {rarity}% chance — {base_gold} <:coin:1399146146315894825>"
        )

    embed = discord.Embed(title="Fish Index",
                          description="\n".join(lines),
                          color=discord.Color.blue())
    embed.set_footer(
        text=
        "*Coins represent base selling price before boosts. XP values are equivalent to base gold price"
    )

    await ctx.send(embed=embed)


@bot.command(aliases=["ci", "chestindex"])
async def chest_index(ctx):
    lines = []

    for name, chest in chests.items():
        emoji = chest["emoji"]
        rewards = chest["rewards"]

        gold_min, gold_max = rewards["gold"]
        xp_min, xp_max = rewards["xp"]

        treasure_config = rewards.get("treasures")
        treasure_text = ""

        if treasure_config:
            max_tier = treasure_config["max_tier"]

            possible = [
                f"{treasure_index[t]['emoji']} {t.title()}"
                for t, data in treasure_index.items()
                if data["tier"] <= max_tier
            ]

            if possible:
                treasure_text = "\n**Possible Treasures:**\n" + ", ".join(possible)

        lines.append(
            f"{emoji} __**{name.title()}**__\n"
            f"<:coin:1399146146315894825> Gold: {gold_min}–{gold_max} | "
            f"<:level:1399200622779302004> XP: {xp_min}–{xp_max}"
            f"{treasure_text}"
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
    embed = discord.Embed(title="📘 Ship Quest Guide",
                          color=discord.Color.green())

    fishing_cmds = [
        "sq cast – Cast your rod for a fish",
        "sq net - Throw out a fishing net for a big catch",
        "sq adv / sq adventure – Go on an adventure to find chests",
        "sq bait <bait/none> <amount> – Equip bait to increase odds of catching better fish",
        "sq dig – Dig for a chance to find bait in the ground",
        "sq fi / sq fish index – View list of fish and their stats",
        "sq ci / sq chest index – View list of chests and their possible contents",
        "sq open <chest/all> – Open a specific chest type or all chests from your inventory",
        "sq sell <item> – Sell fish, treasures, or bait for gold",
    ]
    embed.add_field(
        name=
        "━━━━ <:wooden_rod:1399044497068920912> Fishing & Loot Commands <:chest:1399491916978192406> ━━━━",
        value="\n".join(fishing_cmds),
        inline=False)

    inventory_cmds = [
        "sq p / sq profile – View profile",
        "sq i / sq inventory – View Inventory",
        "sq fish bowl <fish type> <nickname> - Put a rare fish in your fish bowl to boost rare fish odds (and you can name it!)",
        "sq shop – Where you can buy rods, boosts, and more",
        "sq buy <item> – Buy rods or boosts",
        "sq cd / sq cooldown – Check cooldowns & see active boosts"
    ]
    embed.add_field(name="━━━━ Inventory & Shops ━━━━",
                    value="\n".join(inventory_cmds),
                    inline=False)

    misc_cmds = ["sq guide – You're already here brev so idk what to tell u"]
    embed.add_field(name="━━━━ Miscellaneous ━━━━",
                    value="\n".join(misc_cmds),
                    inline=False)

    await ctx.send(embed=embed)


keep_alive()

bot.run(TOKEN)
