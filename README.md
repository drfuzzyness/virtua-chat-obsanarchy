# Virtua Chat OBS Anarchy

Twitch Chat integration for Virtua Gallery to swap between several OBS objects based on chat

## Running

For now, [run steps in Development](#development) first.

### Windows

```sh
poetry run py src/main.py
```

### All others

```sh
poetry run python src/main.py
```

## Development

1. Install Python [`^3.12`](https://www.python.org/downloads/release/python-3128/) from https://www.python.org/
2. Install `poetry` https://python-poetry.org/docs/#installing-with-the-official-installer
3. Clone this repository
4. Install project dependencies with `poetry install`

### Building to executable

```sh
poetry run pyinstaller --onefile --name virtua-chat-obsanarchy src/main.py
```