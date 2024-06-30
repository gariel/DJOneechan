import os
import random
import sys
from typing import Iterable, Optional

import discord
from discord.ext import commands
from discord.errors import NotFound
from dotenv import dotenv_values

from base import Config
from downloader import Downloader
from manager import Manager


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


managers: dict[int, Manager] = {}
async def get_manager(ctx: commands.Context) -> Optional[Manager]:
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
        if not os.getenv("DISABLE_WELCOME_SOUND"):
            managers[id].search_add(welcome_sounds[random.randrange(0, len(welcome_sounds))], bot_author)
            managers[id].play(build_callback(ctx))

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
    await get_manager(ctx)
    await update_status(ctx)


@bot.command("queue", aliases=["q", "QUEUE", "Q"],
             help="Mostra a fila de músicas")
async def cmd_queue(ctx: commands.Context, *_):
    manager = await get_manager(ctx)
    if not manager:
        return
    
    if not manager.queue:
        embed = discord.Embed(color=config.Color)
        embed.add_field(name='Nada pra ver aqui, circulando.', value="(◐ω◑ )")
        await ctx.send(embed=embed)
        return

    queue_list = build_queue_list(manager)

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
        embed = discord.Embed(color=config.Color)
        embed.add_field(name="🎵 Nada tocando agora", value="")
        await ctx.send(embed=embed)
        return
    
    for i, queue_str in enumerate(split(queue_list)):
        text = "🎵 Tocando agora:" if i == 0 else ""
        embed = discord.Embed(color=config.Color)
        embed.add_field(name=text, value=queue_str)
        await ctx.send(embed=embed)

    await update_status(ctx)


@bot.command("play", aliases=["PLAY", "p", "P", "add", "ADD", "a", "A"], help="Adiciona uma música na fila de reprodução")
async def cmd_play(ctx: commands.Context, *args):
    if "willianzy" in str(ctx.author):
        await ctx.send("La vem musica de tchola do zy")
    
    manager = await get_manager(ctx)
    if not manager:
        return

    query = ' '.join(args)
    if query:
        queue_items = manager.search_add(query, str(ctx.author))

        if len(queue_items) == 1:
            await ctx.send(f'🎵 {queue_items[0].title} adicionada na queue ≧◡≦')
        elif len(queue_items) > 1:
            title_items = queue_items[:3]
            titles = ", ".join([qi.title for qi in title_items])
            await ctx.send(f'🎵 {titles} e mais {len(queue_items) - len(title_items)} adicionadas na queue ≧◡≦')
        else:
            await ctx.send(f'❌ Não consegui identificar a música, tente novamente ツ')

        if not manager.is_paused:
            manager.play(build_callback(ctx))

    else:
        manager.play(build_callback(ctx))

    await update_status(ctx)


@bot.command("insert", aliases=["INSERT", "inject", "INJECT", "i", "I", "playnext", "PLAYNEXT", "pn", "PN"],
             help="Adiciona uma música na fila de reprodução como próxima")
async def cmd_insert(ctx: commands.Context, *args):
    manager = await get_manager(ctx)
    if not manager:
        return
    
    query = ' '.join(args)
    queue_items = manager.search_add_next(query, str(ctx.author))

    if len(queue_items) == 1:
        await ctx.send(f'🎵 {queue_items[0].title} injetada como próxima da fila ヽ(゜∇゜)ノ')
    elif len(queue_items) > 1:
        title_items = queue_items[:3]
        titles = ", ".join([qi.title for qi in title_items])
        await ctx.send(f'🎵 {titles} e mais {len(queue_items) - len(title_items)} inseridas como próximas na queue ヽ(゜∇゜)ノ')
    else:
        await ctx.send(f'❌ Não consegui identificar a música, tente novamente ツ')

    manager.play(build_callback(ctx))
    await update_status(ctx)


@bot.command("shuffle", aliases=["SHUFFLE"], help="Randomiza a playlist atual")
async def cmd_shuffle(ctx: commands.Context, *args):
    manager = await get_manager(ctx)
    if not manager:
        return

    queue = manager.queue
    if queue:
        await ctx.send(f'Playlist randomizada ≧◡≦')
    else:
        await ctx.send(f'❌ Não consegui identificar a playlist, tente novamente ツ')

    manager.shuffle()
    await update_status(ctx)


@bot.command("skip", aliases=["SKIP", "next", "NEXT", "n", "N", "s", "S"],
             help="Pula a música atual ou x músicas")
async def cmd_skip(ctx: commands.Context, *args):
    manager = await get_manager(ctx)
    if not manager:
        return
    
    if not args or len(args) != 1:
        await ctx.send('🎵 Pulando para a próxima música')
        manager.next(build_callback(ctx))
    else:
        try:
            n = int(args[0])
        except Exception:
            await ctx.send(f'que que se falo? "{args[0]}" devia ser um numero')

        await ctx.send(f'🎵 Pulando {n} músicas')
        manager.next_n(n, build_callback(ctx))

    await update_status(ctx)


@bot.command("pause", aliases=["PAUSE"],
             help="Pausa a reprodução do BOT")
