import discord
from typing import Optional

async def get_log_webhook(channel: discord.TextChannel) -> Optional[discord.Webhook]:
    """Gets or creates a webhook for a given log channel."""
    try:
        webhooks = await channel.webhooks()
        bot_webhook = discord.utils.get(webhooks, name="WelcomeBot Log")
        if bot_webhook:
            return bot_webhook
        return await channel.create_webhook(name="WelcomeBot Log")
    except Exception as e:
        print(f"Error obtaining webhook for channel {channel.name}: {e}")
        return None

async def send_log(bot: discord.Client, guild: discord.Guild, message: str):
    """Sends a log message to the configured log channel via webhook."""
    from .guild_config import get_guild_config
    
    # First, print to console as a fallback
    print(f"[{guild.name}] {message}")

    # Then, try to send to the log channel
    config = await get_guild_config(guild)
    channel_id = config.get("log_channel")
    
    if channel_id:
        channel = guild.get_channel(channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            webhook = await get_log_webhook(channel)
            if webhook:
                embed = discord.Embed(
                    description=message,
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow()
                )
                if bot.user:
                    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url if bot.user.avatar else None)
                embed.set_footer(text=f"Guild ID: {guild.id}")
                try:
                    await webhook.send(
                        embed=embed, 
                        username=bot.user.name if bot.user else "Bot Logger", 
                        avatar_url=bot.user.avatar.url if bot.user and bot.user.avatar else None
                    )
                except Exception as e:
                    print(f"Failed to send log via webhook: {e}")
