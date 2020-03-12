import asyncio
import json
import datetime
from math import ceil

import discord

import credentials

bot = discord.Client()
invoker_map = {}
options = {
    '\U0001F5E3': 'To Online', '\U0001F4E1': 'To All',
    '\U0001F399': 'To Role', '\U0001F4E2': 'To Online (Embed)',
    '\U0001F6F0': 'To All (Embed)', '\U0001F6AB': 'Cancel'
    }

prefix = "#bc "

async def invoke_menu(recv_msg):
    if recv_msg.channel.id in invoker_map:
        if recv_msg.author.id in invoker_map[recv_msg.channel.id]:
            return

    author = recv_msg.author
    admin_role_pos = discord.utils.get(
        recv_msg.guild.roles, name='Admin'
        ).position

    if max([role.position for role in author.roles]) < admin_role_pos:
        return
    if author.id in invoker_map.get(recv_msg.channel.id, {}):
        return  # Allow only one message at a time per user per channel

    broadcast_msg = recv_msg.content[len(prefix):].strip()  # To strip-off prefix 
    online = sum(
        member.status != discord.Status.offline and not member.bot
        for member in recv_msg.guild.members
    )
    all_ = sum(not member.bot for member in recv_msg.guild.members)

    embed = discord.Embed(title="New Broadcast", color=0x000000)
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
    embed.set_footer(
        text="Please react with an appropriate action to continue"
    )
    if recv_msg.channel.id not in invoker_map:
        invoker_map[recv_msg.channel.id] = {}

    # Not using delete_after so that there's tighter coupling between message
    # deletion and invoker_map entry deletion
    await recv_msg.channel.send(embed=embed)
    msg = await recv_msg.channel.history().get(
        author__name=bot.user.display_name
    )
    invoker_map[recv_msg.channel.id][author.id] = {
        "menu_id": msg.id,
        "broadcast_content": broadcast_msg
    }

    for emoji in options.keys():
        await msg.add_reaction(emoji)

    print(invoker_map)
    print('------------------')
    await asyncio.sleep(60)
    # Following raises (harmless) exception for some reason
    try:
        # Delete entry on timeout
        del invoker_map[msg.channel.id][author.id]
        await msg.delete()
    except Exception as e:
        print(f'Warning: {e}')


async def handle_role_msg(recv_msg):
    if not recv_msg.content.startswith('@'):
        return
    role = discord.utils.get(recv_msg.guild.roles, name=recv_msg.content[1:])
    if role is None:
        return
    channel = recv_msg.channel
    if channel.id not in invoker_map:
        return
    if recv_msg.author.id not in invoker_map[channel.id]:
        return
    menu_msg = await channel.fetch_message(
        invoker_map[channel.id][recv_msg.author.id]["menu_id"]
    )
    role_rxn = discord.utils.get(menu_msg.reactions, emoji='\U0001F399')
    role_reactors = await role_rxn.users().flatten()
    if recv_msg.author not in role_reactors:
        return

    # Delete menu and broadcast if all checks pass
    await menu_msg.delete()
    await broadcast(
        role.members,
        invoker_map[channel.id][recv_msg.author.id]["broadcast_content"]
    )


async def broadcast(recipients, msg, as_embed=False, author=None):
    async def send_to(member):
        try:
            await member.send(msg)
        except discord.errors.Forbidden as e:
            print(e)
        except Exception as be:
            print(be)

    if as_embed:
        async def send_to(member):
            embed = discord.Embed(title="Broadcast Message", color=0xff26ec)
            embed.add_field(name="From", value=author.guild)
            embed.add_field(name="To", value=member.mention)
            embed.add_field(name=":mega: Message", value=msg)
            embed.set_author(name=f"{author}", icon_url=author.avatar_url)
            embed.set_thumbnail(url=author.guild.icon_url)
            embed.set_footer(
                text=f"© {author.guild} {datetime.datetime.now().year}"
            )
            try:
                await member.send(embed=embed)
            except discord.errors.Forbidden as e:
                print(e)
            except Exception as be:
                print(be)

    # for member in recipients:
    #     try:
    #         asyncio.ensure_future(send_to(member))
    #     except discord.errors.Forbidden as e:
    #         continue
    #     except Exception as be:
    #         print(be)
    online = [member for member in recipients if member.status != discord.Status.offline]
    offline = [member for member in recipients if member.status == discord.Status.offline]

    bufsize = int(len(recipients) ** 0.5)

    print(f"Broadcast started at: {datetime.datetime.now()}")

    await asyncio.gather(
        *[
            asyncio.gather(*[send_to(member) for member in online[i*bufsize:(i+1)*bufsize]])
            for i in range(len(recipients)//bufsize)
            ]
        )

    await asyncio.gather(
        *[
            asyncio.gather(*[send_to(member) for member in offline[i*bufsize:(i+1)*bufsize]])
            for i in range(len(recipients)//bufsize)
            ]
        ) 

    print(f"Broadcast ended at: {datetime.datetime.now()}")


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f'for broadcast requests | Use {prefix}<your message> to start broadcasting!')
    )

@bot.event
async def on_message(recv_msg):
    # Using this instead of @bot.command for whitespacing
    if recv_msg.content.startswith(prefix):
        await invoke_menu(recv_msg)
    elif recv_msg.content.startswith("@"):
        await handle_role_msg(recv_msg)
    

@bot.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel

    if channel.id not in invoker_map:
        return
    if user.id not in invoker_map[channel.id]:
        return
    if invoker_map[channel.id][user.id]["menu_id"] != reaction.message.id:
        return
    choice = f"{reaction}"
    if choice not in options:
        await reaction.message.edit(
            embed=reaction.message.embeds[0],
            content="Please choose a valid option"
        )
        return
    if options[choice].lower() == "to role":
        await reaction.message.channel.send(
            f"{user.mention} Please mention role as @role below",
            delete_after=60
        )
        return
    online = [
        member for member in reaction.message.guild.members
        if member.status != discord.Status.offline and not member.bot
    ]
    all_ = [
        member for member in reaction.message.guild.members if not member.bot
    ]
    as_embed = False
    if options[choice].lower().startswith("to online"):
        recipients = online
        if options[choice].lower() == "to online (embed)":
            as_embed = True
    elif options[choice].lower().startswith("to all"):
        recipients = all_
        if options[choice].lower() == "to all (embed)":
            as_embed = True
    else:  # It has to be the cancel option now
        await reaction.message.delete()
        return
    # Delete menu message and initiate broadcast
    await reaction.message.delete()
    await broadcast(
        recipients,
        invoker_map[channel.id][user.id]["broadcast_content"], as_embed,
        author=user
    )


if __name__ == '__main__':
    bot.run(credentials.TOKEN)
