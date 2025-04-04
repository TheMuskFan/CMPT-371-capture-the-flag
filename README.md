# CMPT-371-Project

This project was developed as part of CMPT 371: Data Communications and Networking (Spring 2025) at Simon Fraser University.

It is a multiplayer Capture the Flag game implemented in Python, showcasing real-time communication over a custom client-server architecture using Sockets. The game interface is built with Pygame, allowing 2 to 4 players to compete in a fast-paced arena where players can move, capture, and steal the flag in real time.

## Features

- Real-time multiplayer (2–4 players)
- Client-server architecture using TCP sockets
- Lobby system with ready-up and host-controlled game start
- Flag capturing and adjacent player stealing
- Automatic scoreboard sorting by score
- Spectator mode for non-ready players
- Clean and intuitive Pygame interface

## Installation

Before running the server or client, make sure to install the required dependencies:

```bash
pip install -r requirements.txt
```
## How to Run

### Start the Server
```bash
cd test-server/server
python main.py
```

### Start the Client
```bash
cd test-server/client
python main.py
```

### Select IP address and Port 
When launching the server, you’ll be prompted to enter the IP address and port.
If left blank, the default values will be used:
- IP Address 127.0.0.1
- Port 12345

You will then need to enter in the server's IP address and Port when launching the client.

### Lobby
Once in the lobby, players can select ready and when two or more players are ready, there will be an option to begin the game. Any players that are in the lobby and not ready when the game starts will become spectators

## Authors

- Aki Wangcharoensap
- Josh Chung 
- Karen Sim
- Michael Chandra


