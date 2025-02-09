from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote_plus

from utils import safe


@dataclass
class DBConfig:
    Host: str
    Port: int
    Database: str
    Username: Optional[str]
    Password: Optional[str]

    @property
    def is_valid(self) -> bool:
        return bool(self.Host and self.Port)

    @property
    def is_authenticated(self) -> bool:
        return bool(self.Username)

    @property
    def connection_string(self) -> str:
        cs = "mongodb://%(Host)s:%(Port)s/admin"
        if self.is_authenticated:
            cs = "mongodb://%(Username)s:%(Password)s@%(Host)s:%(Port)s/admin"

        return cs % {
            k: quote_plus(str(v))
            for k, v in vars(self).items()
        }


@dataclass
class Config:
    Token: str
    Prefix: str
    Color: int
    CookieFile: str
    DB: DBConfig
    EnableRunAdvanced: bool

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
            Color=Config.convert_color(env.get("BOT_COLOR")),
            CookieFile=env.get("BOT_COOKIE_FILE"),
            EnableRunAdvanced=env.get("BOT_ENABLE_RUN_ADVANCED_COMMANDS").lower() == "true",
            DB=DBConfig(
                Host=env.get("BOT_DB_HOST"),
                Port=safe(int, env.get("BOT_DB_PORT"), default=0),
                Username=env.get("BOT_DB_USER"),
                Password=env.get("BOT_DB_PASS"),
                Database=env.get("BOT_DB_DATABASE"),
            ),
        )
