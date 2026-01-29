


import json
from downloader import Downloader

downloader = Downloader("")
url = downloader.get_media_url("apt")
print(json.dumps(url))
