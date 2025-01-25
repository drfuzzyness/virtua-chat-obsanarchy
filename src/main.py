"""
Main CLI entrypoint for this app
"""

import asyncio
import argparse

from dotenv import load_dotenv

from chat_integration import ChatIntegration
from obs_enabledisable import ObsEnableDisable
from EnvDefault import EnvDefault


async def main_loop(args: argparse.Namespace):
    """Starts services, then async blocks until done."""
    obs_integration = ObsEnableDisable(
        {
            "obs_url": args.obs_url,
            "secret_obs_password": args.obs_password,
            "target_object_names": ["[CAM 1]", "[CAM 2]", "[CAM 3]", "[CAM 4]"],
        }
    )

    chat_integration = ChatIntegration(
        {
            "secret_twitch_app_id": args.twitch_app_id,
            "secret_twitch_app_secret": args.twitch_app_secret,
            "twitch_channel": args.twitch_channel,
        },
        [],
    )
    await obs_integration.begin()
    await chat_integration.main()


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
        help="Application ID as given to you when setting up your API integration "
        + "(env: SECRET_TWITCH_APP_ID)",
        required=True,
        type=str,
    )
    twitch_api.add_argument(
        "--twitch-app-secret",
        action=EnvDefault,
        envvar="SECRET_TWITCH_APP_SECRET",
        help="Secret key given to you when setting up your API integration "
        + "(env: SECRET_TWITCH_APP_SECRET)",
        required=True,
        type=str,
    )
    twitch_api.add_argument(
        "--twitch-channel",
        action=EnvDefault,
        envvar="TWITCH_CHANNEL",
        help="What Twitch Channel username should be joined? "
        + "(env: TWITCH_CHANNEL)",
        required=True,
        type=str,
    )

    obs_ws = parser.add_argument_group(
        title="OBS Websocket API", description="OBS Websocket connection details"
    )
    obs_ws.add_argument(
        "--obs-url",
        action=EnvDefault,
        envvar="OBS_URL",
        help="What is the websocket URL of your OBS instance? " + "(env: OBS_URL)",
        default="ws://localhost:4444",
        type=str,
        required=False,
    )
    obs_ws.add_argument(
        "--obs-password",
        action=EnvDefault,
        envvar="SECRET_OBS_PASSWORD",
        help="What is the Websocket API password for OBS? "
        + "(env: SECRET_OBS_PASSWORD)",
        type=str,
        required=True,
    )
    asyncio.run(main_loop(parser.parse_args()))
