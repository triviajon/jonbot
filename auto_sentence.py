# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 19:43:43 2021

@author: jon-f
""".

@bot.command()
async def past_messages(ctx):
    
    full_msg = str(ctx.message.content)
    msg_content = full_msg.split(" ")
    
    try:
        user_to_search = msg_content[1]
    except:
        user_to_search = ctx.author
        
    async with ctx.channel.typing():
        channel_messages = await ctx.channel.history(limit=10000).flatten()

    messages = []   
    with open('author_messages.txt', 'w', encoding="utf-8") as file:
        for message in channel_messages: 
            if message.author.id == user_to_search.id:
                messages.append(message.content)
                file.write((message.content + " "))
            
            
    await ctx.send(f"{user_to_search} has sent {len(messages)} in the last 10k messages!")


# https://towardsdatascience.com/using-a-markov-chain-sentence-generator-in-python-to-generate-real-fake-news-e9c904e967e
import pandas as pd

with open('author_messages.txt', 'r', encoding='utf-8') as file:
    words = file.read().split(' ')

dict_df = pd.DataFrame(columns = ['lead', 'follow', 'freq'])
dict_df['lead']=words
follow = words[1:]
follow.append('EndWord')

dict_df['freq']= dict_df.groupby(by=['lead','follow'])['lead','follow'].transform('count').copy()


dict_df = dict_df.drop_duplicates()
pivot_df = dict_df.pivot(index = 'lead', columns= 'follow', values='freq')

sum_words = pivot_df.sum(axis=1)
pivot_df = pivot_df.apply(lambda x: x/sum_words)

from numpy.random import choice
def make_a_sentence(start):
    word= start
    sentence=[word]
    while len(sentence) < 15:
        next_word = choice(a = list(pivot_df.columns), p = (pivot_df.iloc[pivot_df.index ==word].fillna(0).values)[0])
        if next_word == 'EndWord':
                continue

        else:
            sentence.append(next_word)
        word=next_word
    sentence = ' '.join(sentence)
    return sentence
sentence = make_a_sentence('hello')