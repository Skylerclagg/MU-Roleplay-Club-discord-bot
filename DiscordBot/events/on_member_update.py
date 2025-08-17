import discord
from discord.ext import commands
from utils.guild_config import get_guild_config

class OnMemberUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def log(self, guild: discord.Guild, message: str):
        """
        Logs a message using the bot's send_log method if available.
        Otherwise, prints the message to the console with the guild name.
        """
        if hasattr(self.bot, "send_log") and callable(self.bot.send_log):
            try:
                await self.bot.send_log(guild, message)
            except Exception as e:
                print(f"Logging error using send_log for guild {guild.name}: {e}")
                print(f"[{guild.name}] {message}")
        else:
            print(f"[{guild.name}] {message}")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # Check if the nickname changed.
        if before.nick != after.nick:
            config = await get_guild_config(after.guild)
            verified_role_id = config.get("role_given")
            if verified_role_id:
                verified_role = after.guild.get_role(int(verified_role_id))
                if verified_role and verified_role not in after.roles:
                    try:
                        await after.add_roles(verified_role)
                        await self.log(after.guild, f"Auto-assigned role {verified_role.name} to {after} due to nickname change.")
                    except Exception as e:
                        print(f"Failed to add verified role on nickname change for {after}: {e}")
            # Attempt to find the user who made the change via audit logs.
            changer = after
            try:
                async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id:
                        changer = entry.user
                        break
            except Exception as e:
                print(f"Failed to fetch audit logs for {after}: {e}")
            try:
                await self.log(after.guild, f"Nickname change for {after}: '{before.nick}' → '{after.nick}' by {changer}")
            except Exception as e:
                print(f"Logging error in on_member_update: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberUpdate(bot))
