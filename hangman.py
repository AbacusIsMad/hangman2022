import random
import threading
import webbrowser
import flask
import time
from flask_sqlalchemy import SQLAlchemy
import os, sys
import signal
import subprocess
import time
import math
import numpy
import string
import sqlalchemy.exc
import sqlalchemy_utils.functions

#indicate creation errors.
global errno
errno = 0
global fatal
fatal = 0
file_path = ''
dir_path = ''
#executable connects to a stable database that persists when used as a onefile.
def base_path(path):
    #dir_path = os.path.join(os.environ['HOME'], 'hangman')
    global file_path, dir_path, errno
    if getattr(sys, 'frozen', None):
        dir_path = os.path.join(os.path.dirname(sys.executable), 'hangman')
    else:
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hangman')
        #dir_path = os.path.join('/hangman0', 'hangman')
    
    #checking if permissions allow me to create separate db
    #if the database already exists
    print("Can I write to database file?", os.access(file_path, os.W_OK)) #this is good
    print("Can I write to database parent file?", os.access(dir_path, os.W_OK)) #this is not good
    #both the above needs to be true
    #if either of them dont exist, I check by creating the dir, then if it is already there, seeing if the dir is writable. Again both of them needs to be true.
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except PermissionError:
            print("failed to make file! Defaulting to current directory.")
            dir_path = '.'
            errno = 1
    elif not os.access(dir_path, os.W_OK):
        print("directory is not writable! Defaulting to current directory.")
        dir_path = '.' 
        errno = 1  
    file_path = os.path.join(dir_path, 'hangman.db')
    return file_path

#os.path.isfile
#FileExistsError
#PermissionError



if __name__ == '__main__':
    app = flask.Flask(__name__)
    #base_path('')
    
    #connect to development db (inside directory)
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./hangman.db'
    
    #connect to deployment db
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + base_path('')
    db = SQLAlchemy(app)
    print("valid database? ", sqlalchemy_utils.functions.database_exists(app.config['SQLALCHEMY_DATABASE_URI']))
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./hangman.db'
    #db = SQLAlchemy(app)

#globals() can see these names now
def lent(item):
    return len(item)

def lenth(item):
    return item

#timer
global i
i = 0
#timer controls
global a
a = 0
#difficulty
global difficulty
difficulty=0
#Database sorting variables
global lastReq
lastReq = 7
global hello
hello = 7
global recent
recent = 0
#player input error
global invalidPlayer
invalidPlayer = 0
global invalidLetter
invalidLetter = 0
# Model


#session number - random but not really important
def random_pk():
    return random.randint(1e9, 1e10)

#pick word
def random_word():
    global difficulty
    secret = Game.query.filter_by(player=".secret").limit(1).first()
    words = [line.strip() for line in open('words.txt') if ((len(line) > (9 - 3 * difficulty)) & (len(line) < 18 - 5 * difficulty))]
    if (secret is not None): 
        if (secret.ongoing == 1):
            words = ""
            for i in range(random.randint(11, 18)):
                words += random.choice(string.ascii_letters)
            return words.upper()
    return random.choice(words).upper()

#g = [line.strip() for line in open('words.txt') if len(set(line)) > 13]
#print(g) #max different letters = 14

