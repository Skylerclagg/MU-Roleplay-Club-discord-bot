import asyncio
import discord
from utils.guild_config import get_guild_config, redis_client, format_time

async def handle_verification_process(bot: discord.Client, member: discord.Member):
    """
    Begins the verification process for a member:
      - Sends reminders at intervals set in the configuration.
      - Uses a fixed start time so that the overall timeout is measured
        from the first invitation to verify rather than the last reminder.
      - Once the overall reminder timeout is reached:
           * If post_action is "send_dm" or "kick", the corresponding action is executed and the process ends.
           * If post_action is "continue_wait", the bot stops sending reminders and continues waiting.
      - Upon successful verification, a confirmation message is sent, which is customizable:
           * It can be enabled/disabled per server.
           * It can be sent via DM or in the welcome channel, per server configuration.
    """
    guild = member.guild
    guild_id = guild.id
    pending_key = f"pending_verification:{guild_id}:{member.id}"
    
    # Record initial verification start time.
    start_time = asyncio.get_event_loop().time()
    print(f"Verification process started for member: {member}, guild: {guild_id}")
    
    try:
        # Set pending verification key in Redis (expires in 1 day).
        await redis_client.set(pending_key, "pending", ex=86400)
        print(f"Pending verification key set in Redis for {member}.")
    except Exception as e:
        print(f"Failed to set pending verification in Redis for {member}: {e}")
    
    # Fetch guild configuration.
    config = await get_guild_config(guild)
    timeout_action = config.get("timeout_action", "remind")
    if timeout_action == "remind":
        bot_timeout = config.get("reminder_interval", 3600)
    else:
        bot_timeout = config.get("timeout_limit", 86400)
    
    overall_reminder_timeout = config.get("reminder_timeout", 86400)
    post_action = config.get("post_reminder_action", "continue_wait")
    post_message = config.get("post_reminder_message", None)
    
    # Flag used for "continue_wait" mode to suppress further reminder messages.
    suppress_reminders = False

    # Build a list of channels to listen in for a verification response.
    verification_channels = []
    if config.get("dm_enabled"):
        dm_channel = member.dm_channel
        if dm_channel is None:
            try:
                dm_channel = await member.create_dm()
                print(f"DM channel created for {member}.")
            except Exception as e:
                print(f"Could not create DM channel for {member}: {e}")
        if dm_channel:
            verification_channels.append(dm_channel)
    if config.get("welcome_channel"):
        try:
            welcome_channel = guild.get_channel(int(config["welcome_channel"]))
            if welcome_channel:
                verification_channels.append(welcome_channel)
        except Exception as e:
            print(f"Error retrieving welcome channel for guild {guild_id}: {e}")
    if not verification_channels and guild.system_channel:
        verification_channels.append(guild.system_channel)
    
    print(f"Verification channels for {member}: {verification_channels}")
    
    # Main loop: continue waiting until the member is verified or leaves.
    while True:
        if not guild.get_member(member.id):
            print(f"{member} has left the server. Stopping verification process.")
            break

        role_given_id = config.get("role_given")
        if role_given_id:
            verified_role = guild.get_role(int(role_given_id))
            if verified_role and verified_role in member.roles:
                print(f"{member} is already verified. Stopping verification process.")
                break

        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"Elapsed time for verification process: {elapsed} seconds")

        # Handle overall timeout.
        if elapsed >= overall_reminder_timeout and not suppress_reminders:
            print(f"Overall reminder timeout reached for {member}. Post-action: {post_action}")
            if post_action == "send_dm":
                try:
                    dm_channel = member.dm_channel or await member.create_dm()
                    msg = post_message if post_message else f"{member.mention}, your verification period has expired. Please reply via DM to verify."
                    await dm_channel.send(msg)
                    print(f"Sent post-timeout DM to {member}.")
                except Exception as e:
                    print(f"Failed to send post-timeout DM to {member}: {e}")
                break
            elif post_action == "kick":
                try:
                    warn_msg = post_message if post_message else f"{member.mention}, you have failed to verify in time and will be removed from the server."
                    try:
                        await member.send(warn_msg)
                    except Exception:
                        pass
                    print(f"Kicking {member} after overall timeout.")
                    await member.kick(reason="No verification response within overall reminder timeout")
                except Exception as e:
                    print(f"Failed to kick {member}: {e}")
                break
            elif post_action == "continue_wait":
                print(f"Overall timeout reached for {member}, but 'continue_wait' is set. Suppressing further reminders.")
                suppress_reminders = True
                # Continue waiting without sending reminders.
                bot_timeout = config.get("reminder_interval", 3600)
                # Do not break—the loop continues indefinitely.
        
        try:
            def check(msg):
                return msg.author == member and msg.channel in verification_channels
            print(f"Waiting for a message from {member} (timeout = {bot_timeout} seconds)...")
            msg = await bot.wait_for("message", timeout=bot_timeout, check=check)
            print(f"Message received from {member}: {msg.content}")
        except asyncio.TimeoutError:
            print(f"Timeout waiting for response from {member}. Timeout action: {timeout_action}")
            if not suppress_reminders:
                if timeout_action == "kick":
                    print(f"Kicking {member} due to per-reminder timeout.")
                    try:
                        await member.send("You did not submit your full name in time and have been removed from the server.")
                    except Exception:
                        pass
                    await member.kick(reason="No verification response within timeout limit")
                    break
                elif timeout_action == "remind":
                    reminder = config.get("reminder_message", f"{member.mention}, please submit your full name to verify and gain access to the server.")
                    reminder = reminder.replace("{user}", member.mention)
                    for channel in verification_channels:
                        try:
                            await channel.send(reminder)
                            print(f"Sent reminder to {member} in {channel}.")
                        except Exception as e:
                            print(f"Failed to send reminder to {member} in {channel}: {e}")
                    # Reset per-reminder timeout while overall time remains unchanged.
                    bot_timeout = config.get("reminder_interval", 3600)
                elif timeout_action == "restrict":
                    print(f"{member} did not verify in time and remains restricted. Ending process.")
                    break
            else:
                print(f"Reminders are suppressed for {member}. Continuing to wait without sending reminder.")
        else:
            full_name = msg.content.strip()
            if full_name:
                method = "via DM" if isinstance(msg.channel, discord.DMChannel) else f"in #{msg.channel.name}"
                try:
                    await member.edit(nick=full_name)
                    print(f"{member} verified as '{full_name}' {method}.")
                except Exception as e:
                    print(f"Failed to update nickname for {member}: {e}")
                if role_given_id:
                    role = guild.get_role(int(role_given_id))
                    if role and role not in member.roles:
                        try:
                            await member.add_roles(role)
                            print(f"Granted role {role.name} to {member}.")
                        except Exception as e:
                            print(f"Failed to assign verified role for {member}: {e}")
                try:
                    await redis_client.delete(pending_key)
                    print(f"Removed pending verification key for {member} from Redis.")
                except Exception as e:
                    print(f"Failed to delete verification key for {member} from Redis: {e}")
                
                # Send a customizable confirmation message with placeholder replacement.
                if config.get("verification_confirmation_enabled", True):
                    # Get the confirmation message template (default provided) and replace placeholders.
                    confirm_message = config.get(
                        "verification_confirmation_message",
                        "Thank you, {user}! You have been verified and granted access to {server}."
                    )
                    # Replace {user} with the member's mention and {server} with the guild name.
                    confirm_message = confirm_message.replace("{user}", member.mention).replace("{server}", guild.name)
                    
                    if config.get("verification_confirmation_dm", True):
                        try:
                            await member.send(confirm_message)
                            print(f"Sent confirmation DM to {member}.")
                        except Exception as e:
                            print(f"Failed to send confirmation DM to {member}: {e}")
                    else:
                        # Attempt to send the confirmation message in the welcome channel,
                        # falling back to DM if necessary.
                        confirm_channel = None
                        if config.get("welcome_channel"):
                            confirm_channel = guild.get_channel(int(config["welcome_channel"]))
                        if confirm_channel:
                            try:
                                await confirm_channel.send(confirm_message)
                                print(f"Sent confirmation message in {confirm_channel} to {member}.")
                            except Exception as e:
                                print(f"Failed to send confirmation message in {confirm_channel}: {e}")
                        else:
                            try:
                                await member.send(confirm_message)
                                print(f"Sent fallback confirmation DM to {member}.")
                            except Exception as e:
                                print(f"Failed to send fallback confirmation DM to {member}: {e}")
                else:
                    print("Confirmation message is disabled for this server.")
                break
