# this is a file for normal functions
# (ones that don't require an async call)
import numpy as np

def roll(msg):
    """
    Rolling functionality. Currently defaults to top=1000  or tries to find an integer passed in after a space.
    Returns a random number from 0 to top. Defined below are special case numbers. 
    """
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
    return reply

def rvr(msg):
    assert (type(msg) == str), "Message must be a string!"    
    reversed = ''
    for letter in msg:
        reversed = letter + reversed
    return reversed

