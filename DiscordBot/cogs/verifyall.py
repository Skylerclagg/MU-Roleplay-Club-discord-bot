import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from utils.guild_config import get_guild_config
from utils.verification import handle_verification_process
from utils.permissions import mod_check

class VerifyAll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="verifyall", description="Start verification process for all members without the verified role.")
    @app_commands.describe(exclude_roles="Comma-separated list of roles to exclude from verification")
    @app_commands.check(mod_check)
    async def verifyall(self, interaction: discord.Interaction, exclude_roles: str = None):
        await interaction.response.defer(ephemeral=True)
        config = await get_guild_config(interaction.guild)
        verified_role_id = config.get("role_given")
        if not verified_role_id:
            await interaction.followup.send("Verified role is not configured. Use /setrolegiven to set it.", ephemeral=True)
            return
        excluded_role_ids = set()
        if exclude_roles:
            for part in exclude_roles.split(","):
                part = part.strip()
                if part:
                    try:
                        role_id = int(''.join(filter(str.isdigit, part)))
                        excluded_role_ids.add(role_id)
                    except Exception:
                        continue
        count = 0
        for member in interaction.guild.members:
            if member.bot:
                continue
            if verified_role_id in [r.id for r in member.roles]:
                continue
            if any(r.id in excluded_role_ids for r in member.roles):
                continue
            # FIX: Pass self.bot to the verification process handler
            asyncio.create_task(handle_verification_process(self.bot, member))
            count += 1
        await interaction.followup.send(f"Started verification process for {count} members.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(VerifyAll(bot))
