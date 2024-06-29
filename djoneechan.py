import sys
from typing import Iterable

import discord
from discord.ext import commands
from dotenv import dotenv_values

from base import Config, MediaItem, QueueItem
from downloader import Downloader
from manager import Manager
import random


config = Config.create(dotenv_values(".env"))
bot_author = "<bot>"
bot = commands.Bot(
    command_prefix=config.Prefix,
    intents=discord.Intents(
        voice_states=True,
        guilds=True,
        guild_messages=True,
        message_content=True
    )
)


welcome_sounds = [
    "https://www.youtube.com/watch?v=AUU_YHWCRWQ", # Mourão Bom Dia
    "https://www.youtube.com/watch?v=wCH3q2IsXVs", # The Bluetooth Device Is Ready To Pair
    "https://www.youtube.com/watch?v=9MekjuKFtJo", # boraaa acorda fdp
    "https://www.youtube.com/watch?v=aQyk2LG3KQI", # Você É Um Filho Da Puta He-Man
    "https://www.youtube.com/watch?v=N9777WExvCc", # Among Us Impostor
    "https://www.youtube.com/watch?v=0IAr0HhOVZo", # Samsung
    "https://www.youtube.com/watch?v=0VtPgIX_Dbk", # It's Time to D-D-D-D DUEL!
    "https://www.youtube.com/watch?v=I88S3jUeKkE", # Jesus Christ its jason bourne
    "https://www.youtube.com/watch?v=0ynT_2DDBZg", # SOMEBODY TOUCHA MY SPAGHET
    "https://www.youtube.com/watch?v=MUL5w91dzbo", # Goofy Yell
    "https://www.youtube.com/watch?v=AtbMnixO2nc", # Tourettes Guy hits his head
    "https://www.youtube.com/watch?v=UINZ8oRDIkU", # Rapaz é o seguinte, cambio desligo
]


managers: dict[str, Manager] = {}
async def _get_manager(ctx: commands.Context) -> Manager:
    global managers
    id = ctx.guild.id
    voice_state = ctx.author.voice
    if voice_state is None:
        await ctx.send('Você precisa estar em um canal de voz para usar esse comando')
        return None

    member_ids = [member.id for member in ctx.author.voice.channel.members]
    if bot.user.id not in member_ids and id in managers:
        await ctx.send('Você precisa estar no mesmo canal de voz para usar esse comando')
        return None

    if id not in managers:
        voice_state = ctx.author.voice
        vc = await voice_state.channel.connect()
        managers[id] = Manager(Downloader(), vc)
        # welcome sound
        managers[id].search_add(welcome_sounds[random.randrange(0, len(welcome_sounds))], bot_author)
        managers[id].play(callback)

    return managers[id]


@bot.command("disconnect", aliases=["leave", "DISCONNECT", "LEAVE"], help="Desconecta do canal de voz")
async def cmd_disconnect(ctx: commands.Context, *_):
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
        if ctx.guild.id in managers:
            del managers[ctx.guild.id]
    else:
        await ctx.send("I'm not connected to any voice channel.")


@bot.command("connect", aliases=["join", "CONNECT", "JOIN"], help="Conecta ao canal de voz")
async def cmd_connect(ctx: commands.Context, *_):
    await _get_manager(ctx)
    

@bot.command("queue", aliases=["q", "QUEUE", "Q"],
             help="Mostra a fila de músicas")
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
        if item.author == bot_author:
            continue

        queue_list.append(f"‣ **{item.title}** - por {item.author}")
        if item.title != item.medias[0].title:
            for i, media in enumerate(item.medias):
                queue_list.append(f" {i+1:02d} - **{media.title[:50]}**")
    
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
    
    if not queue_list:
        embedVar = discord.Embed(color=config.Color)
        embedVar.add_field(name="🎵 Nada tocando agora", value="")
        await ctx.send(embed=embedVar)
        return
    
    for i, queue_str in enumerate(split(queue_list)):
        text = "🎵 Tocando agora:" if i == 0 else ""
        embedVar = discord.Embed(color=config.Color)
        embedVar.add_field(name=text, value=queue_str)
        await ctx.send(embed=embedVar)


@bot.command("play", aliases=["PLAY", "p", "P", "add", "ADD", "a", "A"], help="Adiciona uma música na fila de reprodução")
async def cmd_play(ctx: commands.Context, *args):
    print(ctx.author)
    if "willianzy" in str(ctx.author):
        await ctx.send("La vem musica de tchola do zy")  # Changed from ctx.reply to ctx.send
    
    manager = await _get_manager(ctx)
    if not manager:
        return

    query = ' '.join(args)
    queue_item = manager.search_add(query, str(ctx.author))
    if queue_item:
        await ctx.send(f'🎵 {queue_item.title} adicionada na queue ≧◡≦')  # Changed from ctx.reply to ctx.send
    else:
        await ctx.send(f'❌ Não consegui identificar a música, tente novamente ツ')  # Changed from ctx.reply to ctx.send
    
    manager.play(callback)