class Game(db.Model):
    #cpy stores highest score, latest stores latest score
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    #word = db.Column(db.String(50), default=random_word)
    word = db.Column(db.String(50), default='')
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))
    playerlower = db.Column(db.String(50))
    wordcpy = db.Column(db.String(50), default='')
    triedcpy = db.Column(db.String(50), default='')
    wordlatest = db.Column(db.String(50), default='')
    triedlatest = db.Column(db.String(50), default='')
    streak = db.Column(db.Integer, default = 0)
    streakhidden = db.Column(db.Integer, default = 0)
    takenlatest = db.Column(db.String(50), default='')
    takenhiddenlatest = db.Column(db.Integer, default = 0)
    takencpy = db.Column(db.String(50), default='')
    takenhiddencpy = db.Column(db.Integer, default = 0)
    pointslatest = db.Column(db.Integer, default = 0)
    pointscpy = db.Column(db.Integer, default = 0)
    ongoing = db.Column(db.Integer, default = 0)
    #extra = db.Column(db.Integer, default = 0)
    
    """also store word and tried in a copied location. The server should display the copied ones.
    the copy is only updated if the game is finished and redirected to home.
    However, the streak (TBA) should be updated nonetheles."""
    
    def __init__(self, player):
        self.player = player

    #receive the requested object as an actual readable name, not just object pointers
    def __repr__(self):
        return '%r' % self.player

    @property
    def errors(self):
        return ''.join(set(self.tried) - set(self.word))

    @property
    def errorscpy(self):
        return ''.join(set(self.triedcpy) - set(self.wordcpy))

    @property
    def errorslatest(self):
        return ''.join(set(self.triedlatest) - set(self.wordlatest))

    @property
    def current(self):
        return ''.join([c if c in self.tried else '_' for c in self.word])
        """people say the python is just the english language but its precisely because its like english that
        makes it impossible to understand. """

    @property
    def currentcpy(self):
        return ''.join([c if c in self.triedcpy else c.lower() for c in self.wordcpy])

    #I don't think this is used.
    @property
    def points(self):
        #set() gives a set with no repetitions, basically the number of unique letters in the word.
        #return 100*(self.tried != '') + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors)
        
        if (len(set(self.word)) >= 4):
            base_score = round(100 + 10 * (14 ** (1/2.2) - ((len(set(self.word)) - 4) ** (1/2.2))) + (len(set(self.word)) ** 1.3))
        else: #rip i forgot complex numbers existed
            base_score = round(100 + 10 * (14 ** (1/2.2) + ((-len(set(self.word)) + 4) ** (1/2.2))) + (len(set(self.word)) ** 1.3))
        time_bonus = round((50 + 40 * (difficulty ** 2) - 2 * len(set(self.word)) - math.exp(3 * (len(set(self.word)) - 50 + difficulty * 10)))/10)
        time_bonus = round(time_bonus / 2 + abs(time_bonus / 2))
        error_penalty = -time_bonus + round(time_bonus / ((len(self.errors) + 1) ** 2)) - round((1 - 0.84 * self.lost) * len(self.errors) * (len(set(self.word))) / 1.3)
        game_penalty = round(-(0.6 * base_score) * (self.lost))
        print("score determined! ", [base_score, time_bonus, error_penalty, game_penalty])
        return [base_score, time_bonus, error_penalty, game_penalty]
        """
        NEW SCORING SYSTEM
        has 4 factors: number of unique letters in words, proportion of those words that have been guessed,
        the number of errors, and time taken
        Proportion is not affected by any other factors.
        The number of unique letters affects the strength of error penalties:
        -the more letters are there, the penalty for error is greater.
        The error panalty affects both the raw score and the time bonus.
        It affects the time bonus more stronly:
        -a quadratic reduction; no errors gives the best bonus while any errors reduce it by a large margin,
        -with full errors completely negating the bonus.
        The number of unique letters give a small decrease to the base score.
        Points =
        unique(word)*k*(proportion)*m, k < 0.5, m = base score
        - errors*l*unique(word), l = penalty multiplier
        +errors^(1/b)*p*(maxtime - timetaken), p = penalty multiplier
        Might add difficulty into account, I'm not sure.
        """

    # Play

    def try_letter(self, letter):
        if not self.finished and letter not in self.tried:
            self.tried += letter
            print("tried letters: ", self.tried)
            db.session.commit()

    # Game status

    @property
    def won(self):
        return self.current == self.word

    @property
    def lost(self):
        return len(self.errors) == 6

    @property
    def finished(self):
        return self.won or self.lost

#create table if it does not exist. TODO: add permission protection here!
#sudo mv /home/elec1005/Downloads/hangman2022/dist/hangmang /hangmang

