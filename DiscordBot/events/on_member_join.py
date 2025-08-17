import discord
from discord.ext import commands
import asyncio
from utils.guild_config import get_guild_config
from utils.verification import handle_verification_process

class OnMemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(f"New member joined: {member}. Preparing to start verification process.")
        
        # Fetch the guild configuration
        try:
            config = await get_guild_config(member.guild)
            print(f"Loaded config for {member.guild.name}: {config}")
        except Exception as e:
            print(f"Error fetching config for guild {member.guild.id}: {e}")
            return  # Stop here if we can't get the config
        
        # If DM verification is enabled, send a DM.
        if config.get("dm_enabled"):
            try:
                dm_channel = member.dm_channel or await member.create_dm()
                dm_welcome = config.get(
                    "dm_welcome_message",
                    "Hello {user}, welcome to {server}! Please reply with your full name to verify."
                )
                # Replace both {user} and {server} placeholders.
                content = dm_welcome.replace("{user}", member.mention).replace("{server}", member.guild.name)
                await dm_channel.send(content)
                print(f"Sent DM to {member}")
            except Exception as e:
                print(f"Failed to send DM to {member}: {e}")
        else:
            # Otherwise, send the welcome message in the designated channel.
            welcome_channel = None
            if config.get("welcome_channel"):
                welcome_channel = member.guild.get_channel(int(config["welcome_channel"]))
            if not welcome_channel:
                welcome_channel = member.guild.system_channel
            welcome_message = config.get(
                "welcome_message",
                f"Welcome {member.mention} to {member.guild.name}! Please reply with your full name to verify and gain access."
            )
            # Replace both placeholders.
            content = welcome_message.replace("{user}", member.mention).replace("{server}", member.guild.name)
            if welcome_channel:
                try:
                    await welcome_channel.send(content)
                    print(f"Sent welcome message in {welcome_channel}")
                except Exception as e:
                    print(f"Could not send welcome message in {welcome_channel}: {e}")
            else:
                try:
                    await member.send(content)
                    print(f"Sent fallback DM to {member}")
                except Exception as e:
                    print(f"Could not send fallback DM to {member}: {e}")

        print(f"Starting verification process for: {member}")
        try:
            # Pass the bot instance (self.bot) and member to the verification process.
            asyncio.create_task(handle_verification_process(self.bot, member))
        except Exception as e:
            print(f"Failed to start verification process for {member}: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberJoin(bot))
