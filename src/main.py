"""
Main CLI entrypoint for this app
"""

import asyncio
import argparse

from dotenv import load_dotenv

import chat_obs
from EnvDefault import EnvDefault

if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="virtua-chat-obsanarchy",
        description="Twitch Chat integration for Virtua Gallery to swap between several OBS objects based on chat",
    )
    twitch_api = parser.add_argument_group(
        title="Twitch API", description="Twitch Chat API integration"
    )
    twitch_api.add_argument(
        "--twitch-app-id",
        action=EnvDefault,
        envvar="SECRET_TWITCH_APP_ID",
        help="Application ID as given to you when setting up your API integration (env: SECRET_TWITCH_APP_ID)",
        required=True,
        type=str,
    )
    twitch_api.add_argument(
        "--twitch-app-secret",
        action=EnvDefault,
        envvar="SECRET_TWITCH_APP_SECRET",
        help="Secret key given to you when setting up your API integration (env: SECRET_TWITCH_APP_SECRET)",
        required=True,
        type=str,
    )
    twitch_api.add_argument(
        "--twitch-channel",
        action=EnvDefault,
        envvar="TWITCH_CHANNEL",
        help="What Twitch Channel username should be joined? (env: TWITCH_CHANNEL)",
        required=True,
        type=str,
    )

    args = parser.parse_args()

    asyncio.run(
        chat_obs.main(
            {
                "secret_twitch_app_id": args.twitch_app_id,
                "secret_twitch_app_secret": args.twitch_app_secret,
                "twitch_channel": args.twitch_channel
            }
        )
    )
