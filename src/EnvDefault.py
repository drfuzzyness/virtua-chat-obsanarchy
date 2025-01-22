"""Stolen from https://stackoverflow.com/a/10551190
"""

import argparse
import os


class EnvDefault(argparse.Action):
    """
    Example:
        >>> parser.add_argument(
            "-u", "--url", action=EnvDefault, envvar='URL',
            help="Specify the URL to process (can also be specified using URL environment variable)")
    """

    def __init__(self, envvar, required=True, default=None, **kwargs):
        if envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super().__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
