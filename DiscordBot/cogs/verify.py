import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from utils.verification import handle_verification_process
from utils.guild_config import get_guild_config
from utils.permissions import mod_check  # Ensure this is defined in your utils

class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="verify",
        description="Manually trigger the verification process for a member."
    )
    @app_commands.check(mod_check)
    async def manualverify(self, interaction: discord.Interaction, member: discord.Member):
        # Inform the interaction caller that the process is starting
        await interaction.response.send_message(f"Starting manual verification for {member.mention}.", ephemeral=True)
        print(f"Manual verification command invoked for {member}.")
        
        # Optionally, check if the member is already verified.
        config = await get_guild_config(interaction.guild)
        role_given_id = config.get("role_given")
        if role_given_id:
            verified_role = interaction.guild.get_role(int(role_given_id))
            if verified_role and verified_role in member.roles:
                await interaction.followup.send(f"{member.mention} is already verified.", ephemeral=True)
                print(f"{member} is already verified.")
                return
        
        # Start the verification process using the existing handler.
        try:
            asyncio.create_task(handle_verification_process(self.bot, member))
            await interaction.followup.send(f"Verification process has been started for {member.mention}.", ephemeral=True)
            print(f"Verification process task created for {member}.")
        except Exception as e:
            await interaction.followup.send(f"Failed to initiate verification for {member.mention}: {e}", ephemeral=True)
            print(f"Error when manually verifying {member}: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))
