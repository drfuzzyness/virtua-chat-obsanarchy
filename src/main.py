"""
Main CLI entrypoint for this app
"""

import asyncio
import argparse
import logging
import re
import sys

from dotenv import load_dotenv
import coloredlogs
import twitchAPI.chat

from chat_integration import ChatIntegration
from obs_enabledisable import ObsEnableDisable
from EnvDefault import EnvDefault

logger = logging.getLogger("virtua_chat_obsanarchy")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="virtua-chat-obsanarchy",
        description="Twitch Chat integration for Virtua Gallery"
        + "to swap between several OBS objects based on chat",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")
    parser.add_argument("--quiet", help="Disables debug logs", action="store_true")
    parser.add_argument(
        "--disable-colors",
        help="Disables colorizing the program logs.",
        action="store_true",
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

    args = parser.parse_args()

    log_level = logging.INFO if args.quiet else logging.DEBUG
    if args.disable_colors:
        logging.basicConfig(level=log_level)
    else:
        coloredlogs.install(
            level=log_level,
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        )

    # Mute some of the noisier modules
    for level_info in [
        "asyncio",
        "simpleobsws",
        "twitchAPI.twitch",
        "twitchAPI.chat",
        "twitchAPI.oauth",
    ]:
        logging.getLogger(level_info).setLevel(logging.INFO)

    for level_warn in [
        "aiohttp.access",
    ]:
        logging.getLogger(level_warn).setLevel(logging.WARN)

    object_names = ["[CAM 1]", "[CAM 2]", "[CAM 3]", "[CAM 4]"]

    obs_integration = ObsEnableDisable(
        {
            "obs_url": args.obs_url,
            "secret_obs_password": args.obs_password,
            "target_object_names": object_names,
        }
    )

    async def trigger_source(msg: twitchAPI.chat.ChatMessage, trigger_index: int):
        logger.info(
            '%s has triggered source %s with message: "%s"',
            msg.user.display_name,
            object_names[trigger_index],
            msg.text,
        )
        await obs_integration.activate_object(object_names[trigger_index])

    chat_integration = ChatIntegration(
        {
            "secret_twitch_app_id": args.twitch_app_id,
            "secret_twitch_app_secret": args.twitch_app_secret,
            "twitch_channel": args.twitch_channel,
        },
        [
            (
                re.compile("Cam 1", re.IGNORECASE),
                lambda msg: trigger_source(msg, 0),
            ),
            (
                re.compile("Cam 2", re.IGNORECASE),
                lambda msg: trigger_source(msg, 1),
            ),
            (
                re.compile("Cam 3", re.IGNORECASE),
                lambda msg: trigger_source(msg, 2),
            ),
            (
                re.compile("Cam 4", re.IGNORECASE),
                lambda msg: trigger_source(msg, 3),
            ),
        ],
    )

    logger.debug("Configuration valid, starting...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.gather(obs_integration.begin(), chat_integration.begin())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Quitting from KeyboardInterrupt...")
        # loop.create_task(chat_integration.close())
        exit_task = asyncio.gather(chat_integration.close(), obs_integration.close())
        loop.run_until_complete(exit_task)
        logger.info("...goodbye 😊")
        sys.exit(0)


if __name__ == "__main__":
    main()
