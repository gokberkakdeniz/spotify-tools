#!/usr/bin/env python3

import argparse
import sys

from plugins.control import Control
from plugins.info import Info


class UnbufferedOutput(object):
    """
        Unbuffered print

        Original: https://stackoverflow.com/a/107717
    """

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
        Hides metavar the line after "list of main commands:"

        Original: https://stackoverflow.com/a/13429281
    """

    def _format_action(self, action):
        parts = super()._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


class SpotifyTools:
    def __init__(self):
        parser = argparse.ArgumentParser(
            prog="spotifyctl",
            formatter_class=SubcommandHelpFormatter
        )
        parser._positionals.title = "list of main commands"
        subparsers = parser.add_subparsers(
            title="plugins",
            dest="plugin"
        )

        self._parser = parser
        self._subparsers = subparsers
        self._plugins = []
        self._args = None

    def add_plugin(self, plugin):
        plugin_instance = plugin(self._subparsers)
        self._plugins.append(plugin_instance)

    def launch(self):
        if self._args is not None:
            raise Exception("Application is already launched!")

        if len(self._plugins) == 0:
            print("error: no plugin found!")
            exit(1)

        self._args = self._parser.parse_args()

        if self._args.plugin is None:
            self._parser.print_usage()
        else:
            for plugin in self._plugins:
                if self._parser.prog + " " + self._args.plugin == plugin._parser.prog:
                    plugin.run(self._args)
                    break

        return self._args


if __name__ == "__main__":
    sys.stdout = UnbufferedOutput(sys.stdout)
    app = SpotifyTools()
    app.add_plugin(Info)
    app.add_plugin(Control)
    args = app.launch()
