import asyncio
import json
import time

import discord
import requests

import credentials

from discord.ext import commands

bot = commands.Bot(command_prefix="$")
invoker_map = {}
# [:speaking_head:] To Online\n"
#              "[:satellite:] To All\n"
#              "[:microphone2:] To Role",
#         name='\u200b',
#         inline=True
#     )
#     embed.add_field(
#         value="[:loudspeaker:] To Online (embed)\n"
#              "[:satellite_orbital:] To All (embed)\n"
#              "[:no_entry_sign:] Cancel",
# ['\U0001F5E3', '\U0001F4E1', '\U0001F399', '\U0001F4E2', '\U0001F6F0', '\U0001F6AB']:
options = {
    '\U0001F5E3': 'To Online', '\U0001F4E1': 'To All',
    '\U0001F399': 'To Role', '\U0001F4E2': 'To Online (Embed)',
    '\U0001F6F0': 'To All (Embed)', '\U0001F6AB': 'Cancel'
    }


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
    online = sum(
        member.status != discord.Status.offline and not member.bot
        for member in ctx.message.guild.members
    )
    print(len(ctx.message.guild.members))
    all_ = sum(not member.bot for member in ctx.message.guild.members)

    embed.add_field(value="Online", name=online, inline=True)
    embed.add_field(value="All", name=all_, inline=True)
    embed.add_field(value='\u200b', name='\u200b')
    embed.add_field(
        value="\n".join(
            [f"[{k}] {v}"  for k, v in list(options.items())[:3]]
            ),
        name='\u200b',
        inline=True
    )
    embed.add_field(
        value="\n".join(
            [f"[{k}] {v}"  for k, v in list(options.items())[3:]]
            ),
        name='\u200b',
        inline=True
    )

    embed.set_author(name=f"{author}", icon_url=author.avatar_url)
    embed.set_footer(text="Please react with an appropriate action to continue")
    if ctx.message.channel.id not in invoker_map:
        invoker_map[ctx.message.channel.id] = {}

    # Not using delete_after so that there's tighter coupling between message
    # deletion and invoker_map entry deletion
    await ctx.send(embed=embed)
    msg = await ctx.channel.history().get(author__name=bot.user.display_name)
    invoker_map[ctx.message.channel.id][author.id] =  {
        "menu_id": msg.id,
        "broadcast_content": broadcast_msg
    }

    for emoji in options.keys():
        await msg.add_reaction(emoji)

    print(invoker_map)
    print('------------------')
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


@bot.event
async def on_reaction_add(reaction, user):
    channel_id = reaction.message.channel.id

    if channel_id not in invoker_map:
        return
    if user.id not in invoker_map[channel_id]:
        return
    print("Reacted Msg ID:", reaction.message.id)
    print("Menu ID:", invoker_map[channel_id][user.id]["menu_id"])
    if invoker_map[channel_id][user.id]["menu_id"] != reaction.message.id:
        return
    print(f"{reaction}", options)
    if f"{reaction}" not in options:
        await reaction.message.edit(
            embed=reaction.message.embeds[0],
            content="Please choose a valid option"
        )


if __name__ == '__main__':
    bot.run(credentials.TOKEN)
