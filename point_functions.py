# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 10:23:50 2021

@author: jon-f
"""

import json

with open('login.private', 'r') as file:
    file_contents = file.read().split("\n")[:]
    datafile, usersfile, triviafile, bot_key1 = file_contents[4:8]

try:
    with open(usersfile) as file:
        users = json.load(file)
except:
    users = {}

def get_users():
    return users

def save_users():
    with open(usersfile, 'w') as file:
        json.dump(get_users(), file, indent=5)    

def level_curve(points):
    if points <= 0:
        return 0
    return int((points/10)**(1/2))+1

def inv_curve(level):
    if level <= 0:
        return 0
    return 10*(level-1)**2

def add_points(user, points):
    users = get_users()
    id = str(user.id)
    if id not in users:
        users[id] = {}
        users[id]["lvl"] = 0
        users[id]["emoji"] = '<a:fatyoshi:878367303811608617>'
    
    curr_points = users[id].get("points", 0) + points
    users[id]["points"] = int(curr_points)

    if level_curve(curr_points) != users[id]["lvl"]:
        users[id]["lvl"] = level_curve(curr_points)
        save_users()
        return True
    
    save_users()
    return False

def get_points(user):
    id = str(user.id)
    users = get_users()
    if id in users:
        return users[id].get("points", 0)
    return 0

def get_lvl(user):
    id = str(user.id)
    users = get_users()
    if id in users:
        return users[id].get("lvl", 0)
    return 0

def set_levelup_emoji(user, emoji):
    id = str(user.id)
    users = get_users()
    
    users[id]["emoji"] = emoji
    save_users()
    
def get_levelup_emoji(user):
    id = str(user.id)
    users = get_users()
    
    return users[id]["emoji"]

def get_ban_status(user, use_id=False):
    if not use_id:
        id = str(user.id)
    users = get_users()

    if users[id].get("ban", None) == None:
        users[id]["ban"] = False
    
    save_users()
    return users[id]["ban"]

def set_ban_status(user, status, use_id=False):
    if not use_id:
        id = str(user.id)
    users = get_users()

    users[id]["ban"] = status
    save_users()
    return status