"""try:
    db.create_all()
    secret = Game.query.filter_by(player=".secret").limit(1).first()
    if (secret is None):
        secretg = Game(".secret")
        secretg.ongoing = 0
        db.session.add(secretg)
        db.session.commit()
except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
    print("database is invalid!")
    if (True or getattr(sys, 'frozen', None)):
    #the executable treats this by simply redirecting
        print("redirecting to internal database!")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./hangman.db'
        db = SQLAlchemy(app)
        print("created app!")
        db.create_all()
        secret = Game.query.filter_by(player=".secret").limit(1).first()
        if (secret is None):
            secretg = Game(".secret")
            secretg.ongoing = 0
            db.session.add(secretg)
            db.session.commit()
        errno = 1
    else:
    #the script shows a warning
        print("invalid database in production will result in a fatal error.")
        fatal = 1"""
        
#db.create_all()   
#rip spent like 3 hours on the last day here to replicate ONE built in method
#new cleaner method now.
#does the file exist at that location?
print("database exists?", os.access(file_path, os.F_OK))
"""if not (os.access(file_path, os.F_OK)):
    print("creating new database...")
    db.create_all()
    secretg = Game(".secret")
    secretg.ongoing = 0
    db.session.add(secretg)
    db.session.commit()"""
#well it exists, but is it valid?
if not (sqlalchemy_utils.functions.database_exists(app.config['SQLALCHEMY_DATABASE_URI'])):
    if not (os.access(file_path, os.F_OK)):
        print("creating new database...")
        db.create_all()
        secretg = Game(".secret")
        secretg.ongoing = 0
        db.session.add(secretg)
        db.session.commit()
    #okay its not valid, do something about it.
    elif (False or getattr(sys, 'frozen', None)):
        print("database is invalid!")
        print("redirecting to internal database!")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./hangman.db'
        print("created app!")
        db.create_all()
        secret = Game.query.filter_by(player=".secret").limit(1).first()
        if (secret is None):
            secretg = Game(".secret")
            secretg.ongoing = 0
            db.session.add(secretg)
            db.session.commit()
        errno = 1
    else:
    #the script shows a warning
        print("invalid database in production will result in a fatal error.")
        fatal = 1



#os.F_OK
print("Can I write to database file now?", os.access(file_path, os.W_OK))
print("Can I write to database parent file now?", os.access(dir_path, os.W_OK))
#secret = Game.query.filter_by(player=".secret").limit(1).first()
#if (secret is None):
    #secretg = Game(".secret")
    #secretg.ongoing = 0
    #db.session.add(secretg)
    #db.session.commit()

# Controller

@app.route('/')
def home():
    global i
    i = 0
    #invalid player check
    m = 0;
    global invalidPlayer
    global file_path
    if invalidPlayer == 1:
        m = 1
    invalidPlayer = 0
        #displays everyone, if they have finished the game at least once, to prevent blanks
    if (fatal == 1):
        return flask.render_template('home.html', m = m, errno = errno, fatal = fatal, file_path = os.path.abspath(file_path))
    for bruh in Game.query.all():
        #resets streak if cheating is detected part 1
        #print(bruh.tried != bruh.triedlatest, bruh.tried != '', bruh.ongoing == 1)
        if ((bruh.tried != bruh.triedlatest) and (bruh.tried != '') and (bruh.ongoing == 1)):
            bruh.streak = 0
            bruh.ongoing = 0
            db.session.commit()
        #based lambda returns game points as the sorting method
    #print (sorted([game for game in Game.query.all()], key=(lambda game: -game.pointscpy)))
    #if game.won

    #whatever I return here, I can use in frontend.
    return flask.render_template('home.html', m = m, errno = errno, fatal = fatal, file_path = os.path.abspath(file_path))

