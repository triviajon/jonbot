# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 10:21:45 2021

@author: jon-f
"""

from turtle import update
from skimage.transform import resize
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime as dt
import string
import csv
import lore_functions
from discord import File
from ftplib import FTP

with open('login.private', 'r') as file:
    file_contents = file.read().split("\n")[:]
    datafile, usersfile, triviafile, bot_key1 = file_contents[4:8]

# checks if msg is of format "-lore mm/dd/year text......"
def isLoreFormat(msg):
    checkedN = [msg[6:8], msg[9:11], msg[12:16]]
    try:
        checkedS = [msg[5], msg[16]]
    except IndexError:
        checkedS = [msg[5]]
    flag = True
    for text in checkedN:
        if not text.isnumeric():
            flag = False
    for text in checkedS:
        if text != ' ':
            flag = False
    return flag

# checks if msg is of format "-lookup mm/dd/yyyy mm/dd/yyyy"
def isDateLookupFormat(msg):
    checkedN = [msg[8:10], msg[11:13], msg[14:18], msg[19:21], msg[22:24], msg[25:29]]
    checkedS = [msg[7], msg[18]]
    flag = True
    for text in checkedN:
        if not text.isnumeric():
            flag = False
    for text in checkedS:
        if text != ' ':
            flag = False
    return flag

def textToDTObj(text):
    # converts mm/dd/yyyy to datetime obj
    dtobj = dt.datetime.strptime(text, '%m/%d/%Y')
    return dtobj

def extractDates(msg):
    # gets lookup command and returns the two dates
    t1 = textToDTObj(msg[8:18])
    t2 = textToDTObj(msg[19:29])
    return t1, t2

def prepare(plaintext):
    stripped = plaintext.translate(str.maketrans('', '', string.punctuation))\
        .lower()
    return stripped

# comomands for image hexing
def binary_array_to_hex(arr):

	bit_string = ''.join(str(int(b)) for b in arr.flatten())
	width = int(np.ceil(len(bit_string)/4))
	return '{:0>{width}x}'.format(int(bit_string, 2), width=width)

def image_to_edgehex(numpy_image):
    numpy_array = resize(numpy_image, (64, 64))
    
    size = numpy_array.shape
    grayscale = np.zeros(size[:-1])
    grayscale1der = np.zeros(size[:-1])
    
    for i in range(size[0]):
        for j in range(size[1]):
            
            if size[2] == 4:
                val = numpy_array[i, j]
                n_val = (0.299*val[0]+0.587*val[1]+0.114*val[2])*val[3]
            elif size[2] == 3:
                val = numpy_array[i, j]
                n_val = 0.299*val[0]+0.587*val[1]+0.114*val[2]
            else:
                n_val = numpy_array[i, j]
            
            grayscale[i, j] = n_val
            
            if i == 0 or j == 0:
                continue
            
            sub = grayscale[i-1:i+1, j-1:j+1]
            
            dIdx = 1/2 * ((sub[0, 1] - sub[0, 0]) + (sub[1, 1] - sub[1, 0]))
            dIdy = 1/2 * ((sub[1, 0] - sub[0, 0]) + (sub[1, 1] - sub[0, 1]))
            
            dIdp = abs(dIdx/2 + dIdy/2)
            if dIdp < 0.03:
                continue
            
            grayscale1der[i, j] = 1
        
    return binary_array_to_hex(grayscale1der)

def hamming_distance(hash1, hash2):
    dist = sum(n1 != n2 for n1, n2 in zip(hash1, hash2))
    return dist

def hash_match(hash1, hash2, percent_match=.6):
    # returns True if at least percent_match % 
    if len(hash1) == 0 or len(hash2) == 0:
        return (False, 0)
    result = 1-hamming_distance(hash1, hash2)/len(hash1)
    return result > percent_match, result

def generateUID(UIDlen=5):

    reader = csv.reader(open(datafile))
    currentUIDs = []
    for line in reader:
        try:
            currentUIDs.append(line[5])
        except:
            pass
    
    rng = np.random.default_rng()
    letters = list(string.ascii_uppercase)
    UID = ''.join(rng.choice(letters, size=UIDlen))
    
    while UID in currentUIDs:
        UID = ''.join(rng.choice(letters, size=UIDlen))

    return UID

async def add_lore(msg, author, ctx):
    if not lore_functions.isLoreFormat(msg):
        return 'Message must be of format "*lore mm/dd/yyyy text..."'

    UID = lore_functions.generateUID()
    print(f"Adding lore with UID: {UID} to database.")
    with open(datafile, 'a+', newline='') as file:
        writer = csv.writer(file)
        
        if len(ctx.message.attachments) > 0:
            attachment = ctx.message.attachments[0]
            imagetypes = ['png', 'jpg', 'jpeg']
            if any(attachment.filename.lower().endswith(imagetype) for imagetype in imagetypes):
                await attachment.save(attachment.filename)
                image = plt.imread(attachment.filename)
                edgehex = lore_functions.image_to_edgehex(image)
                os.remove(attachment.filename)
                content = [author, msg[6:16], msg[17:].strip(), str(attachment.url), edgehex, UID]
                writer.writerow(content)
                return_msg = f"Added lore with **UID**={UID} to database with attachment!"
            else:
                content = [author, msg[6:16], msg[17:].strip(), str(attachment.url), '', UID]
                writer.writerow(content)
                return_msg =  "I didn't understand your attachment filetype. I have still saved it to the database though!"
        else:
            content = [author, msg[6:16], msg[17:], '', '', UID]
            writer.writerow(content)
            return_msg = f"Added lore with **UID**={UID} to database!"
    update_content(content)
    return return_msg

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

async def lookup(ctx, reader):
    database = [line for line in reader]
    UIDs = [item[5] for item in database]

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
        await ctx.send(file=File('full_database.txt'))
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
        img_hash = lore_functions.image_to_edgehex(image)
        os.remove(attachment.filename)
        
        matched_items = []
        matched_items_results = []

        for item in database:
            item_hash = item[4]
            if lore_functions.hash_match(item_hash, img_hash, percent_match=0.3)[0]:
                matched_items.append(item)
                matched_items_results.append(lore_functions.hash_match(item_hash, img_hash)[1])
    else:
        # string match
        tags = lore_functions.prepare(msg_content).split()
        
        matched_items = []
        matched_items_results = []

        for item in database:
            item_content = lore_functions.prepare(item[2]).split(' ')
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

def update_content(content, server_file='public_html/lore/index.html', login_file="login.private", temp_file="temp.html"):
    def add_line(html_file, content_list):
        add, date, detail, attach, edgehex, uid = content_list

        if attach: attach = f"<a href={attach}> Attachment </a>"

        with open(html_file, 'r') as file:
            content = file.read()
        
        content = [elm.lstrip() for elm in content.split("\n")]
        insert_add = content.index("</tbody>")

        to_add = f"<tr> <td>{add}</td> <td>{date}</td> <td>{detail}</td> <td>{attach}</td> <td>{uid}</td></tr> \n"

        content.insert(insert_add, to_add)

        with open(html_file, 'w') as file:
            file.write("\n".join(content))
        return '\n'.join(content)
    
    with open(login_file, 'r') as file:
        host, user, pw, port = file.read().split("\n")[0:4]
    
    if host.startswith("ftp://"): host = host[6:]

    with FTP(host) as ftp:
        ftp.login(user, pw)
        spl = server_file.split("/")
        for dir in spl[:-1]:
            ftp.cwd(dir)
        filename = spl[-1]
        ftp.retrbinary(f"RETR {filename}", open(temp_file, "wb").write)
        add_line(temp_file, content)
        ftp.storbinary(f"STOR {filename}", open(temp_file, 'rb'))
        print("added to online database")
    return None