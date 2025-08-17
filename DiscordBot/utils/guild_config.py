import json
import redis.asyncio as redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
guild_configurations = {}

def parse_time_limit(limit: str):
    limit = limit.strip().lower()
    if limit.endswith('d'):
        try:
            return int(limit[:-1]) * 86400
        except ValueError:
            return None
    elif limit.endswith('h'):
        try:
            return int(limit[:-1]) * 3600
        except ValueError:
            return None
    elif limit.endswith('m'):
        try:
            return int(limit[:-1]) * 60
        except ValueError:
            return None
    elif limit.endswith('s'):
        try:
            return int(limit[:-1])
        except ValueError:
            return None
    else:
        try:
            return int(limit)
        except ValueError:
            return None

def format_time(seconds: int) -> str:
    if seconds % 86400 == 0:
        return f"{seconds // 86400}d"
    elif seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    elif seconds % 60 == 0:
        return f"{seconds // 60}m"
    else:
        return f"{seconds}s"

async def get_guild_config(guild):
    if guild.id in guild_configurations:
        return guild_configurations[guild.id]
    key = f"guild_config:{guild.id}"
    try:
        config_json = await redis_client.get(key)
    except Exception as e:
        print(f"Redis GET error: {e}")
        config_json = None
    if config_json:
        config = json.loads(config_json)
    else:
        config = {
        "welcome_message": "Welcome {user}! Please reply with your full name to verify.",
        "dm_enabled": False,
        "dm_welcome_message": "Hello {user}, welcome! Please reply with your full name to verify.",
        "welcome_channel": None,
        "role_given": None,
        "mod_roles": [],
        "command_permissions": {
            "giverole": {},
            "removerole": {},
            "addusertochannel": {},
            "removeuserfromchannel": {}
        },
        "timeout_action": "remind",      # Options: "kick", "restrict", "remind"
        "timeout_limit": 86400,          # Default overall timeout: 1 day
        "reminder_interval": 3600,       # Default reminder interval: 1 hour
        "reminder_timeout": 86400,       # Overall reminder timeout: 1 day by default
        "post_reminder_action": "continue_wait",  # Options: "send_dm", "continue_wait", "kick"
        "post_reminder_message": None,
        "reminder_message": "Reminder {user}, please submit your full name to verify and gain access to the server.",
        "verification_confirmation_enabled": True,
        "verification_confirmation_message": "Thank you! You have been verified and granted access to the server.",
        "verification_confirmation_dm": True
    }
    guild_configurations[guild.id] = config
    return config

async def save_guild_config(guild, config):
    guild_configurations[guild.id] = config
    key = f"guild_config:{guild.id}"
    try:
        await redis_client.set(key, json.dumps(config))
    except Exception as e:
        print(f"Redis SET error: {e}")
