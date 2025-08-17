import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class ConfigWelcomeChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="configwelcomechannel", description="Configure welcome channel permissions and exclusions.")
    @app_commands.check(mod_check)
    async def configwelcomechannel(
            self,
            interaction: discord.Interaction,
            negativerole: discord.Role,
            positiverole: discord.Role,
            welcomechannel: discord.TextChannel,
            excluderoles: str = "",
            excludecategories: str = ""
        ):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        def parse_ids(input_str: str):
            ids = set()
            if input_str:
                for part in input_str.split(","):
                    part = part.strip()
                    if part:
                        try:
                            id_int = int(''.join(filter(str.isdigit, part)))
                            ids.add(id_int)
                        except Exception:
                            pass
            return ids
        excluded_role_ids = parse_ids(excluderoles)
        excluded_category_ids = parse_ids(excludecategories)
        
        # Update configuration with the chosen welcome channel.
        config = await get_guild_config(guild)
        config["welcome_channel"] = welcomechannel.id
        await save_guild_config(guild, config)
        
        updated_channels = 0
        for channel in guild.channels:
            try:
                if channel.id == welcomechannel.id:
                    await channel.set_permissions(negativerole, overwrite=discord.PermissionOverwrite(view_channel=True))
                else:
                    await channel.set_permissions(negativerole, overwrite=discord.PermissionOverwrite(view_channel=False))
            except Exception as e:
                print(f"Failed to update negative permissions on {channel.name}: {e}")
            try:
                if channel.id == welcomechannel.id:
                    await channel.set_permissions(positiverole, overwrite=discord.PermissionOverwrite(view_channel=True))
                else:
                    # Check for channel exclusions by role or category.
                    is_excluded = (channel.id in excluded_role_ids or
                                   (hasattr(channel, "category") and channel.category and channel.category.id in excluded_category_ids))
                    if not is_excluded:
                        await channel.set_permissions(positiverole, overwrite=discord.PermissionOverwrite(view_channel=True))
                updated_channels += 1
            except Exception as e:
                print(f"Failed to update positive permissions on {channel.name}: {e}")
        await interaction.followup.send(f"Updated permissions on {updated_channels} channels.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigWelcomeChannel(bot))
