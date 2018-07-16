"""COG FOR ADMIN COMMANDS"""

import inspect
import logging
import aiohttp

from discord.ext import commands

from discordbot.cogs.utils.checks import admin_command

logger = logging.getLogger('botLogger.admin')

class Admin(object):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command(pass_context=True, hidden=True)
    @admin_command
    async def change_avatar(self, ctx, url):
        """Sets Bot's avatar"""
        try:
            async with self.session.get(url) as r:
                data = await r.read()
            await self.bot.edit_profile(avatar=data)
            await self.bot.say("Done.")
            logger.debug("changed avatar")
        except Exception as e:
            await self.bot.say("Error, check your console or logs for "
                            "more information.")
            logger.exception(e)

    @commands.command(pass_context=True, hidden=True)
    @admin_command
    async def change_nickname(self, ctx, nickname: str):
        """Sets Bot's nickname"""
        try:
            await self.bot.edit_profile(username=nickname)
            await self.bot.say("Done.")
            logger.debug("changed nickname")
        except Exception as e:
            await self.bot.say("Error, check your console or logs for "
                            "more information.")
            logger.exception(e)

    @commands.command(pass_context=True, hidden=True)
    @admin_command
    async def load(self, ctx, extension_name: str):
        """Loads an extension."""
        try:
            if not "cogs." in extension_name:
                extension_name = "cogs." + extension_name
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as ex:
            await self.bot.say("```py\n{}: {}\n```".format(type(ex).__name__, str(ex)))
            return
        await self.bot.say("{} loaded.".format(extension_name))

    @commands.command(pass_context=True, hidden=True)
    @admin_command
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""
        if not "cogs." in extension_name:
            extension_name = "cogs." + extension_name
        self.bot.unload_extension(extension_name)
        await self.bot.say("{} unloaded.".format(extension_name))

    @commands.command(pass_context=True, hidden=True)
    @admin_command
    async def debug(self, ctx, *, code: str):
        """Evaluates code."""
        code = code.strip('` `')
        python = '```py\n{}\n```'
        try:
            result = eval(code)
            if inspect.isawaitable(result):
                result = await result
        except Exception as ex:
            await self.bot.say(python.format(type(ex).__name__ + ': ' + str(ex)))
            result = None
            return
        await self.bot.say(python.format(result))

def setup(bot):
    bot.add_cog(Admin(bot))