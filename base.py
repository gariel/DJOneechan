from dataclasses import dataclass


@dataclass
class Config:
    Token: str
    Prefix: str
    Color: int

    @staticmethod
    def convert_color(colorstr: str) -> int:
        try:
            return int(colorstr, 16)
        except ValueError:
            print('the BOT_COLOR in .env is not a valid hex color')
            print('using default color ff0000')
            return 0xff0000

    @staticmethod
    def create(env) -> "Config":
        return Config(
            Token=env.get("BOT_TOKEN"),
            Prefix=env.get("BOT_PREFIX", "."),
            Color=Config.convert_color(env.get("BOT_COLOR"))
    )


@dataclass
class QueueItem:
    title: str
    url: str
    author: str = ""
