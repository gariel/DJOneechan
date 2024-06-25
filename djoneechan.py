import sys
from typing import Iterable

import discord
from discord.ext import commands
from dotenv import dotenv_values

from base import Config, MediaItem, QueueItem
from downloader import Downloader
from manager import Manager
import time

    
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

managers: dict[str, Manager] = {}
async def _get_manager(ctx: commands.Context) -> Manager:
    voice_state = ctx.author.voice
    if voice_state is None:
        await ctx.send('Você precisa estar em um canal de voz para usar esse comando')
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
        # the bluetooth audio is ready to pair
        managers[id].search_add("https://www.youtube.com/watch?v=wCH3q2IsXVs", "")

    return managers[id]

# @bot.event
# async def on_message(message):
#     if message.author.bot or not message.content.startswith(config.Prefix):
#         return

#     message.content = message.content.lower()

#     await bot.process_commands(message)

@bot.command("queue", aliases=["q"])
async def cmd_queue(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    
    if not manager.queue:
        embedVar = discord.Embed(color=config.Color)
        embedVar.add_field(name='Nada pra ver aqui, circulando.', value="(◐ω◑ )")
        await ctx.send(embed=embedVar)
        return
    
    queue_list = []
    for item in manager.queue:
        queue_list.append(f"‣ {item.title} - por {item.author}")
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
        text = "🎵 Tocando agora:" if i == 0 else f"Página: {i + 1}"
        embedVar = discord.Embed(color=config.Color)
        embedVar.add_field(name=text, value=queue_str)
        await ctx.send(embed=embedVar)


@bot.command("play", aliases=["p", "add", "a"])
async def cmd_play(ctx: commands.Context, *args):
    print(ctx.author)
    if "willianzy" in str(ctx.author):
        await ctx.send("La vem musica de tchola do zy")
    
    manager = await _get_manager(ctx)
    if not manager:
        return

    query = ' '.join(args)
    queue_item = manager.search_add(query, str(ctx.author))
    if queue_item:
        await ctx.send(f'🎵 {queue_item.title} adicionada na queue ≧◡≦')
    else:
        await ctx.send(f'❌ Não consegui identificar a música, tente novamente ツ')
    
    manager.play(build_callback(ctx))


@bot.command("skip", aliases=["s", "next", "n"])
async def cmd_skip(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    await ctx.send('🎵 Pulando para a próxima música')
    manager.next_track(build_callback(ctx))


@bot.command("stop", aliases=["STOP"])
async def cmd_stop(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    await ctx.send('Queue limpa e player parado ʕ•ᴥ•ʔ')
    manager.clear_queue()
    manager.next_track(build_callback(ctx))


@bot.command("cafe", aliases=["CAFE", "coffee", "COFFEE", "☕"])
async def cmd_cafe(ctx: commands.Context, *_):
    await ctx.send('cafe ? 🐔☕')


@bot.command("ping", aliases=["PING"])
async def cmd_cafe(ctx: commands.Context, *_):
    await ctx.send('Pong 🏓')


@bot.command("clear", aliases=["clean", "empty"])
async def cmd_clear(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    await ctx.send('❌ Queue limpa')
    manager.clear_queue()


def build_callback(ctx: commands.Context):
    def callback(queue_item: QueueItem, media_item: MediaItem):
        async def task():
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name=media_item.title,
                    state=f"Adicionado por {queue_item.author}",
                )
            )
        bot.loop.create_task(task())
    return callback


def get_voice_client_from_channel_id(channel_id: int):
    for voice_client in bot.voice_clients:
        if voice_client.channel.id == channel_id:
            return voice_client


def main():
    return bot.run(config.Token)


if __name__ == '__main__':
    sys.exit(main())
