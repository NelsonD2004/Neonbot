import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from discord import ui
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import os
import asyncio
import twitchio
from twitchio.ext import commands as cmd

import datetime
from typing import List

from discord.interactions import Interaction

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())
con = sqlite3.connect("C:/Users/nelso/OneDrive/Desktop/HenryBot/Stats.db")
cur = con.cursor()



@tasks.loop(minutes=1.0)
async def auto_stream_start():
    global ISLIVE
    channel = bot.get_channel(1112906850090893362)
    guild = bot.get_guild(1112902755426783394)
    role = guild.get_role(1114393370744340621)
    cur.execute("SELECT Live FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    liveStatus = cur.fetchone()[0]
    cur.execute("SELECT Title FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    title = cur.fetchone()[0]
    cur.execute("SELECT Game FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    gameName = cur.fetchone()[0]
    cur.execute("SELECT Noti FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    ISLIVE = cur.fetchone()[0]

    if liveStatus == "True" and ISLIVE == 'False':
        message = await channel.send(embed=EmbedSections.twitch_noti(title, gameName.upper()))
        with open('notiID.txt', "r+") as file:
            file.truncate(0)
            file.writelines(str(message.id))
        await channel.send(role.mention)
        ISLIVE = 'True'
    elif liveStatus == "True" and ISLIVE == 'True':
        with open('notiID.txt', "r+") as file:
            id = file.readline()
            message = await channel.fetch_message(int(id))
        await message.edit(embed=EmbedSections.twitch_noti(title, gameName.upper()))
    else:
        pass
    

@tasks.loop(minutes=1.0)
async def auto_stream_end():
    channel = bot.get_channel(1112906850090893362)
    guild = bot.get_guild(1112902755426783394)
    role = guild.get_role(1114393370744340621)
    cur.execute("SELECT Live FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    liveStatus = cur.fetchone()[0]
    cur.execute("SELECT Noti FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    ISLIVE = cur.fetchone()[0]

    if liveStatus == "False" and ISLIVE == 'True':
        await channel.purge(limit=10)
        cur.execute(f"UPDATE Live_Info SET Noti = '{False}' WHERE Noti = 'True'")
        con.commit()


@bot.event
async def on_ready():
    print("Bot is up")
    auto_stream_start.start()
    auto_stream_end.start()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


#Choices testing
@bot.tree.command(name="test", description="This is used for testing!")
@app_commands.choices(choices=[
    app_commands.Choice(name="Yes", value="yep"),
    app_commands.Choice(name="No", value="yep")
])
async def test(interaction: discord.Interaction, choices: app_commands.Choice[str]):
        if (choices.value == 'yep'):
            await interaction.response.send_message(content="Alright!", ephemeral=True)
        else:
            await interaction.response.send_message(content="Nope!")

#       ACTUAL BOT        #
#-------------------------#
class Variables():
    alternate = False #Button alternate functions. (Off by default)
    notiamount = 0

class EmbedSections():

    def title_card():
        embed = discord.Embed(title="Tatox3 Menu", color=0x6FFF7B)
        embed.set_image(url="https://media.giphy.com/media/pYy1pETzRveSzWQmEz/giphy.gif")
        return embed

    def help_body(name, avatar_url):
        embed=discord.Embed(color=0x6FFF7B)
        embed.set_author(name=f'\n{name}', icon_url=avatar_url)
        embed.add_field(name="🟣 Subscriber roles 🟣", value="To get access to your twitch roles if you are subscribed please ensure you have the twitch connection enabled in your personal account settings and we do the rest.", inline=False)
        embed.add_field(name="🟣 Twitch Live Notifications 🟣", value=f"To get notified when Tatox3 goes live on twitch head over to #live-notifications in order to get the notification role")
        embed.add_field(name="🚧 More helpful tips to be added soon...🚧\nIf you have any suggestions notify any of the admins", value="", inline=False)
        embed.set_footer(text="If you require further assistance, click on the option you are confused about using the buttons below.")
        return embed

    def twitch_body(name, avatar_url):
        embed = discord.Embed(color=0x6FFF7B)
        embed.set_author(name=f'\n{name}', icon_url=avatar_url)
        embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjZjZTZiZWQxOGY5YWE0NzIwOThkZDM0YjQxZDJhOTUwN2ZmZjU1ZiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/gli9wNZ5gt2gy9m2Zg/giphy.gif")
        embed.add_field(name="Further assistance:", value="Below you can find a gif of where you should be looking in your settings to enable your twitch connection.", inline=False)
        embed.add_field(name="", value="1. Go to your settings\n2. Click on the 'Connections' tab\n3. Click on the twitch Icon\n4. Authorize the connection through twitch")
        embed.set_footer(text="If you do not find it useful you can contact a moderator or admin.")
        return embed

    def twitch_noti_body(name, avatar_url, channel):
        embed = discord.Embed(color=0x6FFF7B)
        embed.set_author(name=f'\n{name}', icon_url=avatar_url)
        embed.add_field(name="Further assistance:", value="", inline=False)
        embed.add_field(name="", value=f"1. Go to {channel.mention} at the top of the discord\n2. Click on the reaction for which you want to get notified for!")
        embed.set_footer(text="If you do not find it useful you can contact a moderator or admin.")
        return embed

    def twitch_noti(title, game):
        channel = bot.get_channel(1112906850090893362)
        guild = bot.get_guild(1112902755426783394)
        embed = discord.Embed(title=f"{title}", description=f"TATOX3 IS LIVE ON TWITCH PLAYING {game} COME JOIN!", url="https://www.twitch.tv/tatox3_", color=0x6441a5)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1112902756022358039/1120788781268750437/20230620_145403.jpg") #https://i.pinimg.com/originals/da/99/60/da99605920778b7b85b4fbb96cbacb78.gif
        #https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNmFiY2ZlZjUxMmJiYmU0Yzc1ZTY4NGNhNTBkODQ2MDhhODcwODczMyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/SMoMrhoSQvPBXhxqzj/giphy.gif
        return embed
    
    
    def leaderboard_body(result):
        count = 0
        embed = discord.Embed(title="POTATO LEADERBOARD", color=0x6FFF7B)
        embed.set_thumbnail(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdWZvbXVvYmdjNW92ZTNua2EwZWRobnV1N2VqMHBlemM2aWk3eWVjcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/24vTxomgaewVz5ZwPx/giphy.gif")
        embed.add_field(name=f"LEADER: {result[0][0]} -> {result[0][1]} potatoes", value=f"· • —–—– ٠ ✤ ٠ —–—– • ·")
        for i in result:
            if count > 0:
                embed.add_field(name=f"#{count+1} {result[count][0]}: {result[count][1]}", value="", inline=False)
            count += 1
        embed.set_footer(text="Chat in Henry's twitch chat to earn more")
        return embed



class MenuButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.green)
    async def One(self, interaction: discord.Interaction, button: discord.Button):
        self.Two.disabled = True
        try:
            if Variables.alternate == False:
                button.label = "Back"
                await interaction.response.edit_message(embeds=[EmbedSections.title_card(), EmbedSections.twitch_body(interaction.user.name, interaction.user.avatar.url)], view=self)
                Variables.alternate = True
            else:
                await interaction.response.edit_message(embeds=[EmbedSections.title_card(), EmbedSections.help_body(interaction.user.name, interaction.user.avatar.url)], view=MenuButtons())
                Variables.alternate = False
        except Exception as e:
            print(e)

    @discord.ui.button(label='2', style=discord.ButtonStyle.green)
    async def Two(self, interaction: discord.Interaction, button: discord.Button):
        self.One.disabled = True
        try:
            if Variables.alternate == False:
                button.label = "Back"
                await interaction.response.edit_message(embeds=[EmbedSections.title_card(), EmbedSections.twitch_noti_body(interaction.user.name, interaction.user.avatar.url, channel=bot.get_channel(1114394449657745488))], view=self)
                Variables.alternate = True
            else:
                await interaction.response.edit_message(embeds=[EmbedSections.title_card(), EmbedSections.help_body(interaction.user.name, interaction.user.avatar.url)], view=MenuButtons())
                Variables.alternate = False
        except Exception as e:
            print(e)
    
    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def Exit(self, interaction: discord.Interaction, Button: discord.Button):
        await interaction.response.edit_message(view=None, content="Exited.", embed=None)

class ClearModal(ui.Modal, title='Clear Command'):
    amount = ui.TextInput(label='How much do you want to delete?', style=discord.TextStyle.short,required=True)
    member = ui.TextInput(label="Member name (Optional)", style=discord.TextStyle.short, required=False, default=None)
    reason = ui.TextInput(label="Reason (Optional)", style=discord.TextStyle.paragraph, required=False, default=None)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if self.member.value == "":
                await interaction.channel.purge(limit=int(self.amount.value), reason=self.reason.value)
                await interaction.response.send_message(f"Chat was cleared by: {interaction.user.mention} ({int(self.amount.value)} messages cleared!)", delete_after=30)
            else:
                await interaction.channel.purge(limit=int(self.amount.value), reason=self.reason.value, check=lambda m: m.author.name == self.member.value)
                await interaction.response.send_message(f"{self.member.value}'s chat was cleared by: {interaction.user.mention} ({int(self.amount.value)} messages cleared!)", delete_after=30)
        except Exception:
            await interaction.response.send_message("Hmmm... Something went wrong! Please make sure you put a valid integer as an amount.", ephemeral=True, delete_after=10)



@bot.event
async def on_member_join(person):
    await person.add_roles(person.guild.get_role(1112902914160197724))

@bot.event
async def on_raw_reaction_add(payload):
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    global member
    member = payload.member
    guild = bot.get_guild(1112902755426783394)
    twitch_role = guild.get_role(1114393370744340621)
    music_role = guild.get_role(1114396915400986734)
    if message.id == 1114942064321376256:
        if str(payload.emoji) == "🟣":
            await payload.member.add_roles(twitch_role)
        if str(payload.emoji) == "🎶":
            await payload.member.add_roles(music_role)

@bot.event
async def on_raw_reaction_remove(payload):
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    guild = bot.get_guild(1112902755426783394)
    twitch_role = guild.get_role(1114393370744340621)
    music_role = guild.get_role(1114396915400986734)
    if message.id == 1114942064321376256:
        if str(payload.emoji) == "🟣":
            await member.remove_roles(twitch_role)
        if str(payload.emoji) == "🎶":
            await member.remove_roles(music_role)


@bot.tree.command(name="discord-help")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(embeds=[EmbedSections.title_card(), EmbedSections.help_body(interaction.user.name, interaction.user.avatar.url)], view=MenuButtons(), ephemeral=True, delete_after=120)


@bot.tree.command(name="clear")
@app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction):
    await interaction.response.send_modal(ClearModal())


@bot.tree.command(name="whiffs")
async def Whiff(interaction: discord.Interaction):
    point = cur.execute("SELECT Amount From Whiff")
    result = point.fetchone()
    await interaction.response.send_message(f"Henry has been caught whiffing {result[0]} times on stream!\n\nIf you catch him whiffing do !whiff on his stream", ephemeral=False)

@bot.tree.command(name="link", description="Link the discord bot to your twitch account **CASE SENSITIVE**")
async def link(interaction: discord.Interaction, twitchname: str=None):
    channel = bot.get_channel(1119398653468082270)
    if twitchname is None:
        await interaction.response.send_message("Please specify your twitch username...")
    else:
        try:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE TwitchName = '{twitchname}'")
            result = cur.fetchone()
            cur.execute(f"SELECT DiscordID FROM Economy WHERE TwitchName = '{twitchname}'")
            discord_result = cur.fetchone()
            if int(discord_result[0]) != 0:
                await interaction.response.send_message(f"This twitch name has already been registered to a user with the ID {discord_result[0]}", ephemeral=True)
            if result is None:
                pass
            if int(discord_result[0]) == 0:
                cur.execute(f"UPDATE Economy SET DiscordID = {interaction.user.id} WHERE TwitchName = '{twitchname}'")
                con.commit()
                await interaction.response.send_message(f"{twitchname} and {interaction.user.name} have been linked succesfully!")
                await channel.send(
                f"""- - - LINK INFO:
                Discord Name: {interaction.user.name}
                Twitch Name: {twitchname}
                Discord ID: {interaction.user.id}
                LINK SUCCESSFUL""")
                #FUcking make it an embed pls
        except Exception as e:
            await interaction.response.send_message("Please enter a valid twitch username, make sure you have sent at least 1 message in twitch chat", ephemeral=True)

@bot.tree.command(name="balance", description="Gets the balance of twitch potatoes")
async def bal(interaction: discord.Interaction):
    user_id = interaction.user.id
    cur.execute(f'SELECT DiscordID FROM Economy WHERE DiscordID = {user_id}')
    result = cur.fetchall()
    try:
        if result is None:
            pass
        else:
            cur.execute(f"SELECT Potatoes FROM Economy WHERE DiscordID = {user_id}")
            result = cur.fetchone()
            await interaction.response.send_message(f"Your current potato balance is {result[0]}", ephemeral=True)
    except:
        await interaction.response.send_message("Please use /link (twitch username) to link this bot to your twitch account and access your potatoes!")


@bot.tree.command(name="leaderboard", description="Displays the top 5 potato owners in Henry's stream!")
async def leaderboard(interaction: discord.Interaction):
    cur.execute(f'SELECT TwitchName, Potatoes FROM Economy ORDER BY Potatoes DESC LIMIT 5')
    result = cur.fetchall()
    await interaction.response.send_message(embed=EmbedSections.leaderboard_body(result=result))

@bot.tree.command(name="rank", description="Shows your ranking on the potato leaderboard")
async def rank(interaction: discord.Interaction):
    count = 0
    cur.execute(f'SELECT DiscordID, Potatoes FROM Economy ORDER BY Potatoes DESC')
    result = cur.fetchall()

    for i in result:
        count += 1
        if i[0] == interaction.user.id:
            await interaction.response.send_message(f"{interaction.user.mention} you are rank #{count} on the potato leaderboard with {i[1]} potatoes")
bot.run("MTExMjQ2OTY4MDU5NTE1MjkxNw.Gkw5Br.rrW9d2huMMaDruE2lzL33cchKH3xq7S12ilDp8")
#-------------------------------------------------------------------#