# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 14:13:23 2021

@author: jon-f
"""


import discord
import csv
from discord.ext import commands
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import math
import os
import string
import random
import json
from collections import OrderedDict
from operator import getitem
from lore_functions import isLoreFormat, prepare, generateUID, image_to_edgehex, hash_match
from point_functions import inv_curve, add_points, get_points, get_lvl, set_levelup_emoji, get_levelup_emoji

datafile = 'jonbot.csv'
usersfile = 'users.json'
triviafile = 'trivia.json'

try:
    with open(usersfile) as file:
        users = json.load(file)
except:
    users = {}


#  reverses a string
def rvr(msg):
    assert (type(msg) == str), "Message must be a string!"    
    reversed = ''
    for letter in msg:
        reversed = letter + reversed
    return reversed



bot = commands.Bot(command_prefix='*', description="this is jon's super cool bot")

# commands below
@bot.command()
async def cmds(ctx):
    cmds_text = "Here are a list of all my commands:\n"
    for command in list(bot.all_commands.keys()):
        cmds_text += command + '\n'
    await ctx.send(cmds_text)
    
@bot.command(help="Gets the user's current level and XP. Type *level!", brief="Get level and XP.")
async def level(ctx):
    auth = ctx.author

    points = get_points(auth)
    level = get_lvl(auth)
    
    response = f'You are level {level} with {points} points!'
    await ctx.send(response)
    
    
    plt.figure(facecolor='#36393E')

    n = 2
    r = 1.5
    width = r/n
    
    max_level = 30
    
    percent_complete = points/inv_curve(level+1)
    
    
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
    await ctx.send(rvr(str(ctx.message.content))[:-8])

@bot.command(help="Starts an instance of the number game! Think of a number and follow the bot's instructions after typing *numgame.", brief="Play the numgame!")
async def numgame(ctx):
    def check(user):
        return user.author == ctx.author
    
    await ctx.send("Please think of a number between 0 and 100!")
    low = 0
    high = 100
    userInput = None
    ans = int((low + high)/2)
    
    while True:
        ans = int((low + high)/2)
        await ctx.send("Is your secret number " + str(ans) + "? " + 
                          "Enter 'H' to indicate the guess is too high. " +
                          "Enter 'L' to indicate the guess is too low. " +  
                          "Enter 'C' to indicate I guessed correctly. ")
        
        msg = await bot.wait_for('message', timeout=30, check=check)
        userInput = msg.content
        
        if userInput.lower() == "h":
            high = int(ans)
        elif userInput.lower() == "l":
            low = int(ans)
        elif userInput.lower() == "c":
            await ctx.send("Game over. Your secret number was: "+ str(ans))
            break
        else:
            await ctx.send("Sorry, I did not understand your input.")

@bot.command(help="Add an item to the lore database. To use, type *lore MM/DD/YYYY <message>", brief="Adds lore to the database")
async def lore(ctx):
    msg = str(ctx.message.content)
    author = str(ctx.author)
    if isLoreFormat(msg):
        
        UID = generateUID()
        
        with open(datafile, 'a+', newline='') as file:
            writer = csv.writer(file)
            
            if len(ctx.message.attachments) > 0:
                attachment = ctx.message.attachments[0]
                imagetypes = ['png', 'jpg', 'jpeg']
                
                if any(attachment.filename.lower().endswith(imagetype) for imagetype in imagetypes):
                    await ctx.send(f"Added lore with **UID**={UID} to database with attachment!")
                    await attachment.save(attachment.filename)
                    image = plt.imread(attachment.filename)
                    edgehex = image_to_edgehex(image)
                    os.remove(attachment.filename)

                    writer.writerow([author, msg[6:16], msg[17:].strip(), str(attachment.url), edgehex, UID])
                else:
                    await ctx.send("I didn't understand your attachment filetype. I have still saved it to the database though!")
                    writer.writerow([author, msg[6:16], msg[17:].strip(), str(attachment.url), '', UID])

            else:
                await ctx.send(f"Added lore with **UID**={UID} to database!")
                writer.writerow([author, msg[6:16], msg[17:], '', '', UID])
        print(f"Added lore with UID: {UID} to database!")
    else:
        await ctx.send('Message must be of format "*lore mm/dd/yyyy text..."')

@bot.command(help="Finds lore containing the tags passed into it. To use, type *lookup <tags> with your tags seperated by spaces", brief="Lookups lore containing the words inputted")
async def lookup(ctx):

    reader = csv.reader(open(datafile))
    database = [line for line in reader]
    
    UIDs = [item[5] for item in database]

    def word_mispell_iterator(word):
        mispells = []
        split = list(word)
        for i in range(len(word)):
            for alph_letter in string.ascii_lowercase:
                copy_split = split.copy()
                copy_split[i] = alph_letter
                mispell = ''.join(copy_split)
                if mispell != word:           
                    mispells.append(mispell)
        return mispells
    
    def score_result(tags, item_content, threshold=0.6):
        
        original_words_count = 0
        mispelled_words_count = 0
        
        for tag in tags:
            if tag in item_content:
                original_words_count += 1
            else:
                tag_mispells = word_mispell_iterator(tag)
                for mispell in tag_mispells:
                    if mispell in item_content:
                        mispelled_words_count += 1
                        break
                        
        top_score = len(tags)
        score = original_words_count + mispelled_words_count * 0.25
        did = score/top_score 
        
        return did > threshold, did
    
    async with ctx.typing():
        full_msg = str(ctx.message.content)
        msg_content = full_msg[full_msg.find(' ')+1:]
        
        if msg_content in UIDs:
            # UID match
            
            item_index = UIDs.index(msg_content)
            item = database[item_index]
            matched_items = [item]
            matched_items_results = [1]
        
        elif msg_content == '*':
            response = "The following lore items match your lookup:"
            
            matched_items = database
            
            for i, match in enumerate(matched_items):
                try:
                    attachment = match[3]
                except:
                    attachment = ""
                response = response + '\n\n' + f'Result {i+1} // {match[5]} // 100% match - {match[0]} uploaded lore taking place on {match[1]}:' + "\n" + f"{match[2]}" + "\n" + f'{attachment}'
    
            with open('full_database.txt', 'w') as file:
                file.write(response)
            await ctx.send(file=discord.File('full_database.txt'))
            os.remove('full_database.txt')
            
            return
            
        elif len(ctx.message.attachments) > 0:
            # picture match
            attachment = ctx.message.attachments[0]
            imagetypes = ['png', 'jpg', 'jpeg']
    
            if not any(attachment.filename.lower().endswith(imagetype) for imagetype in imagetypes):
                await ctx.send("Sorry, I did not understand your attachment. Cancelling *lookup.")
                return
                
            await attachment.save(attachment.filename)
            image = plt.imread(attachment.filename)
            img_hash = image_to_edgehex(image)
            os.remove(attachment.filename)
            
            matched_items = []
            matched_items_results = []
    
            for item in database:
                item_hash = item[4]
                if hash_match(item_hash, img_hash, percent_match=0.3)[0]:
                    matched_items.append(item)
                    matched_items_results.append(hash_match(item_hash, img_hash)[1])
        else:
            # string match
            tags = prepare(msg_content).split()
            
            matched_items = []
            matched_items_results = []
    
            for item in database:
                item_content = prepare(item[2]).split(' ')
                if score_result(tags, item_content)[0]:
                    matched_items.append(item)
                    matched_items_results.append(score_result(tags, item_content)[1])
    
        if matched_items and len(matched_items) > 1:
            response = "The following lore items match your lookup:```"
            for i, match in enumerate(matched_items):
                try:
                    attachment = match[3]
                except:
                    attachment = ""
                response = response + '\n\n' + f'Result {i+1} // {match[5]} // {matched_items_results[i]*100:.1f}% match - **{match[0]}** uploaded lore taking place on **{match[1]}**:' + "\n" + f"{match[2]}" + "\n" + f'{attachment}'
            response = response + '```'
            
        elif matched_items and len(matched_items) == 1:
            
            match = matched_items[0]
            
            try:
                attachment = match[3]
            except:
                attachment = ""
            response = f'**{match[0]}** uploaded lore with **UID**={match[5]} taking place on **{match[1]}**:' + "\n" + f"{match[2]}" + "\n" + f'{attachment}'
    
        else:
            response = "Sorry, no items match your search."
        await ctx.send(response)
    
@bot.command(help="Sets your level-up emoji to any custom emoji! To use, type *setemoji <emoji>", brief="Changes your level-up emoji!")
async def setemoji(ctx):
    full_msg = str(ctx.message.content)
    msg_content = full_msg[full_msg.find(' ')+1:]
    
    if msg_content.startswith('<') and msg_content.endswith('>'):
        set_levelup_emoji(ctx.author, msg_content)
        response = f"Set level-up emoji to {msg_content}"
    else:
        response = f"Something went wrong! {msg_content} could not be parsed as a custom emoji!"   
    
    await ctx.send(response)

@bot.command(help="Plays a game of trivia! To play, type *trivia or *trivia <number> for any number of trivia games in a row!", brief="Play trivia games for points!")
async def trivia(ctx):
    def check(user):
        return user.author == ctx.author
    
    full_msg = str(ctx.message.content)
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
            add_points(ctx.author, points)
        else:
            await ctx.send(f"Sorry, that is incorrect. the correct answer was **{answers.index(correct)+1}. {correct}**")


@bot.command(help="Starts a gamble with your points! To play, type *gamble <points> <gamemode>. Current gamemodes: coin, russian.", brief="Gambles with your points!")
async def gamble(ctx):
    
    def check(user):
        return user.author == ctx.author
    
    full_msg = str(ctx.message.content)
    msg_content = full_msg.split(" ")
    
    point_amount = int(msg_content[1])
    gamemode = msg_content[2]
    
    if point_amount > get_points(ctx.author):
        await ctx.send("You do not have enough points. Check your points with *level")
        return
    
    rng = np.random.default_rng()
    
    if gamemode in ['coin', 'flip', 'coinflip']:
        multiplier = 2
        add_points(ctx.author, -1*point_amount)

        result = rng.integers(0, 1, endpoint=True)
        print(result)
        
        await ctx.send('Heads or tails?')
        msg = await bot.wait_for('message', timeout=15, check=check)
        userInput = msg.content.lower()
        
        if userInput in ["heads", "head", "h"]:
            r = 0
        elif userInput in ['tails', 'tail', 't']:
            r = 1
        else:
            await ctx.send("Sorry, I did not understand your response")
            return
        
        if result == r:
            await ctx.send(f'You won the gamble! You won {multiplier*point_amount} points!')
        else:
            multiplier = 0
            await ctx.send(f'Sorry, you lost the gamble. You lost {point_amount} points.')

        if add_points(ctx.author, multiplier*point_amount):
            await ctx.send(f'{ctx.author.mention} is now level {get_lvl(ctx.author)}! {get_levelup_emoji(ctx.author)}')
            
    elif gamemode in ['russian', 'russian_roulette', 'rr', 'roulette']:
        multiplier = 6
        add_points(ctx.author, -1*point_amount)
        result = rng.integers(1, 6, endpoint=True)
        print(result)
        
        await ctx.send('Pick a number 1-6. If your number matches my number, you win! Otherwise, you lose all your points.')
        msg = await bot.wait_for('message', timeout=15, check=check)
        r = int(msg.content)
        
        if result == r:
            await ctx.send(f'You won the gamble! You won {multiplier*point_amount} points!')
        else:
            multiplier = 0
            await ctx.send(f'Sorry, you lost the gamble. You lost {point_amount} points.')

        if add_points(ctx.author, multiplier*point_amount):
            await ctx.send(f'{ctx.author.mention} is now level {get_lvl(ctx.author)}! {get_levelup_emoji(ctx.author)}')
        
    else:
        await ctx.send('Sorry, I do not offer that game yet.')
        return
    
@bot.command(help="Test if the bot is online. Type *ping", brief="Bot test")
async def ping(ctx):
    await ctx.send("pong!")

@bot.command(help="Roll a random number for fun. Type *roll or *roll <maximum number>. Some numbers have special responses!", brief="Rolls a random number")
async def roll(ctx):
    msg = str(ctx.message.content)
    try:
        top = int(msg[msg.find(' '):])
    except:
        top = 1000
    bot = 1
    rng = np.random.default_rng()
    number = rng.integers(bot, top, endpoint=True)
    WYASI = [707, 717, 725, 726, 728, 729, 737, 747, 757, 767, 777, 787, 797]
    
    if number == 727:
        reply = "**WYSI <a:fatyoshi:878367303811608617> 727** " * 10
    elif number in WYASI:
        reply = "wyasi :( " + str(number)
    elif number == 69:
        reply = "lol 69 funny number XD"
    elif number == 420:
        reply = "sm0k3 w33d 3v3ryd@y 420 snoopy poopy XD"
    else:
        reply = str(number)
    await ctx.send(reply)
    
@bot.command(help="Displays the current top 10 leaderboard. To use, type *leaderboards", brief="Displays top 10.")
async def leaderboards(ctx):
    ordered = OrderedDict(sorted(users.items(), 
                             key = lambda x: getitem(x[1], 'points'), reverse=True))
    
    response = "**Top 10 Ranking:**"
    for i, user in enumerate(ordered):
        if i < 10:
            user = await bot.fetch_user(user)
            response = response + "\n" + "          " + f"{i+1}. *{user.display_name}* - {get_points(user)} points"
        else:
            break
    await ctx.send(response)
    
@bot.command(help="Plays a game with the bot for points! To use, type *play <game>", brief="Play games with the bot!")
async def play(ctx):
    def check(user):
        return user.author == ctx.author
    
    async def tictactoe():

        async def display_board(board):
            
            # for python console
            size = board.shape[0]
            
            empty_board = generate_board_string(size)
            empty_values = string.ascii_uppercase[0:size**2]
            
            board_values = board.ravel()
            stringify_board_values = []
            for i, val in enumerate(board_values):
                if val == 0:
                    stringify_board_values.append(empty_values[i])
                elif val == 1:
                    stringify_board_values.append('x')
                else:
                    stringify_board_values.append('•')
                    
            final = '```' + empty_board.format(*stringify_board_values) + '```'
            
            await ctx.send(final)
            
        async def user_select(board):
            
            # for python console
            size = board.shape[0]
        
            selection = ''
            empty_values = string.ascii_uppercase[0:size**2]
            letter_board = np.reshape(list(empty_values), (size, size))
            
            while True:
                msg = await bot.wait_for('message', timeout=20, check=check)
                selection = msg.content.upper()
                
                if selection == "CANCEL":
                    return "cancel"
                
                
                pos = np.where(letter_board == selection)
                
                if board[pos] == 0 and len(pos) > 0:
                    return pos
                else:
                    message = 'Invalid selection! Please try again'
                    await ctx.send(message)
                    
        def end_game_message(winner=None):
            message = "The game is over! "
            
            if winner:
                message = message + f"The winner is {winner}!"
            
            return message
            
        def generate_board_string(size):
            
            pos0 = " {} "
            vdivider = "|"
            hdivider = "-"
            
            row = ((pos0 + vdivider) * size)[:-1]
            
            final = ''
            
            for i in range(size):
                final = final + row + '\n'
                if i != size-1:
                    final = final + hdivider*(len(row)-size) + '\n'
                    
            return final
            
        def scan_for_win(board, marker):
            for row in board:
                if (row == marker).all():
                    return True
            for row in np.transpose(board):
                if (row == marker).all():
                    return True
                
            if all(board[v, v] == marker for v in range(size)):
                return True
            if all(np.flip(board, axis=1)[v, v] == marker for v in range(size)):
                return True
            
            return False
        
        def winning_moves(board, marker=-1):
            # assumes the computer is -1 player
            
            board_vars = []
            
            for i in range(size):
                for j in range(size):
                    if board[i, j] == 0:
                        copy = board.copy()
                        copy[i, j] = marker
                        board_vars.append(copy)
            
            winning_positions = []
            
            for variation in board_vars:
                if scan_for_win(variation, marker):
                    winning_pos = np.where((abs(board-variation) == 1))
                    winning_positions.append(winning_pos)
                    
            return winning_positions
        
        def setup_fork_moves(board, marker=-1):
            
            board_vars = []
            
            for i in range(size):
                for j in range(size):
                    if board[i, j] == 0:
                        copy = board.copy()
                        copy[i, j] = marker
                        board_vars.append(copy)
            
            ways_to_win = len(winning_moves(board, marker))
            
            fork_positions = []
            
            for variation in board_vars:
                if len(winning_moves(variation, marker)) - ways_to_win > 1:
                    fork_pos = np.where(board-variation == 1)
                    fork_positions.append(fork_pos)
            
            return fork_positions
        
        def computer_move(board, marker):
            """
            1. If I can win on this move, do it.
            2. If the other player can win on the next move, block that winning square.
            3. If I can make a move that will set up a fork for myself, do it.
            4. Take the center square if it's free.
            5. Take a corner square if one is free.
            6. Take whatever is available.
            """
                        
            winning_positions = winning_moves(board, turn)
            if winning_positions:
                move = rng.choice(winning_positions)
                return move
            
            opp_winning_positions = winning_moves(board, turn*-1)
            if opp_winning_positions:
                move = rng.choice(opp_winning_positions)
                return move
                        
            fork_positions = setup_fork_moves(board, turn)
            if fork_positions:
                move = rng.choice(fork_positions)
                return move
                
            center = int((size-1)/2)
            if board[center, center] == 0:
                move = (center, center)
                return move
                
            corner_positions = (0, 0), (size-1, size-1), (0, size-1), (size-1, 0)
            corner_values = [board[pos] for pos in corner_positions]
            give_a_chance = rng.choice([0, 1], p=[50/100, 50/100])
            if any(val == 0 for val in corner_values) and give_a_chance:
                empty_corners = [pos for pos in corner_positions if board[pos] == 0]
                move = rng.choice(empty_corners)
                return move
            
            empty_spaces = np.where(board == 0)
            num_empty_spaces = len(empty_spaces[0])
            
            if num_empty_spaces:
                positions = [(empty_spaces[0][i], empty_spaces[1][i]) for i in range(num_empty_spaces)]
                move = rng.choice(positions)
                return move
            
            return None
        
        # game start
        try:
            size = int(msg_content[2])
            if size > 5 or size < 2:
                size = 3
        except:
            size = 3
        
        board = np.zeros((size, size))
        rng = np.random.default_rng()
        turn = rng.choice([-1, 1])
        players = {
        -1: bot.user,
        1: ctx.author}
        
        await ctx.send(f'{players[turn].mention} starts first!')
        
        while True:
            
            if turn == 1:
                await ctx.send(f"{players[turn].mention}'s turn!")
                await display_board(board)
                userPos = await user_select(board)
                if userPos == "cancel":
                    break
                board[userPos] = 1
                
            elif turn == -1:
                await ctx.send("Computer's turn!")
                computerPos = tuple(computer_move(board, marker=-1))
                board[computerPos] = -1
                
            if scan_for_win(board, turn):
                await display_board(board)
                await ctx.send(end_game_message(winner=players[turn]))
                if turn == 1:
                    add_points(ctx.author, point_amount)
                    await ctx.send(f'You won the game! You won {point_amount} points!')
                break
            
            elif (board != 0).all():
                await display_board(board)
                await ctx.send(end_game_message())
                break
                
            turn = turn * -1
            
    
    full_msg = str(ctx.message.content)
    msg_content = full_msg.split(" ")
    
    game = msg_content[1].lower()
    
    if game in ['tictactoe', 'tic-tac-toe', 'ttt']:
        point_amount = 100
        await tictactoe()
    else:
        point_amount = 100
        await tictactoe()



@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="jon swags", url="https://twitch.tv/jonsaro/"))
    print("The bot is running!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return None
    
    if int(message.channel.id) == 832872575704236062 or int(message.channel.id) == 378739394909306901:
        if message.content.startswith('*lore') or message.content.startswith('*lookup'):
            pass
        else:
           return None
        
    print(f'{message.author} updated point values!')

    if add_points(message.author, 1):
        
        await message.channel.send(f'{message.author.mention} is now level {get_lvl(message.author)}! {get_levelup_emoji(message.author)}')
        
    await bot.process_commands(message)

bot.run('ODI3MjU3OTkwMjM1MDI5NTU0.YGYaCg.3zS81Lvr_oTP4SlkOZHtZ7VfIAs')
# bot.run('Mzc4NzM4Nzg5Mzg1ODk1OTM2.WgZl_A.3Ge48SzNwIjzTUznxDdWimxhGnc')