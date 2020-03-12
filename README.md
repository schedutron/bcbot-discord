# BcBot

BcBot is a neat, generic broadcast bot for Discord guilds (servers). To set up, make a `credentials.py` file first:
```
$ cp credentials.py.example credentials.py
```

Now, paste your Discord bot token in the `credentials.py` file.

Next, while in the root of the repository, install dependencies via
```
$ python3 -m pip install -r requirements.txt
```
You can also set up a virtual environment if you want, but it's not necessary.

Now, (again while in the root of the repo), start the bot with:
```
$ python3 -m app.bot
```

## Short Demo:
![Small demo gif for the broadcast bot usage](/demo.gif)