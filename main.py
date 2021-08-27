# Imports 
from datetime import datetime
import discord 
from discord.ext import commands, tasks
import os 
import json
import asyncio
from itertools import cycle



bot = commands.Bot(command_prefix=",", intents = discord.Intents.all())
bot.remove_command("help")
status_list = cycle(["DM me for support", "Modmail"])

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Game(name=next(status_list)))


def get_token():
    with open("config.json", "r") as f:
        data = json.load(f)

        return data["token"]


@bot.event 
async def on_ready():
    print(f"{bot.user} is now ready!")
    await bot.wait_until_ready()
    await change_status.start()


@bot.event
async def on_message(message : discord.Message):
    content = str(message.content)
    if content.startswith(bot.command_prefix):
        if message.content ==  ",close":
            await close(message)
        if message.content == ",help":
            await help_(message)
    
    if message.author.bot:
        return 
    if isinstance(message.channel, discord.DMChannel):
        await message.author.send(embed=discord.Embed(title="Sent message!", description = f"{message.content}", colour = discord.Colour.green()))
        guild = bot.get_guild(868226236051255346)

        category = discord.utils.get(guild.categories, name = "Modmail tickets")
        if category == None:
            overwrites_for_category = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                discord.utils.get(guild.roles, id = 879847238715707463): discord.PermissionOverwrite(view_channel=True)
            }
            category = await guild.create_category(name="Modmail tickets", overwrites = overwrites_for_category)
        channel = discord.utils.get(category.channels, name = f"{message.author.id}")
        if channel == None:
            overwrites_for_channel = {
                    message.author: discord.PermissionOverwrite(view_channel=True)
            }
            channel = await category.create_text_channel(name=f"{message.author.id}", overwrites = overwrites_for_channel)
        embed = discord.Embed(title=f"New message", description = message.content, colour = discord.Colour.green())
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        await channel.send(embed=embed)
    if isinstance(message.channel, discord.TextChannel):
        if message.channel.category.name == "Modmail tickets":
            embed = discord.Embed(title="Message sent", description = message.content, colour = discord.Colour.green())
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
            embed = discord.Embed(title="New message", description = message.content, colour = discord.Colour.random())
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            user = bot.get_user(int(message.channel.name))
            await user.send(embed=embed)
    await bot.process_commands(message)


async def close(ctx : commands.Context):
    user = bot.get_user(int(ctx.channel.name))
    if ctx.channel.category.name == "Modmail tickets":
        await ctx.channel.send(f"Deleting channel in 3 seconds")
        await asyncio.sleep(3)
        await ctx.channel.delete()
        await user.send(embed=discord.Embed(title="Ticket closed", description = f"Your ticket has been closed, please note that replying to this message will create another support ticket", colour = discord.Colour.random()))
    else:
        await ctx.channel.send(f"You are not in a modmail channel!")


@commands.command()
async def help_(ctx):
    embed = discord.Embed(title="List of all commands", colour = discord.Colour.random(), timestamp = datetime.now())
    embed.add_field(name="Close", value = "Close the modmail!", inline = False)
    await ctx.channel.send(embed=embed)

bot.run(get_token())