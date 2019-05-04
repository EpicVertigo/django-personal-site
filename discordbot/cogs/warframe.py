"""
Cog for checking Warframe alerts
"""

import asyncio
import logging

import discord
from discord.errors import InvalidArgument
from discord.ext import commands
from discord.utils import get as get_user
from django.db.models import Q

from discordbot.models import DiscordUser, WFAlert

logger = logging.getLogger("botLogger.warframe")


class Warframe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.watchdog = self.bot.loop.create_task(
            self.warframe_alert_watchdog())
        self.RESOURCES = {
            'Nitain Extract (Resource)': 'nitain_extract',
            'Orokin Cell (Resource)': 'orokin_cell',
            'Orokin Cell Resource': 'orokin_cell',
            'Orokin Reactor (Blueprint)': 'orokin_reactor_bp',
            'Orokin Reactor (Item)': 'orokin_reactor_bp',
            'Orokin Catalyst Blueprint': 'orokin_catalyst_bp',
            'Orokin Catalyst (Blueprint)': 'orokin_catalyst_bp',
            'Orokin Catalyst (Item)': 'orokin_catalyst_bp',
            'Tellurium (Resource)': 'tellurium',
            'Forma Blueprint': 'forma_bp',
            'Forma (Item)': 'forma_bp',
            'Exilus Adapter Blueprint': 'exilus_ap',
            'Exilus Adapter (Blueprint)': 'exilus_ap',
            'Exilus Adapter': 'exilus_ap',
            'Exilus Adaptor': 'exilus_ap',
            'Exilus Adaptor (Item)': 'exilus_ap',
            'Exilus Adapter (Item)': 'exilus_ap',
            'kavat': 'kavat',
            '5x Kavat Genetic Code (Resource)': 'kavat',
            '10x Kavat Genetic Code (Resource)': 'kavat',
        }

    def cog_unload(self):
        if self.watchdog:
            self.watchdog.cancel()

    async def warframe_alert_watchdog(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            new_alerts = WFAlert.objects.filter(announced=False)
            for alert in new_alerts:
                if alert.keywords:
                    keywords = alert.keywords.split(',')
                    matches = [self.RESOURCES[k]
                               for k in keywords if k in self.RESOURCES]
                    if matches:
                        if len(matches) == 2:
                            subscribers = DiscordUser.objects.select_related().filter(
                                Q(**{f'wf_settings__{matches[0]}': True}) |
                                Q(**{f'wf_settings__{matches[1]}': True}))
                        else:
                            subscribers = DiscordUser.objects.select_related().filter(
                                **{f'wf_settings__{matches[0]}': True})
                        for sub in subscribers:
                            try:
                                user = get_user(
                                    self.bot.get_all_members(), id=sub.id)
                                if user:
                                    await user.send(embed=self.create_embed(alert))
                                else:
                                    logger.error(
                                        "Can't find %s in get_all_members(). User unsubbed", sub)
                                    self._unsub_user(sub)
                            except InvalidArgument:
                                pass
                alert.announced = True
                alert.save()
            await asyncio.sleep(60)

    def create_embed(self, alert):
        embed = discord.Embed(
            title="**Warframe Alert**",
            colour=discord.Colour(0xff0074),
            description=f"{alert.content}\n\n[Unsubscribe](https://epicvertigo.xyz/profile)")
        embed.set_thumbnail(url="https://i.imgur.com/ZvDNumd.png")
        embed.set_footer(text=f"WFAlert ID: {alert.id}")
        return embed

    def _unsub_user(self, user):
        """Set's user settings to Default"""
        settings = user.wf_settings
        fields = [x.name for x in settings._meta.fields if x.name != 'id']
        for field in fields:
            setattr(settings, field, False)
        settings.save()


def setup(bot):
    bot.add_cog(Warframe(bot))
