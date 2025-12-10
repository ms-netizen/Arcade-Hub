Arcade Hub

Arcade Hub is a collection of classic games built in Python and served through a Flask interface. 
The project includes fully functional versions of Roulette, Rock Paper Scissors, Tetris, and Uno. 
The website front page is written using HTML and Bootstrap.
This project combines Tkinter, Pygame, Flask, HTML, CSS, and custom assets.

Features
Flask Web Interface
The main backend logic is handled by the Flask app in app.py. 
It manages routing, API endpoints, and communication with each game script.

Roulette (Pygame)
A roulette game with wheel physics, bets, colors, and score tracking.

Uno (Tkinter)
A full Uno match with AI opponents, card logic, turn system, color selection, and a modern interface.

Rock Paper Scissors (Tkinter)
Includes both Player versus Computer and Player versus Player modes with keyboard controls and visual feedback.

Tetris (Pygame)
A falling block puzzle game with scoring, animation, record keeping, and custom themed backgrounds.

Frontend Website
A responsive landing page that is simple, and built using HTML and Bootstrap.


Folder Structure
Arcade-Hub/
│
├── app.py
|
├── templates
  ├──index.html
├── roulette.py
├── uno game.py
├── tetris game.py
├── rock paper scissors game.py
│
├── pic1.jpeg
├── pic2.jpg
├── font1.otf
├── font2.otf

How to Run
1. Install required modules

pip install flask pygame
Tkinter is included with Python on most systems.

Start the Flask application
python app.py

Open the local site
Navigate to:
http://localhost:5000

Launch any game
Use the buttons on the homepage to start Roulette, RPS, Tetris, or Uno.
Each game opens in a separate window.
