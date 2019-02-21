import argparse
import shlex
from typing import Dict, Any

from redbot.core.commands import Converter, Context, BadArgument
from redbot.core.i18n import Translator

_ = Translator("BanSync", __file__)


class NoExitParser(argparse.ArgumentParser):
    """By default, an error on this calls sys.exit"""

    def error(self, message):
        raise BadArgument() from None


class SyndicatedConverter(Converter):
    """
    Parser based converter.

    Takes sources, and either
        destinations, a flag to automatically determine destinations, or both
    """

    async def convert(self, ctx: Context, argument: str) -> dict:

        parser = NoExitParser(description="Syndicated Ban Syntax", add_help=False)
        parser.add_argument("--sources", nargs="*", dest="sources", default=[])
        parser.add_argument("--destinations", nargs="*", dest="dests", default=[])
        parser.add_argument(
            "--auto-destinations", action="store_true", default=False, dest="auto"
        )

        vals = parser.parse_args(shlex.split(argument))
        ret: Dict[str, Any] = {}

        guilds = set(ctx.bot.guilds)

        ret["sources"] = set(filter(lambda g: str(g.id) in vals.sources, guilds))
        if not ret["sources"]:
            raise BadArgument(_("I need at least 1 source.")) from None

        if vals.auto:
            ret["dests"] = guilds - ret["sources"]
            ret["auto"] = True
        elif vals.dests:
            ret["dests"] = set()
            for guild in guilds:
                to_comp = str(guild.id)
                if to_comp in vals.dests and to_comp not in ret["sources"]:
                    ret["dests"].add(guild)
        else:
            raise BadArgument(
                _(
                    "I need either at least one destination, "
                    " to be told to automatically determine destinations, "
                    "or a combination of both to add extra destinations beyond the automatic."
                )
            ) from None
        ret["usr"] = ctx.author
        return ret