@app.route('/database', methods = ['GET', 'POST'])
def database():
    global hello
    global lastReq
    global recent
    toggled = 0
    #cope
    seethe = [0, 1, "playerlower", "word", 4, "errors", 6, "points", 8, 9, 10, "takenhidden", 12, "streak"]
    mald = ['cpy', 'latest']
    
    #Depending on the column header clicked (E.g Score or Player), sorts the database alphabetically or numerically (depending on data type).
    #inverts the list if the same button is clicked again, much like normal database tables.
    if flask.request.method == 'POST':
        temp = int(flask.request.form['select'])
        #toggle between highest score and most recent score for players
        if (temp == -1):
            recent = int(recent != 1)
            toggled = 1
        else:
            hello = temp
        #check if a different button is pressed
        if ((lastReq % hello > 0)):
            lastReq = 0
        if (toggled == 0):
            lastReq = lastReq + hello - (2 * hello * (lastReq == hello))
        print("hello: ", hello, "lastReq: ", lastReq)
        #Prime numbers because we wanted unique moduli that wouldn't interfere with each other
        #what a sigma solution
    elif flask.request.method == 'GET':
        pass
    games = sorted(
    [game for game in Game.query.all() if (game.wordcpy != '')],
    key=lambda game: globals()["lent" + "h" * (hello != 5)]
    (getattr(game, seethe[hello] + mald[recent] * (hello == 3 or hello == 5 or hello == 7 or hello == 11))),
    reverse=(lastReq != hello) != (hello == 7 or hello == 13))[:10]
    return flask.render_template('database.html', games=games, hello=hello, lastReq=lastReq, recent=recent)

@app.route('/instructions', methods = ['GET', 'POST'])
def instructions():
    secret = Game.query.filter_by(player=".secret").limit(1).first()
    if flask.request.method == 'POST':
        if (int(flask.request.form['secret']) == 1):
            secret.ongoing = int(secret.ongoing != 1)
            db.session.commit()
    return flask.render_template('instructions.html', secret=secret.ongoing)

@app.route('/play')
def new_game():
    #reset timer
    global i
    i = 0
    global invalidPlayer
    player = flask.request.args.get('player')
    player = player.strip()
    
    #checking if the name is valid - letters only, no spaces or symbols.
    for k in range(len(player)):
        if not ((65 <= ord(player[k]) <= 90) or (97 <= ord(player[k]) <= 122) or (player[k] == ' ')):
            invalidPlayer = 1
            return flask.redirect(flask.url_for('home'))
        if (k > 15):
            invalidPlayer = 1
            return flask.redirect(flask.url_for('home'))

    #go to difficulty select page
    return flask.redirect(flask.url_for('options', player=player))
    
@app.route('/nearly/<player>')
def nearly(player):

    #check for past logins:
    past_player = Game.query.filter_by(player=player).limit(1).first()
    if (past_player is not None):
        print("player already exists!", past_player)
        game = past_player
        #resets streak if cheating is detected part 2
        if ((game.tried != game.triedcpy) and (game.tried != '') and (game.ongoing == 1)):
            game.streak = 0
    

        #reroll random word for new game, and reset the game status as well. 
        #(resetting word and tried should do it.)
        #game.word = random_word()
        game.tried = ''
    else: #create new player object
        game = Game(player)
        game.playerlower = game.player.lower()
    global i
    i = 0
    game.word = random_word()
    print("game.word = ", game.word)
    db.session.add(game)
    game.ongoing = 1
    db.session.commit()
    return flask.redirect(flask.url_for('play', game_id=game.pk))



@app.route('/options/<player>', methods=['GET', 'POST'])
def options(player):
    global difficulty
    #difficulty persists across different sessions
    if flask.request.method == 'POST':
        if int(flask.request.form['select']) != -1:
            difficulty = int(flask.request.form['select'])
        else:
            return flask.redirect(flask.url_for('nearly', player=player))
        
        print("difficulty is ", difficulty)
        return flask.render_template('options.html', difficulty=difficulty, player=player)
    elif flask.request.method == 'GET':
        pass
        #return flask.redirect(flask.url_for('temp', player=player))
    #return flask.redirect(flask.url_for('options', player=player))
    return flask.render_template('options.html', difficulty=difficulty, player=player)
    

