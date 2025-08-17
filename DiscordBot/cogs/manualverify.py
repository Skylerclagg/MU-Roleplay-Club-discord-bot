import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class ManualVerify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="manualverify", description="Manually verify a member (updates nickname and assigns verified role).")
    @app_commands.check(mod_check)
    async def manualverify(self, interaction: discord.Interaction, member: discord.Member, full_name: Optional[str] = None):
        config = await get_guild_config(interaction.guild)
        verified_role_id = config.get("role_given")
        if not verified_role_id:
            await interaction.response.send_message("Verified role is not configured. Use /setrolegiven to set it.", ephemeral=True)
            return
        verified_role = interaction.guild.get_role(verified_role_id)
        if not verified_role:
            await interaction.response.send_message("Verified role not found in this server.", ephemeral=True)
            return
        if full_name:
            try:
                await member.edit(nick=full_name)
            except Exception as e:
                await interaction.response.send_message(f"Failed to update nickname: {e}", ephemeral=True)
                return
        try:
            await member.add_roles(verified_role)
        except Exception as e:
            await interaction.response.send_message(f"Failed to assign role: {e}", ephemeral=True)
            return
        await interaction.response.send_message(f"{member.mention} has been manually verified.", ephemeral=True)
        # Optionally log this action (if your bot.send_log is available)
        try:
            await self.bot.send_log(interaction.guild, f"Manual verification: {interaction.user} manually verified {member} with full name: {full_name or member.display_name}")
        except Exception:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(ManualVerify(bot))
