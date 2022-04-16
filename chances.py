import string
import random
import numpy as np
import datetime as dt
import point_functions
from discord.ext import commands


async def game_gamble(msg, ctx, bot):
    def check(user):
        return user.author == ctx.author

    author = ctx.author

    msg_content = msg.split(" ")
    point_amount = int(msg_content[1])
    gamemode = msg_content[2]
    
    if point_amount > point_functions.get_points(author):
        return 0, "You do not have enough points. Check your points with *level."
        
    if gamemode in ['coin', 'flip', 'coinflip']:
        reply = coinflip(author, point_amount, check, ctx, bot)
    elif gamemode in ['russian', 'russian_roulette', 'rr', 'roulette']:
        reply = rr(author, point_amount, check, ctx, bot)
    else:
        reply = 'Sorry, I do not offer that game yet.'
    return reply

async def coinflip(author, point_amount, check, ctx, bot):
    rng = np.random.default_rng()

    multiplier = 2
    point_functions.add_points(author, -1*point_amount)

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
        reply = f'You won the gamble! You won {multiplier*point_amount} points!'
    else:
        multiplier = 0
        reply = f'Sorry, you lost the gamble. You lost {point_amount} points.'

    if point_functions.add_points(ctx.author, multiplier*point_amount):
        await ctx.send(f'{ctx.author.mention} is now level {point_functions.get_lvl(ctx.author)}! {point_functions.get_levelup_emoji(ctx.author)}')
    return reply

async def rr(author, point_amount, check, ctx, bot):
    rng = np.random.default_rng()

    multiplier = 6
    point_functions.add_points(author, -1*point_amount)
    result = rng.integers(1, 6, endpoint=True)
    print(result)
    
    await ctx.send('Pick a number 1-6. If your number matches my number, you win! Otherwise, you lose all your points.')
    msg = await bot.wait_for('message', timeout=15, check=check)
    r = int(msg.content)
    
    if result == r:
        reply = f'You won the gamble! You won {multiplier*point_amount} points!'
    else:
        multiplier = 0
        reply= f'Sorry, you lost the gamble. You lost {point_amount} points.'

    if point_functions.add_points(ctx.author, multiplier*point_amount):
        await ctx.send(f'{ctx.author.mention} is now level {point_functions.get_lvl(ctx.author)}! {point_functions.get_levelup_emoji(ctx.author)}')
    return reply

async def play(ctx, bot):
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
                    point_functions.add_points(ctx.author, point_amount)
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

async def numbergame(ctx, bot):
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

async def quote(ctx, attempts=150):

    full_msg = str(ctx.message.content)
    msg_content = full_msg.split(" ")

    try:
        user_to_search = ctx.message.mentions[0].id
    except:
        try:
            msg_content[1]
            start_at = msg_content[1].index("@") + 1
            end_at = msg_content[1].index(">")
            user_to_search = msg_content[1][start_at:end_at]
        except:
            user_to_search = ctx.author.id

    async with ctx.channel.typing():
        end = dt.datetime.today() - dt.timedelta(days=1)

        for i in range(attempts):
            start = dt.datetime.today() - dt.timedelta(days=random.randint(0, 365*2))
            channel_messages = await ctx.channel.history(limit=100, before=end, after=start).flatten()   
            for message in channel_messages: 
                if int(message.author.id) == int(user_to_search):
                    return message.content, user_to_search
            
        return False, user_to_search
