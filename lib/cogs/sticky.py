import asyncio
import base64
import os
import re
from contextlib import suppress
from datetime import datetime, timedelta, timezone

import discord

from discord.ext import commands, tasks
from ..db import db


timeout = 30
reactions = ["🔁", "✅", "🛑"]
channel_tag_rx = re.compile(r'<#[0-9]{18}>')
channel_id_rx = re.compile(r'[0-9]{18}')



class Sticky(commands.Cog):

    def __init__(self, bot):
   
        self.bot = bot


    def custom_check():
        def predicate(ctx):
            
            command  =  db.field("SELECT commandname FROM command WHERE channelid = ?", ctx.channel.id)
            if command is not None:
                command.split(',')
                if  len(command)> 1 and ctx.command.name in command :
                    return 
                elif ctx.command.name in command :
                    return
            return True
        return commands.check(predicate)
     
    #     self.tasks = []
    #     self.bot.loop.create_task(self.init_reminders())


    # async def smart_delete(self, message: discord.Message):
    #     if message.guild and message.guild.me.guild_permissions.manage_messages:
    #         try:
    #             await message.delete()
    #         except Exception:
    #             pass

    # async def smart_clear(self, message: discord.Message):
    #     if message.guild and message.guild.me.guild_permissions.manage_messages:
    #         try:
    #             await message.clear_reactions()
    #         except Exception:
    #             pass

    # def cog_unload(self):
    #     for task in self.tasks:
    #         task.cancel()
    #     self.check_single.cancel()
    #     self.check_loop.cancel()

    # async def init_reminders(self):
    #     await self.bot.wait_until_ready()
       
           
    #     self.tasks.append(self.check_single.start())
    #     self.tasks.append(self.check_loop.start())

    # @tasks.loop(seconds=15)
    # async def check_single(self):
    #     await self.bot.wait_until_ready()

    #     result = db.records("SELECT * FROM reminders WHERE type_ = 'single'")
    #     if not result:
    #         return

    #     for reminder in result:
    #         if float(reminder[6]) - datetime.now().timestamp() <= 15.0:
    #             message_content_ascii = base64.urlsafe_b64decode(str.encode(reminder[5]))
    #             message_content = message_content_ascii.decode("ascii")
    #             user_id = int(reminder[2])
    #             sleep_time = float(reminder[6]) - datetime.now().timestamp()
    #             if sleep_time <= 0:
    #                 sleep_time = 0
    #             self.tasks.append(
    #                 self.bot.loop.create_task(
    #                     self.send_single(sleep_time, user_id, int(reminder[3]), message_content,
    #                                      int(reminder[1]), int(reminder[0]))
    #                 )
    #             )

    # async def send_single(self, sleep_time: float, user_id: int, channel_id: int, message_content: str, guild_id: int, index: int):
    #     if sleep_time > 0:
    #         await asyncio.sleep(sleep_time)
    #     try:
    #         channel = await self.bot.fetch_channel(channel_id)
    #         user = await channel.guild.fetch_member(user_id)
    #         embed = discord.Embed(description=message_content,
    #                               color=discord.Color.blue())
    #         embed.set_author(name=f"Reminder for {user.display_name}", icon_url=user.avatar_url)
    #         await channel.send(f"{user.mention}")
    #         await channel.send(embed=embed)
    #     except (discord.Forbidden, discord.HTTPException, discord.InvalidData, discord.NotFound, KeyError):
    #         pass

       
    #     db.execute(f"DELETE FROM reminders WHERE id = {index}")

    # @tasks.loop(seconds=1, count=1)
    # async def check_loop(self):
    #     await self.bot.wait_until_ready()
        
    #     result = db.records("SELECT * FROM reminders WHERE type_ = 'loop'")
    #     if not result:
    #         return

    #     for reminder in result:
    #         message_content_ascii = base64.urlsafe_b64decode(str.encode(reminder[5]))
    #         message_content = message_content_ascii.decode("ascii")
    #         self.tasks.append(
    #             self.bot.loop.create_task(
    #                 self.send_loop(reminder[6], int(reminder[2]), reminder[3],
    #                                message_content, int(reminder[1]), int(reminder[0]))
    #             )
    #         )

    # async def send_loop(self, loop_interval: int, user_id: int, channel_id: int, message_content: str, guild_id: int, index: int):
    #     while True:
    #         await asyncio.sleep(1.0)
    #         if int(datetime.now().timestamp()) % int(loop_interval) == 0:
    #             try:
    #                 channel = await self.bot.fetch_channel(channel_id)
    #                 user = await channel.guild.fetch_member(user_id)
    #                 embed = discord.Embed(description=message_content,
    #                                       color=discord.Color.blue())
    #                 embed.set_author(name=f"Reminder for {user.display_name}", icon_url=user.avatar_url)
    #                 await channel.send(f"{user.mention}")
    #                 await channel.send(embed=embed)
    #             except (discord.Forbidden, discord.HTTPException, discord.InvalidData, discord.NotFound):
    #                 break
    #         else:
    #             continue

    # async def send_remind_help(self, ctx) -> discord.Message:
    #     embed = discord.Embed(title="Reminders Help",
    #                           description=f"To use reminder commands, just do `{ctx.prefix}remind ["
    #                                       f"option]`. Here is a list of valid options",
    #                           color=discord.Color.blue())
    #     embed.add_field(name="Create",
    #                     value=f"Usage: `{ctx.prefix}remind [message_with_time]`\n"
    #                           f"Returns: Your reminder message at the specified time\n"
    #                           f"Aliases: `reminder`\n"
    #                           f"Note: You must specify a time within your message, whether it be exact or "
    #                           f"relative",
    #                     inline=False)
    #     embed.add_field(name="Edit",
    #                     value=f"Usage: `{ctx.prefix}remind edit`\n"
    #                           f"Returns: An interactive reminder edit panel\n"
    #                           f"Aliases: `-e`\n"
    #                           f"Note: You must have at least one reminder queued\n\n*An error may occur if the "
    #                           f"reminder fires while you are in the middle of editing it. It may also end up firing "
    #                           f"twice if you edit it within 15 seconds of it's firing time*",
    #                     inline=False)
    #     embed.add_field(name="Delete",
    #                     value=f"Usage: `{ctx.prefix}remind delete`\n"
    #                     f"Returns: An interactive reminder delete panel\n"
    #                     f"Aliases: `rm` `trash`\n"
    #                     f"Note: You must have at least one reminder queued in that server\n\n*An error may "
    #                     f"occur if the reminder fires while you are in the middle of deleting it. If you proceed, it "
    #                     f"may display that the deletion was unsuccessful. It's entry has already been deleted from "
    #                     f"the database after it was fired*")
    #     return await ctx.channel.send(embed=embed)

    # async def timeout(self, ctx) -> discord.Message:
    #     embed = discord.Embed(title="Reminder Setup Timed Out",
    #                           description=f"{ctx.author.mention}, your reminder setup timed out due to inactivity",
    #                           color=discord.Color.dark_red())
    #     return await ctx.channel.send(embed=embed)

    # async def check_panel_exists(self, panel: discord.Message) -> bool:
    #     try:
    #         if panel.id:
    #             return True
    #     except discord.NotFound:
    #         return False

    # async def edit_panel(self, panel_embed: discord.Embed, panel: discord.Message,
    #                      title: str = None, description: str = None, color: discord.Color = None) -> bool:
    #     panel_exists = await self.check_panel_exists(panel)
    #     if not panel_exists:
    #         return False

    #     if not title:
    #         title = panel_embed.title
    #     if not description:
    #         description = panel_embed.description
    #     if not color:
    #         color = discord.Color.blue()

    #     panel_embed_edited = discord.Embed(title=title,
    #                                        description=description,
    #                                        color=color)

    #     await panel.edit(embed=panel_embed_edited)
    #     return True

    # async def no_panel(self, ctx) -> discord.Message:
    #     embed = discord.Embed(title="Reminder Setup Cancelled",
    #                           description=f"{ctx.author.mention}, the reminder setup panel was either deleted or could "
    #                                       f"not be found",
    #                           color=discord.Color.dark_red())
    #     return await ctx.channel.send(embed=embed)

    # async def cancelled(self, ctx, panel: discord.Message) -> discord.Message:
    #     embed = discord.Embed(title="Reminder Setup Cancelled",
    #                           description=f"{ctx.author.mention}, the reminder setup was cancelled",
    #                           color=discord.Color.blue())
    #     if await self.check_panel_exists(panel):
    #         return await panel.edit(embed=embed)
    #     else:
    #         return await ctx.channel.send(embed=embed)

    # async def not_valid_time(self, ctx) -> discord.Message:
    #     embed = discord.Embed(title="Invalid Time",
    #                           description=f"{ctx.author.mention}, you did not provide a valid time",
    #                           color=discord.Color.dark_red())
    #     return await ctx.channel.send(embed=embed)

    # async def create_reminder(self, user_id: int, channel_id: int, guild_id: int,
    #                           send_time: int, message_content: str, remind_type: str):
    #     encoded = str(base64.urlsafe_b64encode(message_content.encode("ascii")), encoding="utf-8")
       
       
    #     result = db.execute(f"INSERT INTO reminders(guild_id, users, channel_id, type_, message_content, time_) VALUES (?,?,?,?,?,?)", guild_id, user_id, channel_id, remind_type, encoded, send_time)
    #     id_ = db.field('SELECT last_insert_rowid() FROM reminders')
    #     print(id_)
    #     if remind_type == "single":
    #         self.tasks.append(
    #             self.bot.loop.create_task(self.send_single(send_time, user_id, channel_id,
    #                                                        message_content, guild_id, id_))
    #         )
    #     else:
    #         self.tasks.append(
    #             self.bot.loop.create_task(self.send_loop(send_time, user_id, channel_id,
    #                                                      message_content, guild_id, id_))
    #         )

    # async def get_reminders(self, guild_id: int, user_id: int) -> str:
        
    #     result = db.records(f"SELECT * FROM reminders WHERE guild_id = {guild_id} AND users = {user_id}")
    #     if not result:
    #         return

    #     string = ""
    #     for entry in result:
    #         message_content_ascii = base64.urlsafe_b64decode(str.encode(entry[5]))
    #         message_content = message_content_ascii.decode("ascii")
    #         if entry[4] == "single":
    #             string += f"**ID: [{entry[0]}]** {entry[4]}, fires in <#{entry[3]}> at " \
    #                 f"{datetime.fromtimestamp(entry[6])}, {message_content}\n\n"
    #         else:
    #             td = entry[6]
    #             time_formatted = ""
    #             skip = False
    #             while True:
    #                 days = divmod(td, 86400)
    #                 if days[0] != 0:
    #                     time_formatted += f"{days[0]} days, "
    #                 rem_sec = days[1]
    #                 if rem_sec == 0:
    #                     break
    #                 hours = divmod(rem_sec, 3600)
    #                 if hours[0] != 0:
    #                     time_formatted += f"{hours[0]} hours, "
    #                 rem_sec = hours[1]
    #                 if rem_sec == 0:
    #                     break
    #                 minutes = divmod(rem_sec, 60)
    #                 if minutes[0] != 0:
    #                     time_formatted += f"{minutes[0]} minutes, "
    #                 seconds = rem_sec
    #                 if seconds != 0:
    #                     time_formatted += f"{seconds} seconds"
    #                 break
    #             string += f"**ID: [{entry[0]}]** {entry[4]}, fires in <#{entry[3]}> every {time_formatted} " \
    #                 f"{message_content}\n\n"
    #     return string

    # async def get_reminder_time(self, guild_id: int, user_id: int, index: int) -> str:
      
    #     result = (db.records(f"SELECT * FROM reminders WHERE id={index}"))[0]

    #     if result[4] == "single":
    #         return datetime.fromtimestamp(float(result[6])).strftime("%m/%d/%Y %H:%M:%S UTC")
    #     else:
    #         td = timedelta(seconds=int(result[6]))
    #         time_formatted = ""
    #         while True:
    #             days = divmod(td.seconds, 86400)
    #             if days[0] != 0:
    #                 time_formatted += f"{days[0]} days, "
    #             rem_sec = days[1]
    #             if rem_sec == 0:
    #                 break
    #             hours = divmod(rem_sec, 3600)
    #             if hours[0] != 0:
    #                 time_formatted += f"{hours[0]} hours, "
    #             rem_sec = hours[1]
    #             if rem_sec == 0:
    #                 break
    #             minutes = divmod(rem_sec, 60)
    #             if minutes[0] != 0:
    #                 time_formatted += f"{minutes[0]} minutes, "
    #             seconds = rem_sec
    #             if seconds != 0:
    #                 time_formatted += f"{seconds} seconds"
    #         return time_formatted

    # async def no_reminders(self, ctx) -> discord.Message:
    #     embed = discord.Embed(title="No Reminders",
    #                           description=f"{ctx.author.mention}, you currently have no reminders scheduled",
    #                           color=discord.Color.blue())
    #     return await ctx.channel.send(embed=embed)

    # async def get_reminder_type(self, index: int) -> str:
      
    #     type = db.field(f"SELECT type_ FROM reminders WHERE id={index}")

    #     return type

    # async def get_reminder_content(self, index: int) -> str:
        
    #     encoded = db.field(f"SELECT message_content FROM reminders WHERE id={index}")

    #     content_ascii = base64.urlsafe_b64decode(str.encode(encoded))
    #     content = content_ascii.decode("ascii")
    #     return content

    # async def get_reminder_channel(self, index: int) -> int:
    
    #     channel_id = db.field(f"SELECT channel_id FROM reminders WHERE id={index}")

    #     return int(channel_id)

    # async def edit_reminder(self, guild_id: int, user_id: int, index: int,
    #                         channel_id, time_to_send, edited_content) -> bool:
    #     encoded = str(base64.urlsafe_b64encode(edited_content.encode("ascii")), encoding="utf-8")
    #     sets = []
    #     if channel_id:
    #         sets.append(f"channel_id = {channel_id}")
    #     if time_to_send:
    #         sets.append(f"time = {time_to_send}")
    #     if edited_content:
    #         sets.append(
    #             f"message_content = $tag${str(base64.urlsafe_b64encode(edited_content.encode('ascii')), encoding='utf-8')}$tag$")
    #     try:
    #         db.execute(f"UPDATE reminders SET {', '.join(sets)} WHERE id={index} AND guild_id = {guild_id}")
    #         return True
    #     except Exception:
    #         return False

    # async def delete_reminder(self, ctx, index) -> bool:
    #     try:
        
    #         if isinstance(index, str):
    #             exists = db.records(f"SELECT * FROM reminders WHERE guild_id = {ctx.guild.id} AND users = {ctx.author.id}")
    #             if not exists:
    #                 return False
    #             db.execute(f"DELETE FROM reminders WHERE guild_id = {ctx.guild.id} AND users = {ctx.author.id}")
    #         else:
    #             exists = db.field(f"SELECT * FROM reminders WHERE id=? AND users = ?", index, ctx.author.id)
    #             if not exists:
    #                 return False
    #             db.execute(f"DELETE FROM reminders WHERE id=? AND users = ?", index, ctx.author.id)
    #         return True
    #     except Exception:
    #         return False

    # @commands.group(invoke_without_command=True,
    #                 aliases=['reminder', 'reminders'],
    #                 desc="Sets a reminder",
    #                 usage="remind (message)",
    #                 note="A time should be specified as a part of `(message)`. If that is not the case, the help "
    #                 "command for remind will be displayed")
    # async def remind(self, ctx, *, message_with_time: str = None):

    #     if not message_with_time:
    #         return await self.send_remind_help(ctx)

    #     dates = search_dates(text=message_with_time, settings={
    #                          'PREFER_DATES_FROM': "future"})
    #     current_time = datetime.now().timestamp()
    #     if not dates:
    #         return await self.not_valid_time(ctx)
    #     time_to_send = dates[0][1].timestamp()
    #     remind_message_rem_time = message_with_time.replace(
    #         f"{dates[0][0]}", "")
    #     if remind_message_rem_time.startswith(" "):
    #         remind_message = remind_message_rem_time[1:]
    #     else:
    #         remind_message = remind_message_rem_time

    #     panel_embed = discord.Embed(title="Reminder Setup Panel",
    #                                 description=f"{ctx.author.mention}, would you like this reminder to loop?\n\n"
    #                                             f"*React with* 🔁 *to loop,* ✅ *to have it send once, or* 🛑 "
    #                                             f"*to cancel",
    #                                 color=discord.Color.blue())
    #     panel = await ctx.channel.send(embed=panel_embed)
    #     for reaction in reactions:
    #         await panel.add_reaction(reaction)

    #     def reacted_user(reaction: discord.Reaction, user: discord.User) -> bool:
    #         if reaction.message.id == panel.id and user.id == ctx.author.id and (reaction.emoji in reactions):
    #             return True
    #         else:
    #             return False

    #     try:
    #         result = await self.bot.wait_for("reaction_add", check=reacted_user,
    #                                          timeout=timeout)
    #     except asyncio.TimeoutError:
    #         return await self.timeout(ctx)
    #     reaction = result[0].emoji
    #     with suppress(discord.Forbidden):
    #         await self.smart_clear(panel)
    #     if reaction == "🛑":
    #         return await self.cancelled(ctx, panel)
    #     elif reaction == "🔁":
    #         str_time = "every " + str(dates[0][0]).replace("in ", "").replace("at ", "")
    #         panel_new_title = "Reminder Successfully Created"
    #         panel_new_description = f"{ctx.author.mention}, your reminder has been created and will be dispatched to " \
    #                                 f"this channel {str_time}"
    #         finished = await self.edit_panel(panel_embed, panel, panel_new_title, panel_new_description)
    #         if not finished:
    #             return await self.cancelled(ctx, panel)
    #         loop_interval = time_to_send - current_time
    #         await self.create_reminder(ctx.author.id, ctx.channel.id, ctx.guild.id, loop_interval,
    #                                    remind_message, "loop")
    #     else:
    #         if str(dates[0][0]).startswith("in ") or str(dates[0][0]).startswith("at "):
    #             str_time = str(dates[0][0])
    #         else:
    #             str_time = "in " + str(dates[0][0])
    #         panel_new_title = "Reminder Successfully Created"
    #         panel_new_description = f"{ctx.author.mention}, your reminder has been created and will be dispatched to " \
    #                                 f"this channel {str_time}"
    #         finished = await self.edit_panel(panel_embed, panel, panel_new_title, panel_new_description)
    #         if not finished:
    #             return await self.cancelled(ctx, panel)
    #         await self.create_reminder(ctx.author.id, ctx.channel.id, ctx.guild.id, time_to_send,
    #                                    remind_message, "single")

    # @remind.command(aliases=['-e'])
    # async def edit(self, ctx):
    #     reminders_list = await self.get_reminders(ctx.guild.id, ctx.author.id)
    #     if not reminders_list:
    #         return await self.no_reminders(ctx)
    #     panel_embed = discord.Embed(title="Edit Reminders",
    #                                 description=f"{ctx.author.mention}, please type the ID number of the reminder that "
    #                                 f"you would like to edit, or type *\"cancel\"* to cancel\n\n{reminders_list}",
    #                                 color=discord.Color.blue())
    #     panel = await ctx.channel.send(embed=panel_embed)

    #     def from_user(message: discord.Message) -> bool:
    #         if message.author.id == ctx.author.id:
    #             return True
    #         else:
    #             return False

    #     # User inputs index of reminder they want to edit
    #     while True:
    #         try:
    #             if not await self.check_panel_exists(panel):
    #                 return await self.cancelled(ctx, panel)
    #             result = await self.bot.wait_for("message", check=from_user, timeout=timeout)
    #         except asyncio.TimeoutError:
    #             return await self.timeout(ctx)
    #         if result.content == "cancel":
    #             return await self.cancelled(ctx, panel)
    #         try:
    #             index = int(result.content)
    #             break
    #         except (ValueError, TypeError):
    #             continue
    #     await self.smart_delete(result)

    #     reminder_type = await self.get_reminder_type(index)
    #     if reminder_type == "single":
    #         description = f"{ctx.author.mention}, please enter the time you would like this reminder to fire, type " \
    #             f"*\"skip\"* to keep the current time or type *\"cancel\"* to cancel\n\n" \
    #             f"Current Time: {await self.get_reminder_time(ctx.guild.id, ctx.author.id, index)}"
    #     elif reminder_type == "loop":
    #         description = f"{ctx.author.mention}, please enter the interval you would like this reminder to loop or" \
    #             f"type *\"cancel\"* to cancel\n\n" \
    #             f"Loops Every: {await self.get_reminder_time(ctx.guild.id, ctx.author.id, index)}"

    #     await self.edit_panel(panel_embed, panel, title=None, description=description)

    #     # User inputs time they want the reminder to fire at
    #     while True:
    #         try:
    #             if not await self.check_panel_exists(panel):
    #                 return await self.cancelled(ctx, panel)
    #             result = await self.bot.wait_for("message", check=from_user, timeout=timeout)
    #         except asyncio.TimeoutError:
    #             return await self.timeout(ctx)
    #         if result.content == "cancel":
    #             return await self.cancelled(ctx, panel)
    #         if result.content == "skip":
    #             time_to_send = None
    #             break

    #         current_time = datetime.now().timestamp()
    #         dates = search_dates(text=result.content, settings={
    #                              'PREFER_DATES_FROM': "future"})
    #         if not dates:
    #             continue
    #         if reminder_type == "single":
    #             time_to_send = dates[0][1].timestamp()
    #         elif reminder_type == "loop":
    #             time_to_send = int(dates[0][1].timestamp() - current_time)
    #         break
    #     await self.smart_delete(result)

    #     description = f"{ctx.author.mention}, please type what you would like the reminder content to be if you would "\
    #         "like to change it, otherwise, type *\"skip\"* to keep the current content or type *\"cancel\"* to cancel" \
    #         f"\n\nCurrent Content: {await self.get_reminder_content(index)}"
    #     await self.edit_panel(panel_embed, panel, title=None, description=description)

    #     # User inputs reminder content they want to be displayed
    #     while True:
    #         try:
    #             if not await self.check_panel_exists(panel):
    #                 return await self.cancelled(ctx, panel)
    #             result = await self.bot.wait_for("message", check=from_user, timeout=timeout)
    #         except asyncio.TimeoutError:
    #             return await self.timeout(ctx)
    #         if result.content == "cancel":
    #             return await self.cancelled(ctx, panel)
    #         elif result.content == "skip":
    #             edited_content = None
    #         else:
    #             edited_content = result.content
    #         break
    #     await self.smart_delete(result)

    #     description = f"{ctx.author.mention}, please tag or enter the ID of the channel you would like this reminder " \
    #         f"to fire in\n\nCurrent channel: <#{await self.get_reminder_channel(index)}>"
    #     await self.edit_panel(panel_embed, panel, title=None, description=description)

    #     # User inputs reminder channel they want the reminder to fire in
    #     while True:
    #         try:
    #             if not await self.check_panel_exists(panel):
    #                 return await self.cancelled(ctx, panel)
    #             result = await self.bot.wait_for("message", check=from_user, timeout=30)
    #         except asyncio.TimeoutError:
    #             return await self.timeout(ctx)
    #         if result.content == "cancel":
    #             return await self.cancelled(ctx, panel)
    #         if result.content == "skip":
    #             channel_id = None
    #             break
    #         if re.match(channel_tag_rx, result.content):
    #             channel_id = int(result.content[2:20])
    #             break
    #         elif re.match(channel_id_rx, result.content):
    #             channel_id = int(result.content)
    #             break
    #         else:
    #             continue
    #     await self.smart_delete(result)
    #     if channel_id:
    #         channel = ctx.guild.get_channel(int(channel_id))
    #         perms = ctx.guild.me.permissions_in(channel)
    #         if not perms.send_messages:
    #             await self.smart_delete(panel)
    #             # raise customerrors.CannotMessageChannel(channel)

    #     succeeded = await self.edit_reminder(ctx.guild.id, ctx.author.id, index, channel_id, time_to_send, edited_content)
    #     if succeeded:
    #         await self.edit_panel(panel_embed, panel, title="Reminder Successfully Edited",
    #                               description=f"{ctx.author.mention}, your reminder was successfully edited")
    #     else:
    #         await self.edit_panel(panel_embed, panel, title="Reminder Edit Failed",
    #                               description=f"{ctx.author.mention}, your reminder could not be edited")
    #     return

    # @remind.command(aliases=['rm', 'trash'])
    # async def delete(self, ctx):
    #     reminders_list = await self.get_reminders(ctx.guild.id, ctx.author.id)
    #     if not reminders_list:
    #         return await self.no_reminders(ctx)
    #     panel_embed = discord.Embed(title="Delete Reminder",
    #                                 description=f"{ctx.author.mention}, please type the number of the reminder that "
    #                                 f"you would like to delete, *\"all\"* to delete all reminders, or type *\"cancel\"*"
    #                                 f" to cancel\n\n{reminders_list}",
    #                                 color=discord.Color.blue())
    #     panel = await ctx.channel.send(embed=panel_embed)

    #     reactions = ["✅", "🛑"]

    #     def from_user(message: discord.Message) -> bool:
    #         if message.author.id == ctx.author.id:
    #             return True
    #         else:
    #             return False

    #     def reacted(reaction: discord.Reaction, user: discord.User) -> bool:
    #         return reaction.emoji in reactions and reaction.message.id == panel.id and user.id == ctx.author.id

    #     while True:
    #         try:
    #             if not await self.check_panel_exists(panel):
    #                 return await self.cancelled(ctx, panel)
    #             result = await self.bot.wait_for("message", check=from_user, timeout=30)
    #         except asyncio.TimeoutError:
    #             return await self.timeout(ctx)
    #         if result.content == "cancel":
    #             return await self.cancelled(ctx, panel)
    #         elif result.content == "all":
    #             index = "all"
    #             break
    #         try:
    #             index = int(result.content)
    #             break
    #         except ValueError:
    #             continue
    #     await self.smart_delete(result)

    #     panel_embed.description = (f"{ctx.author.mention}, deleting is a destructive, irreversable action. React with "
    #                                f"{reactions[0]} to confirm or {reactions[1]} to cancel")

    #     try:
    #         await panel.edit(embed=panel_embed)
    #         try:
    #             for reaction in reactions:
    #                 await panel.add_reaction(reaction)
    #         except Exception:
    #             pass
    #     except Exception:
    #         return await self.cancelled(ctx, panel)

    #     try:
    #         result = await self.bot.wait_for("reaction_add", check=reacted, timeout=30)
    #     except asyncio.TimeoutError:
    #         return await self.timeout(ctx)
    #     if result[0].emoji == reactions[0]:
    #         pass
    #     else:
    #         return await self.cancelled(ctx, panel)

    #     try:
    #         await self.smart_clear(panel)
    #     except Exception:
    #         pass

    #     succeeded = await self.delete_reminder(ctx, index)
    #     if not succeeded:
    #         await self.edit_panel(panel_embed, panel, title="Reminder Delete Failed",
    #                               description=f"{ctx.author.mention}, your reminder could not be deleted. Check to see "
    #                               "if you input a valid ID.",
    #                               color=discord.Color.dark_red())
    #     else:
    #         await self.edit_panel(panel_embed, panel, title="Reminder Successfully Deleted",
    #                               description=f"{ctx.author.mention}, your reminder was successfully deleted")
    #     return




    
    @commands.group(name = 'stickyname', aliases = ['sticky-name', 'sname', 'sn'], description  = 'sticky nickname once used on a user,he/she cannot change their name')
    @custom_check()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_nicknames=True)
    async def sticky_name(self, ctx):
        # await ctx.send(f"Do `{ctx.prefix}help monitor` to get help")
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))


    @sticky_name.error
    async def stickyname_error(self, ctx, exc):
        if isinstance(exc, commands.BotMissingPermissions):
            await ctx.send("bot require manage nicknames perm to run this command.")
        elif isinstance(exc,commands.MissingPermissions ):
            await ctx.send("user should have administrator to run this command.")
     
    
    @sticky_name.command(name="delete", description  = 'Remove sticky name',aliases = ['del'], usage = '+sname delete <user>')
    @custom_check()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_nicknames=True)
    async def _dl(self, ctx, user:discord.Member =None):
        
        if user is None:
            return await ctx.send("Please speficy an user.")
        
        data = db.record("SELECT * FROM monitor WHERE target = ? and  mentor = ? and guild  = ?", user.id, ctx.author.id, ctx.guild.id)
        
        if data is None:
            return await ctx.send("You have not added this user in your sticky name list. Or you have mentioned invalid user.")
        try:

            db.execute("DELETE FROM monitor WHERE target =? and mentor =? and guild = ?", data[2], data[1], data[3])
            await user.edit(nick = data[5])
            await ctx.send("sticky name removed.")
        except:
            await ctx.send('try again some error occured')


    @sticky_name.command(name="clear", description  = 'clear your whole sticky name list', usage = '+sname clear')
    @custom_check()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_nicknames=True)
    async def _cl(self, ctx):
      
        
        datas = db.records("SELECT * FROM monitor WHERE mentor = ? and guild = ?", ctx.author.id, ctx.author.guild.id)
        
        if datas is None:
            return await ctx.send("your dont have any sticky names")
        try:
            for data in datas:
            
                db.execute("DELETE FROM monitor WHERE target =? and mentor =? and guild= ?", data[2], data[1], data[3])
                user = ctx.guild.get_member(data[2])
                await user.edit(nick = data[5])
            await ctx.send("list cleared")
        except:
            await ctx.send('try again some error occured')
	
    @sticky_name.command(name  = 'add', description = "stick a nickname on someone", usage = '+sname add <user> <nick>')
    @custom_check()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_nicknames=True)
    async def add(self, ctx, bot:discord.Member, *, nicks:str):
        


        if len(nicks) >32:
            return await ctx.send("nick must be of 32 character or less")
      
        user = bot

        if (ctx.guild.me.top_role.position < user.top_role.position or ctx.author.top_role.position< user.top_role.position or user.guild_permissions.administrator):
            return await ctx.send('you cant apply sticky name to the user either the user is admin or has the higher role than you or bot')
        
    
        
        data = db.records("SELECT * FROM monitor WHERE mentor = ? and guild =?", ctx.author.id, ctx.guild.id)
                
        if len(data) >= 5:
            return await ctx.send("Maximum sticky names reached. Delete any previous user to create new one.")

        data = db.record("SELECT * FROM monitor WHERE target = ? and mentor = ? and guild = ?", user.id, ctx.author.id, ctx.guild.id)
        if data:
          
            return await ctx.send("You already sticked a nickname to this person")

        data = db.record("SELECT * FROM monitor WHERE target = ? and guild = ?", user.id,ctx.guild.id)
        if data:
            return await ctx.send('sorry someone already have a sticky name of them')
            
              
              
        try:

            db.execute("INSERT INTO monitor(target, mentor, guild, nick, before_nick) VALUES(?,?,?,?,?)", user.id, ctx.author.id, ctx.author.guild.id,nicks, user.display_name)
            await user.edit(nick=nicks)
            await ctx.send(f"sticky name added to the {str(user)}")
        except:
            await ctx.send('try again some error occured')
    
    @sticky_name.command(name="list", description = "View list of your stick names", usage = '+sname list')
    @custom_check()
    async def _ls(self, ctx, user : discord.Member = None):
        user = user or ctx.author
        
        data = db.records("SELECT * FROM monitor WHERE mentor = ? and guild = ?", user.id, ctx.guild.id)
        
        if not data:
            return await ctx.send(f"{user.mention}, have no sticky names right now.")


        msg1 = ""
        count = 0
        msg2 = ""
  
        msg3 = ""
        
        
        for entry in data:
            count += 1
            user = ctx.guild.get_member(entry[2])

            nene = '**⠀⠀Sr No. |         Target⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Sticky Name**\n\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\n'

            nene += f'```js\n   {count}      {user.name}#{user.discriminator}               {entry[4]}\n```'
            # msg1 += f"**{count} . **  {entry[5]} \n"

      
            # msg2 += f"**{count} . **  {entry[2]} \n"

            # msg3 += f"**{count} . **  {entry[4]} \n"



     
        embed = discord.Embed(colour=ctx.author.color,description  = f'{nene}')
        # embed.add_field(name= 'User name', value= f' >>> {msg1}', inline = False)
        # embed.add_field(name= 'User id', value= f' >>> {msg2}', inline = False)
        # embed.add_field(name= 'Sticky name', value= f' >>> {msg3}', inline = False)
        embed.set_author(name=f"{user.name}'s list of sticky names", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


        



        
      
        
       

   
    @commands.Cog.listener()
    async def on_member_update(self, before, after):   
        if before.display_name != after.display_name:
            mon = db.record("SELECT * FROM monitor WHERE target = ? and guild = ?", after.id, after.guild.id)
            if mon is None :
                return
            await after.edit(nick = mon[4]) 


    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("sticky")


def setup(bot):
    bot.add_cog(Sticky(bot))


    #make it guild wise