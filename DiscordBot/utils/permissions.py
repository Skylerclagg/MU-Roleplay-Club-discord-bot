import discord
from utils.guild_config import get_guild_config

DEVELOPER_IDS = [348286042136117251, 123456789012345678]  # Your developer override IDs

async def mod_check(interaction: discord.Interaction) -> bool:
    # Developer override: any user in DEVELOPER_IDS can execute the command.
    if interaction.user.id in DEVELOPER_IDS:
        return True

    # The check fails if the command wasn't run in a guild.
    if interaction.guild is None:
        return False

    # Get the server configuration.
    config = await get_guild_config(interaction.guild)

    # Allow if the user is an administrator.
    if interaction.user.guild_permissions.administrator:
        return True

    # Allow if any of the user's roles are in the mod roles list from configuration.
    for role in interaction.user.roles:
        if role.id in config.get("mod_roles", []):
            return True

    # Otherwise, the user does not meet the criteria.
    return False
