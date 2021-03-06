# Hangman

Simple hangman game implemented with Flask

# Installation

## Option 1: Ubuntu packages

    sudo apt-get install python-flask python-flask-sqlalchemy

## Option 2: pip

[Install pip](https://pip.pypa.io/en/stable/installing/), then:

    pip install Flask Flask-SQLAlchemy

# Run

    python hangman.py

Create dabase with:

    python -c 'from hangman import db; db.create_all()'
    
# Compilation

    pyinstaller --onefile --add-data 'templates:templates' --add-data 'static:static' --add-data 'hangman.db:.' --add-data 'words.txt:.' hangman.py -n hangmang --clean

# Links

* Hangman github repository: https://github.com/vlopezferrando/hangman
* Slides: https://slides.com/victorlf/flask
* Flask: http://flask.pocoo.org
* Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/en/2.x/
* Jinja2: http://jinja.pocoo.org/docs/dev/
* Bootstrap: http://getbootstrap.com
* JQuery: https://jquery.com
