# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 14:13:23 2021

@author: jon-f
"""

import discord
from discord.ext import commands
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import math, csv, os, string, random, json, csv
from collections import OrderedDict
from operator import getitem
import lore_functions, point_functions, chances, norm



bot = commands.Bot(command_prefix='*', description="this is jon's super cool bot")

@bot.command()
async def cmds(ctx):
    cmds_text = "Here are a list of all my commands:\n"
    for command in list(bot.all_commands.keys()):
        cmds_text += command + '\n'
    await ctx.send(cmds_text)
    
@bot.command(help="Gets the user's current level and XP. Type *level!", brief="Get level and XP.")
async def level(ctx):
    auth = ctx.author

    points = point_functions.get_points(auth)
    level = point_functions.get_lvl(auth)
    
    response = f'You are level {level} with {points} points!'
    await ctx.send(response)
    
    
    plt.figure(facecolor='#36393E')

    n = 2
    r = 1.5
    width = r/n
    
    max_level = 30
    
    percent_complete = points/point_functions.inv_curve(level+1)
    
    
    ax = plt.subplot(projection='polar', label='pie')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_thetagrids([0, 90, 180, 270], labels=["0%", "25%", "50%", "75%"])
    ax.set_rgrids([0], labels=[''])
    ax.barh(1, math.radians(360), width*1.25, color='#a574a8')
    ax.barh(0, math.radians(360), width*1.25, color='#628085')
    ax.barh(1, math.radians(percent_complete*360), width, color="#c9a9d4")
    ax.barh(0, math.radians(level/max_level*360), width, color="#a9c5d1")
    
    ax.plot([math.radians(level/max_level*360), math.radians(level/max_level*360)],
            [-width, width/2*1.25], "k--", linewidth=2)
    ax.plot([math.radians(percent_complete*360), math.radians(percent_complete*360)],
            [width*1/1.25/1.25, width/2*1.25+1], "k--", linewidth=2)
    
    t = ax.text(math.radians(30), 1.15, f"Level: {level}", size=20, weight='bold')
    t.set_path_effects([path_effects.PathPatchEffect(
            edgecolor='white', linewidth=1.1, facecolor='black')])
    t = ax.text(math.radians(40), 0.73, f"XP: {points} points", size=16, weight='bold')
    t.set_path_effects([path_effects.PathPatchEffect(
            edgecolor='white', linewidth=1.1, facecolor='black')])
    
    ax.set_facecolor("#36393E")
    plt.savefig("chart.png", dpi=300)
    
    await ctx.send(file=discord.File('chart.png'))

@bot.command(help="Reverses a message. To use, type *reverse <message>", brief="Reverses a message.")
async def reverse(ctx):
    reply = norm.rvr(str(ctx.message.content))[:-8]
    await ctx.send(reply)

@bot.command(help="Starts an instance of the number game! Think of a number and follow the bot's instructions after typing *numgame.", brief="Play the numgame!")
async def numgame(ctx):
    
    reply = await chances.numbergame(ctx, bot)
    return reply

@bot.command(help="Add an item to the lore database. To use, type *lore MM/DD/YYYY <message>", brief="Adds lore to the database")
async def lore(ctx):
    msg = str(ctx.message.content)
    author = str(ctx.author)
    reply = await lore_functions.add_lore(msg, author, ctx)
    await ctx.send(reply)


@bot.command(help="Finds lore containing the tags passed into it. To use, type *lookup <tags> with your tags seperated by spaces", brief="Lookups lore containing the words inputted")
async def lookup(ctx):

    reader = csv.reader(open(datafile))
    async with ctx.typing():
        reply = await lore_functions.lookup(ctx, reader)
    await ctx.send(reply)
    
@bot.command(help="Sets your level-up emoji to any custom emoji! To use, type *setemoji <emoji>", brief="Changes your level-up emoji!")
async def setemoji(ctx):
    full_msg = str(ctx.message.content)
    msg_content = full_msg[full_msg.find(' ')+1:]
    
    if msg_content.startswith('<') and msg_content.endswith('>'):
        point_functions.set_levelup_emoji(ctx.author, msg_content)
        response = f"Set level-up emoji to {msg_content}"
    else:
        response = f"Something went wrong! {msg_content} could not be parsed as a custom emoji!"   
    
    await ctx.send(response)

@bot.command(help="Plays a game of trivia! To play, type *trivia or *trivia <number> for any number of trivia games in a row!", brief="Play trivia games for points!")
async def trivia(ctx):
    
    full_msg = str(ctx.message.content)

    def check(user):
        return user.author == ctx.author
    try:
        games = int(full_msg[full_msg.find(' ')+1:])
    except:
        games = 1
    
    if games > 10 or games < 1:
        await ctx.send("The number of games played must be a number between 1 and 10!")
        return
    
    rng = np.random.default_rng()
    
    difficulty_points = {
        'easy': 3,
        'medium': 5,
        'hard': 10
    }
    
    for game in range(games):
        with open(triviafile) as fp:
            trivia_qs = json.load(fp)        
            question_info = trivia_qs[str(rng.integers(0, len(trivia_qs)))]
        
        question = question_info['question'].replace('&#039;', "'").replace('&amp;', "&").replace('&quot;', '"')
        correct = question_info['correct_answer']
        answers = [correct] + question_info['incorrect_answers']
        difficulty = question_info['difficulty']
        random.shuffle(answers)    
    
        answer_choices = ""
        for i, answer in enumerate(answers):
            answer_choices = answer_choices + f"""{i+1}. {answer.replace('&#039;', "'").replace('&amp;', "&").replace('&quot;', '"')}""" + '\n'
    
        response = f'**Category**: {question_info["category"]}\n**Difficulty**: \
{difficulty}\n\n**Question**: {question}\n\
Answer choices:\n{answer_choices}Type the number of your answer!'
    
        await ctx.send(response)
        msg = await bot.wait_for('message', timeout=15, check=check)
        
        try:
            int(msg.content)
        except:
            await ctx.send("I didn't understand your input! Cancelling.")
            return
        
        if int(msg.content) == answers.index(correct)+1:
            points = difficulty_points[difficulty]
            await ctx.send(f"Correct! You have been awarded {points} points.")
            point_functions.add_points(ctx.author, points)
        else:
            await ctx.send(f"Sorry, that is incorrect. the correct answer was **{answers.index(correct)+1}. {correct}**")


@bot.command(help="Starts a gamble with your points! To play, type *gamble <points> <gamemode>. Current gamemodes: coin, russian.", brief="Gambles with your points!")
async def gamble(ctx):
    full_msg = str(ctx.message.content)
    reply = await chances.game_gamble(full_msg, ctx, bot)    
    await ctx.send(reply)

@bot.command(help="Test if the bot is online. Type *ping", brief="Bot test")
async def ping(ctx):
    await ctx.send("pong!")

@bot.command(help="IDK Alexa wanted it", brief="IDK")
async def bing(ctx):
    await ctx.send("bong https://tenor.com/view/bing-bong-bingbong-tiktok-meme-gif-24189665")

@bot.command(help="Roll a random number for fun. Type *roll or *roll <maximum number>. Some numbers have special responses!", brief="Rolls a random number")
async def roll(ctx):
    msg = str(ctx.message.content)
    reply = norm.roll(msg)
    await ctx.send(reply)

@bot.command(help="ban hammar. to use, type *ban <@user> true/false", brief="ban hammar")
async def ban(ctx):
    if int(ctx.author.id) != int(admin): 
        await ctx.send("You are not an admin!")
        return None
    full_msg = str(ctx.message.content)
    content = full_msg.split(" ")
    
    try:
        content[1], content[2]
    except:
        ctx.send("Error: Command should be of form: *ban <@user> <status>")
        return

    user_to_ban = ctx.message.mentions[0]

    print(user_to_ban.id, 'ban')

    status = True if content[2][0].lower() == "t" else False # checks to see if first letter is t

    point_functions.set_ban_status(user_to_ban, status)
    if status:
        await ctx.send("User banned from jonbot commands.")
    else:
        await ctx.send("User unbanned from jonbot commands.")
    return None
    
@bot.command(help="Displays the current top 10 leaderboard. To use, type *leaderboards", brief="Displays top 10.")
async def leaderboards(ctx):
    ordered = OrderedDict(sorted(point_functions.get_users().items(), 
                             key = lambda x: getitem(x[1], 'points'), reverse=True))
    
    response = "**Top 10 Ranking:**"
    for i, user in enumerate(ordered):
        if i < 10:
            user = await bot.fetch_user(user)
            response = response + "\n" + "          " + f"{i+1}. *{user.display_name}* - {point_functions.get_points(user)} points"
        else:
            break
    await ctx.send(response)
    
@bot.command(help="Plays a game with the bot for points! To use, type *play <game>", brief="Play games with the bot!")
async def play(ctx):
    def check(user):
        return user.author == ctx.author
    await chances.play(ctx, bot)
    await ctx.send("gg")

@bot.command(help="Searches the last 15000 messages for ones sent by the quoted user (or self if none). Sends a random one.", brief="Sends a random messsage")
async def toquote(ctx):
    response, author = await chances.quote(ctx)
    if not response:
        await ctx.send(f"Sorry, I tried REALLY hard and couldn't find a message. Try again!")
    else:
        await ctx.send(f"To quote <@{author}>: {response}")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="jon swags", url="https://twitch.tv/jonsaro/"))
    print("The bot is running!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return None
        
    print(f'{message.author} updated point values!')
    print(f"Message:", message.content)

    if point_functions.add_points(message.author, 1):
        await message.channel.send(f'{message.author.mention} is now level {point_functions.get_lvl(message.author)}! {point_functions.get_levelup_emoji(message.author)}')
        
    if point_functions.get_ban_status(message.author):
        return None

    await bot.process_commands(message)

with open('login.private', 'r') as file:
    file_contents = file.read().split("\n")[:]
    contents = file_contents[4:10]
    datafile, usersfile, triviafile, bot_key1, bot_key2, admin = [cont.strip('\n') for cont in contents]
    
bot.run(bot_key2)