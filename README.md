# Virtua Chat OBS Anarchy

Twitch Chat integration for Virtua Gallery to swap between several OBS objects based on chat.

When a viewer posts in chat any of the following triggers, the corresponding OBS Source with corresponding name will have its opacity either set to visible or transparent.

| Chat message regex | OBS Source Name |
|--------------------|-----------------|
| "Cam 1"            | `[CAM 1]`       |
| "Cam 2"            | `[CAM 2]`       |
| "Cam 3"            | `[CAM 3]`       |

## Running

**Download the pre-built program from here: https://github.com/drfuzzyness/virtua-chat-obsanarchy/releases/latest**

Make a `.env` file where you want to run the code, based on the [`.env.example` file here](./.env.example) and fill it out with your secrets.

### Creating a Twitch Token

1. Enable 2FA on your Twitch account at https://www.twitch.tv/settings/security
1. Go to https://dev.twitch.tv/console and sign in.
2. Click **Register Your Application**
3. Set a name (ex: `virtua-chat-obsanarchy`)
4. Set the OAuth redirect URL to be this app's OAuth server `http://localhost:17563`
5. Set the category (ex: **Broadcaster Suite**)
6. Set the client type to **Confidential**
7. Prove that you exist
8. Click **Manage** on your new Application
9. Grab the **Client ID** as `SECRET_TWITCH_APP_ID`
10. Grab the **Client Secret** as `SECRET_TWITCH_APP_SECRET`

### Setting up OBS Settings

1. Don't install the old plugin ["OBS Websocket API"](https://github.com/obsproject/obs-websocket/releases) as it's built into OBS now and will cause conficts if you run the old installer
    - If you get errors about OBS Websockets when you start OBS, use **Help** / **Check File Integrity**
2. Open **OBS**. Go to **Tools** / **WebSocket Server Settings**
3. **Generate Password**
4. Press **Show Connect Info**
5. Grab the password from there as `SECRET_OBS_PASSWORD`
6. Grab the server port to put into `OBS_URL` in the format `ws://localhost:YOUR_PORT_HERE` (see [`.env.example`](./.env.example))

### Setting up your OBS Scenes

For each of your OBS scenes, you'll need to make three sources with the following _exact_ names.

- `[CAM 1]`
- `[CAM 2]`
- `[CAM 3]`

The name of the source is what allows the app to change the opacity to show and hide the source.

You'll also need to add the **Color Key** Filter to each source. Right click on a source, and choose **Filters**. In the bottom left of the window, click the **Plus** icon, and choose **Color Key**. You can leave all settings as default. This program will automatically change the opacity of that from `0` to `1` to deactivate or activate the source.

### First Run

1. Start the program, be ready for a browser window to open.

Windows:

```ps1
.\virtua-chat-obsanarchy.exe
```

All others:

```sh
./virtua-chat-obsanarchy --help
```

2. A browser tab will open to `https://www.twitch.tv/login?client_id=....`. Log into Twitch using your production Twitch account, and authorize yourself against your app.

You're good to go! The login credential is now saved to your user's Appdata folder and will be reused. After some time, the token will need to be refreshed, which will automatically cause a browser window to open.


## Development

1. Install Python [`^3.12`](https://www.python.org/downloads/release/python-3128/) from https://www.python.org/
2. Install `poetry@^2.0.1`  https://python-poetry.org/docs/#installing-with-the-official-installer
    - Follow the steps at the end of the installer's output to add `POETRY` to your `PATH`!
3. Clone this repository
4. Install project dependencies with `poetry install`

### Running

Copy the [`.env.example` file here](./.env.example) to `.env` and fill it out with your secrets.

#### Windows

```sh
poetry run py src/main.py
```

or

```sh
poetry env activate
py src/main.py
```

#### All others

```sh
poetry run python src/main.py
```

or

```sh
poetry env activate
python src/main.py
```

### Building to executable

```sh
poetry run pyinstaller --onefile --name virtua-chat-obsanarchy src/main.py
```