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


file_path = ''
#executable connects to a stable database that persists when used as a onefile.
def base_path(path):
    dir_path = os.path.join(os.environ['HOME'], 'hangman')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    global file_path
    file_path = os.path.join(dir_path, 'hangman.db')
    #engine = create_engine('sqlite:///' + 'file_path')
    #engine.connect(file_path)
    return dir_path

if __name__ == '__main__':
    app = flask.Flask(__name__)
    base_path('')
    
    #connect to development db (inside directory)
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./hangman.db'
    
    #connect to deployment db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
    
    db = SQLAlchemy(app)

#timer
global i
i = 0
#timer controls
global a
a = 0

# Model

#session number - random but not really important
def random_pk():
    return random.randint(1e9, 1e10)

#pick word
def random_word():
    #TODO: insert difficulty into length of word here!
    words = [line.strip() for line in open('words.txt') if len(line) > 10]
    return random.choice(words).upper()


class Game(db.Model):
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    word = db.Column(db.String(50), default=random_word)
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))
    wordcpy = db.Column(db.String(50), default='')
    triedcpy = db.Column(db.String(50), default='')
    wordlatest = db.Column(db.String(50), default='')
    triedlatest = db.Column(db.String(50), default='')
    streak = db.Column(db.Integer, default = 0)
    streakhidden = db.Column(db.Integer, default = 0)
    taken = db.Column(db.String(50), default='')
    takenhidden = db.Column(db.Integer, default = 0)
    ongoing = db.Column(db.Integer, default = 0)
    difficulty = db.Column(db.Integer, default = 0)
    
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
        return 100*(self.tried != '') + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors)
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


    @property
    def pointscpy(self):
        return 100*(self.triedcpy != '') + 2*len(set(self.wordcpy)) + len(self.wordcpy) - 10*len(self.errorscpy)

    # Play

    def try_letter(self, letter):
        if not self.finished and letter not in self.tried:
            self.tried += letter
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

#create table if it does not exist
db.create_all()


# Controller


@app.route('/')
def home():
    global i
    i = 0
    
    #TODO: move this somewhere else and display it using an iframe. Use buttons to customise how it is sorted.
    games = sorted(
    #bro uses lambda function to further confuse code lmao
        [game for game in Game.query.all() if (game.wordcpy != '')],
        key=lambda game: -game.pointscpy)[:10]
        #displays everyone, if they have finished the game at least once, to prevent blanks
    for bruh in games:
        #resets streak if cheating is detected part 1
        print(bruh.tried != bruh.triedcpy, bruh.tried != '', bruh.ongoing == 1)
        if ((bruh.tried != bruh.triedcpy) and (bruh.tried != '') and (bruh.ongoing == 1)):
            bruh.streak = 0
            bruh.ongoing = 0
            db.session.commit()
        #based lambda returns game points as the sorting method
    print (sorted([game for game in Game.query.all()], key=(lambda game: -game.pointscpy)))
    #if game.won
    


    #whatever I return here, I can use in frontend.
    return flask.render_template('home.html', games=games)


@app.route('/database')
def database():
    games = sorted(
        [game for game in Game.query.all() if (game.wordcpy != '')],
        key=lambda game: -game.pointscpy)[:10]
    return flask.render_template('database.html', games=games)

@app.route('/instructions')
def instructions():
    return flask.render_template('instructions.html')

@app.route('/play')
def new_game():
    #reset timer
    global i
    i = 0
    player = flask.request.args.get('player')
    player = player.strip()
    
    #checking if the name is valid - letters only, no spaces or symbols.
    for k in range(len(player)):
        if not ((65 <= ord(player[k]) <= 90) or (97 <= ord(player[k]) <= 122)):
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
        game.word = random_word()
        game.tried = ''
    else: #create new player object
        game = Game(player)

    
    db.session.add(game)
    game.ongoing = 1
    db.session.commit()
    return flask.redirect(flask.url_for('play', game_id=game.pk))



@app.route('/options/<player>', methods=['GET', 'POST'])
def options(player):
    difficulty = 0
    if flask.request.method == 'POST':
        difficulty = int(flask.request.form['select'])
        if difficulty == -1:
            return flask.redirect(flask.url_for('nearly', player=player))
        print("difficulty is ", difficulty)
        return flask.render_template('options.html', difficulty=difficulty)
    elif flask.request.method == 'GET':
        pass
        #return flask.redirect(flask.url_for('temp', player=player))
    #return flask.redirect(flask.url_for('options', player=player))
    return flask.render_template('options.html', a=a)
    

#@app.route('/play/<game_id>/<a>', methods=['GET', 'POST'])
@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    #game_id is the first entry thus don't need to be done.
    game = Game.query.get_or_404(game_id)
    
    if flask.request.method == 'POST':
        global i
        letter = flask.request.form['letter'].upper()
        if len(letter) == 1 and letter.isalpha():
            print(letter)
            game.try_letter(letter)
            global a
            a = int(((len(game.tried) != 0) and not (game.won or game.lost)))
            print("a is", a)
            #word saving
            if (game.won or game.lost):
                #update scoreboard
                print("progress saved!")
                game.wordlatest = game.word
                game.triedlatest = game.tried
                if (game.points >= game.pointscpy):
                    game.wordcpy = game.word
                    game.triedcpy = game.tried
                print(game.wordcpy, game.triedcpy)
                
                #update time taken
                game.takenhidden = i
                mins, secs = divmod(i, 60)
                game.taken = "{:02d}:{:02d}".format(mins, secs)
                
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
                print("progress not yet saved")

    if flask.request.is_xhr:
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished)
    else: 
        return flask.render_template('play.html', game=game)


#timer
@app.route('/bcontent', methods=['GET'])
def bcontent():
    global i
    global a
    print("timer ", a)
    i += a
    mins, secs = divmod((i), 60)
    small = "{:02d}:{:02d}".format(mins, secs)
    #return flask.Response(small)
    #pass small to render time, pass i to decide which color it is. I also have to pass difficulty here too.
    #maybe also show the time bonus?
    return flask.render_template('timer.html', i=i, small=small)




# Main

#based
def based_path(path):
    if (__file__ == "hangman.py"):
        print("it is in development!")
        return "."
    if getattr(sys, 'frozen', None):
    	basedir = sys._MEIPASS
    else:
    	basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)


if __name__ == '__main__':
    #changes directory if in production
    os.chdir(based_path(''))


    #kill port 5000
    port = 5000
    process = subprocess.Popen(["lsof", "-i", ":{0}".format(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    for process in str(stdout.decode("utf-8")).split("\n")[1:]:
        data = [x for x in process.split(" ") if x != '']
        if (len(data) <=1):
            continue
        
        os.kill(int(data[1]), signal.SIGKILL)
        print("port killed!")

    #wait a bit for game to load, then open browser.
    threading.Timer(1.5, lambda: webbrowser.open("http://0.0.0.0:5000")).start()
    #port = int(os.environ.get('PORT', 5000))
    running = app.run(host='0.0.0.0', debug=False)
