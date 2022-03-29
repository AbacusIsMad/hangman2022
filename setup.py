import PyInstaller.__main__
import os

PyInstaller.main.run([
     'name-%s%' % 'gamer',
     '--onefile',
     '--windowed',
     '--add-data',
     os.path.join('./', 'hangman.py'), """your script and path to the script"""
])
