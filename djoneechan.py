import sys
from typing import Iterable

import discord
from discord.ext import commands
from dotenv import dotenv_values

from base import Config
from downloader import Downloader
from manager import Manager

    
config = Config.create(dotenv_values(".env"))


bot = commands.Bot(
    command_prefix=config.Prefix,
    intents=discord.Intents(
        voice_states=True,
        guilds=True,
        guild_messages=True,
        message_content=True
    )
)


managers = {}
async def _get_manager(ctx: commands.Context) -> Manager:
    voice_state = ctx.author.voice
    if voice_state is None:
        await ctx.send('you have to be in a voice channel to use this command')
        return None

    # member_ids = [member.id for member in ctx.author.voice.channel.members]
    # if bot.user.id not in member_ids: # TODO and ctx.guild.id in queues.keys():
    #     await ctx.send('you have to be in the same voice channel as the bot to use this command')
    #     return None

    global managers
    id = ctx.guild.id
    if id not in managers:
        voice_state = ctx.author.voice
        vc = await voice_state.channel.connect()
        managers[id] = Manager(Downloader(), vc)
    return managers[id]


@bot.command("queue", aliases=["q"])
async def cmd_queue(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    
    if not manager.queue:
        embedVar = discord.Embed(color=config.Color)
        embedVar.add_field(name='Nothing playing.', value="(◐ω◑ )")
        await ctx.send(embed=embedVar)
        return
    
    queue_list = []
    for item in manager.queue:
        queue_list.append(f"‣ {item.title}")
        if item.title != item.medias[0].title:
            for i, media in enumerate(item.medias):
                queue_list.append(f"    {i+1:03d} - {media.title}")
    
    def split(queue_list: list) -> Iterable[str]:
        queue_str = ""
        for qi in queue_list:
            new_str = f"{queue_str}\n{qi}"
            if len(new_str) > 1024:
                yield queue_str
                queue_str = qi
            else:
                queue_str = new_str

        if queue_str:
            yield queue_str
    
    for i, queue_str in enumerate(split(queue_list)):
        text = "Now playing:" if i == 0 else f"Page: {i + 1}"
        embedVar = discord.Embed(color=config.Color)
        embedVar.add_field(name=text, value=queue_str)
        await ctx.send(embed=embedVar)


@bot.command("play", aliases=["p", "add", "a"])
async def cmd_play(ctx: commands.Context, *args):
    manager = await _get_manager(ctx)
    if not manager:
        return

    query = ' '.join(args)
    queue_item = manager.search_add(query)
    if queue_item:
        await ctx.send(f'added {queue_item.title} to the kawaii queuee ≧◡≦')
    else:
        await ctx.send(f'onechan was not able to add the music ツ')
    
    manager.play(buils_log_music_callback(ctx))


@bot.command("skip", aliases=["s", "next", "n"])
async def cmd_skip(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    await ctx.send('skipping')
    manager.next_track(buils_log_music_callback(ctx))


@bot.command("clear", aliases=["clean", "empty"])
async def cmd_clear(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    await ctx.send('cleaning queue')
    manager.clear_queue()


def buils_log_music_callback(ctx: commands.Context):
    def callback(title):
        bot.loop.create_task(ctx.send(title))
    return callback


def get_voice_client_from_channel_id(channel_id: int):
    for voice_client in bot.voice_clients:
        if voice_client.channel.id == channel_id:
            return voice_client


def main():
    return bot.run(config.Token)


if __name__ == '__main__':
    sys.exit(main())
