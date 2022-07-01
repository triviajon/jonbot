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

def add_to_public(content, server_file='public_html/SKEG/index.html', login_file="login.private", temp_file="temp_public.html"):
    def add_line(html_file, content_list):
        user, time, message = content_list

        with open(html_file, 'r') as file:
            content = file.read()
        
        content = [elm.lstrip() for elm in content.split("\n")]
        insert_add = content.index("<p></p>")

        to_add = f"<p></p>\n<p><b>{user}</b> {time}: {message}\n"

        content.insert(insert_add, to_add)

        with open(html_file, 'w') as file:
            file.write("\n".join(content))
        return '\n'.join(content)
    
    with open(login_file, 'r') as file:
        host, user, pw, _ = file.read().split("\n")[0:4]
    
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
        print("added to $SKEG")
    return None