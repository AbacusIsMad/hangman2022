import random
import threading
import webbrowser
import flask
import time
from flask_sqlalchemy import SQLAlchemy
#from flask_socketio import SocketIO, disconnect

app = flask.Flask(__name__)


# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./hangman.db'
db = SQLAlchemy(app)

"""#establish package connection
socketio = SocketIO(app)


#detect abrupt logoffs
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('client_disconnecting')
def disconnect_details(data):
    print('user disconnected.')

@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    socketio.emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)
mhm mhm this didn't work for some reason. I will thus not rely on packages and implement the similiar structure on the database level
"""


# Model

#session number - random but not really important
def random_pk():
    return random.randint(1e9, 1e10)

#pick word
def random_word():
    words = [line.strip() for line in open('words.txt') if len(line) > 10]
    return random.choice(words).upper()


class Game(db.Model):
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    word = db.Column(db.String(50), default=random_word)
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))
    wordcpy = db.Column(db.String(50), default='')
    triedcpy = db.Column(db.String(50), default='')
    streak = db.Column(db.Integer, default = 0)
    
    """also store word and tried in a copied location. The server should display the copied ones.
    the copy is only updated if the game is finished and redirected to home.
    However, the streak (TBA) should be updated nonetheles."""
    #player is gotten externally
    
    def __init__(self, player):
        self.player = player

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
        return 100 + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors)
        """
        NEW SCORING SYSTEM
        has 4 factors: number of unique letters in words, proportion of those words that have been gotten,
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
        +errors^0.5*p*(maxtime - timetaken), p = penalty multiplier
        """
        return 

    @property
    def pointscpy(self):
        return 100 + 2*len(set(self.wordcpy)) + len(self.wordcpy) - 10*len(self.errorscpy)

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


# Controller

@app.route('/bcontent', methods=['GET'])
def bcontent():
    
    def timer(t):
        global i
        i = 0
        while True:
            time.sleep(1) #put 60 here if you want to have seconds
            mins, secs = divmod(i, 60)
            #flask.Response(i, mimetype='text/html')
            print(i)
            yield "{:02d}:{:02d}".format(mins, secs)
            i += 1
    return flask.Response(['a', 'b', 'c', 'd', 'e', 'f', 'g'])





@app.route('/')
def home():
    games = sorted(
    #bro uses lambda function to further confuse code lmao
        [game for game in Game.query.all()],
        key=lambda game: -game.points)[:10]
        #based lambda returns game points as the sorting method
    print (sorted([game for game in Game.query.all()], key=(lambda game: -game.points)))
    #if game.won
    
    #testinglol = Game.query.filter_by(player="josh").limit(1).first()
    #print(testinglol)

    return flask.render_template('home.html', games=games)

@app.route('/play')
def new_game():
    player = flask.request.args.get('player')
    player = player.strip()
    
    #checking if the name is valid - letters only, no spaces or symbols.
    valid = 1
    for i in range(len(player)):
        if not ((65 <= ord(player[i]) <= 90) or (97 <= ord(player[i]) <= 122)):
            valid = 0
            return flask.redirect(flask.url_for('home'))

    #check for past logins:
    past_player = Game.query.filter_by(player=player).limit(1).first()
    if (past_player is not None):
        print("player already exists!", past_player)
        game = past_player
        print (type(game.word))
#reroll random word for new game, and reset the game status as well. (resetting word and tried should do it.)
        
        game.word = random_word()
        game.tried = ''
    else:
        game = Game(player)

    
    db.session.add(game)
    db.session.commit()
    i = 0;
    return flask.redirect(flask.url_for('play', game_id=game.pk))

@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    #game_id is the first entry thus don't need to be done.
    game = Game.query.get_or_404(game_id)

    if flask.request.method == 'POST':
        letter = flask.request.form['letter'].upper()
        if len(letter) == 1 and letter.isalpha():
            print(letter)
            game.try_letter(letter)
            #put saving stuff here?
            if (game.won or game.lost):
                print("progress saved!")
                game.wordcpy = game.word
                game.triedcpy = game.tried
                print(game.wordcpy, game.triedcpy)
                db.session.commit()
            else:
                print("progress not yet saved")

    if flask.request.is_xhr:
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished)
    else: 
        return flask.render_template('play.html', game=game)






# Main
import os, sys
import signal
import subprocess

def base_path(path):
    if getattr(sys, 'frozen', None):
    	basedir = sys._MEIPASS
    else:
    	basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == '__main__':
    #os.chdir(base_path(''))
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
