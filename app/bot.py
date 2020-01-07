import asyncio
import json
import time

import discord
import requests

import credentials

from discord.ext import commands

bot = commands.Bot(command_prefix="$")
invoker_map = {}

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


@bot.command()
async def bcbot(ctx, *, broadcast_msg):
    author = ctx.message.author
    admin_role_pos = discord.utils.get(
        ctx.message.guild.roles, name='Admin'
        ).position
    print(admin_role_pos)
    print(max([role.position for role in author.roles]))
    print('----')
    if max([role.position for role in author.roles]) < admin_role_pos:
        return
    if author.id in invoker_map.get(ctx.message.channel.id, {}):
        return  # Allow only one message at a time per user per channel

    #print(time.ctime())
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

    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    embed.set_footer(text="Please react with an appropriate action to continue")
    if ctx.message.channel.id not in invoker_map:
        invoker_map[ctx.message.channel.id] = {}
    invoker_map[ctx.message.channel.id][author.id] =  {
        "menu_id": ctx.message.id,
        "broadcast_content": broadcast_msg
    }
    await ctx.send(embed=embed)
    msg = await ctx.channel.history().get(author__name=bot.user.display_name)
    # Manually adding reactions for now
    for emoji in ['\U0001F5E3', '\U0001F4E1', '\U0001F399', '\U0001F4E2', '\U0001F6F0', '\U0001F6AB']:
        await msg.add_reaction(emoji)
    print(invoker_map)
    await asyncio.sleep(60)
    del invoker_map[msg.channel.id][author.id]  # Delete entry on timeout
    await msg.delete()
    return

    await ctx.send(f"Broadcast started at: {time.ctime()}")
    for member in ctx.message.guild.members:
        if member == bot.user:
            continue
        channel = member.dm_channel
        if channel is None:
            channel = await member.create_dm()

        try:
            await channel.send(
                broadcast_msg
            )
            #count += 1
        except discord.errors.Forbidden as e:
            continue
        except Exception as be:
            print(be)

    print(time.ctime())
    await ctx.send(f"Broadcast ended at: {time.ctime()}")


if __name__ == '__main__':
    bot.run(credentials.TOKEN)
