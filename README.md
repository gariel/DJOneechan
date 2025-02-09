
# DJ Oneechan

## Preparations

- Create a virtual env
``` bash
python3 -m venv .venv
```
- Activate the virtual env
``` bash
# Activate in linux/mac
source .venv/bin/activate
# Activate on windows
.venv\Scripts\activate
```
- Restore the dependencies
``` bash
pip install -r requirements.txt
```

## Running

- You should have the virtual env active
- Create a bot in Discord Dev Panel
- Set the `.env` file using the token from Discord following the `.env_sample`
- Set other configs
- You can set the mongoDB credentials for statistics
- Run directly with python:
```bash
python djoneechan.py
```

## Tests

- You should have the virtual env active 

``` bash
pytest tests
```