@bot.command("shuffle", aliases=["SHUFFLE"], help="Randomiza a playlist atual")
async def cmd_shuffle(ctx: commands.Context, *args):
    manager = await _get_manager(ctx)
    if not manager:
        return

    queue = manager.queue
    if queue:
        await ctx.send(f'Playlist randomizada ≧◡≦')
    else:
        await ctx.send(f'❌ Não consegui identificar a playlist, tente novamente ツ')
    
    manager.shuffle(callback)


@bot.command("insert", aliases=["INSERT", "inject", "INJECT", "i", "I", "playnext", "PLAYNEXT", "pn", "PN"],
             help="Adiciona uma música na fila de reprodução como próxima")
async def cmd_insert(ctx: commands.Context, *args):
    manager = await _get_manager(ctx)
    if not manager:
        return
    
    query = ' '.join(args)
    queue_item = manager.search_add_next(query, str(ctx.author))
    if queue_item:
        await ctx.send(f'🎵 {queue_item.title} injetada como próxima da fila ヽ(゜∇゜)ノ')
    else:
        await ctx.send(f'❌ Não consegui identificar a música, tente novamente ツ')
    
    manager.play(callback)


@bot.command("skip", aliases=["SKIP", "next", "NEXT", "n", "N", "s", "S"],
             help="Pula a música atual ou x músicas")
async def cmd_skip(ctx: commands.Context, *args):
    manager = await _get_manager(ctx)
    if not manager:
        return
    
    if not args or len(args) != 1:
        await ctx.send('🎵 Pulando para a próxima música')
        manager.next_media(callback)
    else:
        try:
            n = int(args[0])
        except Exception:
            await ctx.send(f'que que se falo? "{args[0]}" devia ser um numero')

        await ctx.send(f'🎵 Pulando {n} músicas')
        manager.next_n_medias(n, callback)


@bot.command("skipplaylist", aliases=["SKIPPLAYLIST", "sp", "SP"],
             help="Pula a playlist atual")
async def cmd_skip_playlist(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    await ctx.send('🎵 Pulando o item atual')
    manager.next_item(callback)


@bot.command("stop", aliases=["STOP"],
             help="Para a reprodução do BOT")
async def cmd_stop(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    await ctx.send('Queue limpa e player parado ʕ•ᴥ•ʔ')
    manager.clear_queue()
    manager.next_item(callback)


@bot.command("clear", aliases=["CLEAR", "clean", "CLEAN", "empty", "EMPTY"],
             help="Limpa a fila de reprodução")
async def cmd_clear(ctx: commands.Context, *_):
    manager = await _get_manager(ctx)
    if not manager:
        return
    await ctx.send('❌ Queue limpa')
    manager.clear_queue()

@bot.command("cafe", aliases=["CAFE", "coffee", "COFFEE", "☕"],
             help="Faz um cafezinho")
async def cmd_cafe(ctx: commands.Context, *_):
    await ctx.send('cafe ? 🐔☕')


@bot.command("ping", aliases=["PING"],
             help="Response test")
async def cmd_cafe(ctx: commands.Context, *_):
    await ctx.send('Pong 🏓')


@bot.event
async def on_voice_state_update(member: discord.member.Member, before: discord.VoiceState, after: discord.VoiceState):
    # disconects when everyone leaves
    if not before.channel:
        return
    
    members = [member for member in before.channel.members if member.id != bot.user.id]
    if not members:
        vc = get_voice_client_from_channel_id(before.channel.id)
        if vc:
            del managers[before.channel.guild.id]
            await vc.disconnect()


def callback(queue_item: QueueItem, media_item: MediaItem):
    async def task(has_music: bool):
        if has_music:
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name=media_item.title,
                    state=f"Adicionado por {queue_item.author}",
                )
            )
        else:
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.unknown
                )
            )

    has_music = queue_item and queue_item.author != bot_author
    bot.loop.create_task(task(has_music))


def get_voice_client_from_channel_id(channel_id: int) -> discord.VoiceProtocol:
    for voice_client in bot.voice_clients:
        if voice_client.channel.id == channel_id:
            return voice_client


def main():
    return bot.run(config.Token)


if __name__ == '__main__':
    sys.exit(main())