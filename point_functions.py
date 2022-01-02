# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 10:23:50 2021

@author: jon-f
"""

import json

usersfile = 'users.json'
triviafile = 'trivia.json'

try:
    with open(usersfile) as file:
        users = json.load(file)
except:
    users = {}



def save_users():
    with open(usersfile, 'w') as file:
        json.dump(users, file, indent=5)    

def level_curve(points):
    if points <= 0:
        return 0
    return int((points/10)**(1/2))+1

def inv_curve(level):
    if level <= 0:
        return 0
    return 10*(level-1)**2

def add_points(user, points):
    
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
    if id in users:
        return users[id].get("points", 0)
    return 0

def get_lvl(user):
    id = str(user.id)
    if id in users:
        return users[id].get("lvl", 0)
    return 0

def set_levelup_emoji(user, emoji):
    id = str(user.id)
    
    users[id]["emoji"] = emoji
    save_users()
    
def get_levelup_emoji(user):
    id = str(user.id)
    
    return users[id]["emoji"]