async def cmd_pause(ctx: commands.Context, *_):
    manager = await get_manager(ctx)
    if not manager:
        return

    await ctx.send('Pausando (>‘o’)>')
    manager.pause(build_callback(ctx))
    await update_status(ctx)


@bot.command("stop", aliases=["STOP"],
             help="Para a reprodução do BOT")
async def cmd_stop(ctx: commands.Context, *_):
    manager = await get_manager(ctx)
    if not manager:
        return

    await ctx.send('Queue limpa e player parado ʕ•ᴥ•ʔ')
    manager.clear_queue()
    manager.next(build_callback(ctx))
    await update_status(ctx)


@bot.command("clear", aliases=["CLEAR", "clean", "CLEAN", "empty", "EMPTY"],
             help="Limpa a fila de reprodução")
async def cmd_clear(ctx: commands.Context, *_):
    manager = await get_manager(ctx)
    if not manager:
        return

    await ctx.send('❌ Queue limpa')
    manager.clear_queue()
    await update_status(ctx)


@bot.command("cafe", aliases=["CAFE", "coffee", "COFFEE", "☕"],
             help="Faz um cafezinho")
async def cmd_cafe(ctx: commands.Context, *_):
    await ctx.send('cafe ? 🐔☕')
    await update_status(ctx)


@bot.command("ping", aliases=["PING"],
             help="Response test")
async def cmd_cafe(ctx: commands.Context, *_):
    await ctx.send('Pong 🏓')
    await update_status(ctx)


@bot.command("say", aliases=["SAY", "fala", "FALA", "fale", "FALE", "diz", "DIZ"],
             help="Diz alguma coisa no canal de voz por TTS")
async def cmd_say(ctx, *args):
    manager = await get_manager(ctx)
    if not manager:
        return

    message = " ".join(args)
    user_name = ctx.message.author.display_name
    complete_message = f'{user_name} disse "{message}"'
    manager.interruption(complete_message, build_callback(ctx))


@bot.event
async def on_voice_state_update(
        member: discord.member.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
    # disconects when everyone leaves
    if not before.channel:
        return
    
    members = [member for member in before.channel.members if member.id != bot.user.id]
    if not members:
        vc = get_voice_client_from_channel_id(before.channel.id)
        if vc:
            del managers[before.channel.guild.id]
            await vc.disconnect(force=True)


def sort_params(args, *types) -> list:
    mapping = {type(a): a for a in args}
    return [mapping[t] for t in types]


class Buttons(discord.ui.View):
    def __init__(self, manager, callback):
        super().__init__()
        self.manager = manager
        self.callback = callback

    @discord.ui.button(label="⏯️", style=discord.ButtonStyle.gray, custom_id="pause")
    async def pause_button(self, *args):
        await self.ok(args)
        if self.manager.is_paused:
            self.manager.play(self.callback)
        else:
            self.manager.pause(self.callback)
        self.callback()

    @discord.ui.button(label="🔀", style=discord.ButtonStyle.gray, custom_id="shuffle")
    async def shuffle_button(self, *args):
        await self.ok(args)
        self.manager.shuffle()
        self.callback()

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.gray, custom_id="next")
    async def next_button(self, *args):
        await self.ok(args)
        self.manager.next(self.callback)
        self.callback()

    async def ok(self, args):
        interaction, _ = sort_params(args, discord.Interaction, discord.ui.Button)
        try:
            await interaction.response.edit_message()
        except NotFound:
            pass


def build_queue_list(manager: Manager) -> list[str]:
    status = manager.is_paused and "⏸️" or "▶️"

    queue_list = []
    for i, item in enumerate(manager.queue):
        indicator = ""
        if i == 0:
            indicator = status
        queue_list.append(f"{indicator}‣ {i:02d} - **{item.title[:50]}** - por {item.author}")
    return queue_list


async def update_status(ctx: commands.Context):
    manager = await get_manager(ctx)
    status = manager.is_paused and "⏸️" or "▶️"

    next = build_queue_list(manager)[1:5]
    next_str = "\n".join(next)

    if manager.queue:
        queue_item = manager.queue[0]
        title = queue_item.title
        state = f"{status} - Adicionado por {queue_item.author}\n\n{next_str}"
        buttons = Buttons(manager, build_callback(ctx))
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=title,
                state=state,
            )
        )
    else:
        title = "Fila zerada. Adicione músicas com /play <nome/link da música>"
        state = "⏹️"
        buttons = None
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.unknown
            )
        )

    msgs = [msg async for msg in ctx.history() if msg.author.id == bot.user.id]
    for last in msgs:
        if last.author.id == bot.user.id and last.embeds and last.embeds[0].title == "Info":
            try:
                await last.delete()
            except NotFound:
                pass

    e = discord.Embed(color=config.Color, title="Info")
    e.add_field(name=title, value=state)
    await ctx.send(embed=e, view=buttons)


def build_callback(ctx: commands.Context):
    def callback():
        bot.loop.create_task(update_status(ctx))
    return callback


def get_voice_client_from_channel_id(channel_id: int) -> discord.VoiceProtocol:
    for voice_client in bot.voice_clients:
        if voice_client.channel.id == channel_id:
            return voice_client


def main():
    return bot.run(config.Token)


if __name__ == '__main__':
    sys.exit(main())
