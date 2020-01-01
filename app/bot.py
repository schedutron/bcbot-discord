import discord

import credentials

client = discord.Client()

@client.event
async def on_ready():
    print(f"Logged on as {client.user}!")

if __name__ == '__main__':
    client.run(credentials.TOKEN)
