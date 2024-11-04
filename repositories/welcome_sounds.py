from typing import Optional

from pymongo.synchronous.database import Database

from models.welcome_sound import WelcomeSound
from repositories import BaseRepository, with_default

default_welcome_sounds = [
    WelcomeSound(url=url, title=title, author="<default>")
    for url, title in {
        "https://www.youtube.com/watch?v=AUU_YHWCRWQ": "Mourão Bom Dia",
        "https://www.youtube.com/watch?v=wCH3q2IsXVs": "The Bluetooth Device Is Ready To Pair",
        "https://www.youtube.com/watch?v=9MekjuKFtJo": "boraaa acorda fdp",
        "https://www.youtube.com/watch?v=aQyk2LG3KQI": "Você É Um Filho Da Puta He-Man",
        "https://www.youtube.com/watch?v=N9777WExvCc": "Among Us Impostor",
        "https://www.youtube.com/watch?v=0IAr0HhOVZo": "Samsung",
        "https://www.youtube.com/watch?v=0VtPgIX_Dbk": "Its Time to D-D-D-D DUEL!",
        "https://www.youtube.com/watch?v=I88S3jUeKkE": "Jesus Christ its jason bourne",
        "https://www.youtube.com/watch?v=0ynT_2DDBZg": "SOMEBODY TOUCHA MY SPAGHET",
        "https://www.youtube.com/watch?v=MUL5w91dzbo": "Goofy Yell",
        "https://www.youtube.com/watch?v=AtbMnixO2nc": "Tourettes Guy hits his head",
        "https://www.youtube.com/watch?v=UINZ8oRDIkU": "Rapaz é o seguinte, cambio desligo",
        "https://www.youtube.com/watch?v=opBFaCS_PV4": "Peido",
        "https://www.youtube.com/watch?v=ABfj2JDEw9Q": "Kaguya ara ara",
    }.items()
]


class WelcomeSoundsRepository(BaseRepository):
    COLLECTION_NAME = "welcome_sounds"

    def __init__(self, client: Optional[Database]):
        super().__init__(client)
        if self._is_valid:
            first_time = self.COLLECTION_NAME not in client.list_collection_names()
            self._collection = client[self.COLLECTION_NAME]
            if first_time:
                self._collection.insert_many(
                    self._convert(dws)
                    for dws in default_welcome_sounds
                )

    @with_default(default_welcome_sounds)
    def get_all(self) -> list[WelcomeSound]:
        return self._unconvert_n(WelcomeSound, list(self._collection.find()))

    @with_default([d.url for d in default_welcome_sounds])
    def get_all_urls(self) -> list[str]:
        return [
            r["url"]
            for r in self._collection.find({}, {"url": 1, "_id": 0})
        ]
