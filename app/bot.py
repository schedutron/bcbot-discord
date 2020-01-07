import json
import time

import discord
import requests

import credentials

from discord.ext import commands

bot = commands.Bot(command_prefix="$")

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


@bot.command()
async def bcbot(ctx, *, broadcast_msg):
    author = ctx.message.author
    admin_role_pos = discord.utils.get(
        ctx.message.guild.roles, name='Admin'
        ).position
    if max([role.position for role in author.roles]) < admin_role_pos:
        return
    print(time.ctime())
    embed = discord.Embed(title="New Broadcast", color=0x000000)
    embed.add_field(
        value="[:speaking_head:] To Online\n"
             "[:satellite:] To All\n"
             "[:microphone2:] To Role",
        name='\u200b',
        inline=True
    )
    embed.add_field(
        value="[:loudspeaker:] To Online (embed)\n"
             "[:satellite_orbital:] To All (embed)\n"
             "[:no_entry_sign:] Cancel",
        name='\u200b',
        inline=True
    )

    #     value="To Online", inline=True)
    # embed.add_field(name=":satellite:", value="To All")
    # embed.add_field(name=":microphone2:", value="To Role")

    # embed.add_field(name=":loudspeaker:", value="To Online (embed)")
    # embed.add_field(name=":satellite_orbital:", value="To All (embed)")
    # embed.add_field(name=":no_entry_sign:", value="Cancel")
    # embed.set_thumbnail(
    #     url="https://dl.dropboxusercontent.com/s/iwigx2ywlycfpyz/cell-tower.svg?dl=0"
    # )
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    embed.set_footer(text="Please react with an appropriate action to continue")
    await ctx.send(embed=embed)
    msg = await ctx.channel.history().get(author__name=bot.user.display_name)
    # Manually adding reactions for now
    print(msg.guild.emojis)
    for emoji in ['\U0001F5E3', '\U0001F4E1', '\U0001F399', '\U0001F4E2', '\U0001F6F0', '\U0001F6AB']:
        await msg.add_reaction(emoji)

    return
    await ctx.send(f"Broadcast started at: {time.ctime()}")
    for member in ctx.message.guild.members:
        if member == bot.user:
            continue
        channel = member.dm_channel
        if channel is None:
            channel = await member.create_dm()

        # r = requests.post(
        #     f'https://discordapp.com/api/channels/{channel.id}/messages',
        #     data=data,
        #     headers = {
        #         'Authorization': f"Bot {credentials.TOKEN}",
        #         'Content-Type': 'application/json'
        #         }
        # )

        try:
            await channel.send(
                broadcast_msg
            )
            #count += 1
        except discord.errors.Forbidden as e:
            continue
        except Exception as be:
            print(be)
        # if count % 5 == 0:
        #     print("sleeping")
        #     time.sleep(3)
    print(time.ctime())
    await ctx.send(f"Broadcast ended at: {time.ctime()}")


if __name__ == '__main__':
    bot.run(credentials.TOKEN)