#@app.route('/play/<game_id>/<a>', methods=['GET', 'POST'])
@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    #game_id is the first entry thus don't need to be done.
    game = Game.query.get_or_404(game_id)
    global a
    global i
    global difficulty
    global invalidLetter
    #print("difficulty is in play:", difficulty)
    if len(game.tried) == 0:
        i = 0
        a = 0
    invalidLetter = 0
    secret = Game.query.filter_by(player=".secret").limit(1).first()
    
    if flask.request.method == 'POST':
        letter = flask.request.form['letter'].upper()
        if len(letter) == 1 and letter.isalpha():
            print(letter)
            temp = game.tried
            game.try_letter(letter)
            if temp == game.tried:
                invalidLetter = 1
            a = int(((len(game.tried) != 0) and not (game.won or game.lost)))
            print("a: ", a, "invalidLetter: ", invalidLetter)
            #word saving
            if (game.won or game.lost):
                print("progress saved!")
                #update word
                game.wordlatest = game.word
                game.triedlatest = game.tried
                
                game.pointslatest = sum(list(game.points))
                #update time taken
                game.takenhiddenlatest = i
                mins, secs = divmod(i, 60)
                game.takenlatest = "{:02d}:{:02d}".format(mins, secs)                
                if (sum(list(game.points)) >= game.pointscpy):
                    game.pointscpy = sum(list(game.points))
                    game.wordcpy = game.word
                    game.triedcpy = game.tried
                    game.takencpy = game.takenlatest
                    game.takenhiddencpy = game.takenhiddenlatest
                print(game.wordcpy, game.triedcpy)
                
                #update streak
                if game.won:
                    game.streak += 1
                    game.streakhidden = 1
                    print("WON")
                #has a buffer against wrong word since it's so easy to die
                elif (game.streak > 0):
                    if (game.streakhidden == 0):
                        game.streak -= 1
                    else:
                        game.streakhidden = 0
                game.ongoing = 0
                db.session.commit()
            else:
                pass
                #print("progress not yet saved")
        else:
            invalidLetter = 1        
    if flask.request.is_xhr:
        #print("parsing request!")
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished, invalidLetter=invalidLetter)
    else: 
        return flask.render_template('play.html', game=game, difficulty=difficulty, invalidLetter=invalidLetter, secret=secret.ongoing)


#timer
@app.route('/bcontent', methods=['GET'])
def bcontent():
    global i
    global a
    global difficulty
    i += a
    mins, secs = divmod((i), 60)
    small = "{:02d}:{:02d}".format(mins, secs)
    #pass small to render time, pass i to decide which color it is. I also have to pass difficulty here too.
    #maybe also show the time bonus?
    return flask.render_template('timer.html', i=i, small=small, difficulty=difficulty)




# Main

#based
def based_path(path):
    #if (__file__ == "hangman.py"):
    #    print("it is in development!")
    #    return "."
    if getattr(sys, 'frozen', None):
    	basedir = sys._MEIPASS
    else:
    	basedir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basedir, path)

print(fatal, errno)
if __name__ == '__main__':
    #changes directory if in production
    os.chdir(based_path(''))

    #kill port
    port = 42069
    process = subprocess.Popen(["lsof", "-i", ":{0}".format(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    for process in str(stdout.decode("utf-8")).split("\n")[1:]:
        data = [x for x in process.split(" ") if x != '']
        if (len(data) <=1):
            continue
        os.kill(int(data[1]), signal.SIGKILL)
        print("port killed!")

    #wait a bit for game to load, then open browser.
    threading.Timer(2, lambda: webbrowser.open("http://0.0.0.0:" + str(port))).start()
    #print(globals())
    #app.run(host='0.0.0.0', port=port, debug=False)
    app.run(host=os.getenv('IP', '0.0.0.0'), 
        port=int(os.getenv('PORT', port)), debug=False)
