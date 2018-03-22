import asyncio
import datetime
import json
import logging
import random
import statistics
import time
from collections import deque
from datetime import datetime
from functools import wraps

import aiohttp
import bs4
import gspread
import requests
import wikipedia
from bs4 import BeautifulSoup
from django.core.exceptions import FieldError

from discordbot.models import (DiscordPicture, DiscordSettings, DiscordUser,
                               Wisdom)

logger = logging.getLogger(__name__)
wisdom_history = deque([], maxlen=5)

def get_credentials():
    """Get credentials from file"""
    try:
        with open('discordbot/credentials.json', 'r', encoding='utf-8') as jsonPrivate:
            credentials = json.load(jsonPrivate)
            return credentials
            logger.debug('Credentials loaded')
    except Exception as e:
        logger.error(e)
        
def get_nickname_cache():
    """Get nickname dictionary from discord user model"""
    query_set = DiscordUser.objects.values_list('id', 'display_name')
    cached_nicknames = {x[0] : x[1] for x in query_set}
    return cached_nicknames

def get_random_entry(model):
    """Get random entry from given model

    Args:
        model (BaseModel): Django model with pid field
    
    Returns:
        random_entry: Random entry from given model with pid=0
    """
    try:
        random_entry = model.objects.filter(pid=0).order_by('?').first()
        model.objects.filter(id=random_entry.id).update(pid=1)
    except AttributeError:
        model.objects.all().update(pid=0)
        random_entry = model.objects.filter(pid=0).order_by('?').first()
        model.objects.filter(id=random_entry.id).update(pid=1)
    except FieldError as ex:
        logger.error(ex)
        return str(ex).split('.')[0]

    if model.__name__ is 'Wisdom':
        wisdom_history.append(random_entry)

    return random_entry


def update_display_names(servers):
    """Update display names for every user in bot.servers"""
    users = {}
    cache = get_nickname_cache()
    for server in servers:
        for member in server.members:
            users[member.id] = member.display_name

    for discord_id, name in users.items():
        if not discord_id in cache:
            DiscordUser.objects.create(id = discord_id, display_name = name)
        elif name != cache[discord_id]:
            u = DiscordUser.objects.filter(id=discord_id).update(display_name=name)
    
    DiscordSettings.objects.filter(key='cache_update').update(value=datetime.now())
    logger.info('HYPERLUL')

def refresh_wisdom_history():
    """Updates current lastwisdom deque if wisdom table changes

    Returns:
        str: Bot message
    """
    tempIDs = [x.id for x in wisdom_history]
    wisdom_history.clear()
    for item in Wisdom.objects.filter(id__in=tempIDs):
        wisdom_history.append(item)
    logger.info('monkaS')
    return "Wisdom history updated"

# move this crap to imgur_hb
def get_random_picture():
    """Gets random picture from imgur table and sets new pid based on picture's age"""
    random_pic = DiscordPicture.objects.filter(pid__lt=2).order_by('?').first()
    if random_pic:
        id = random_pic.id
        current_pid = random_pic.pid
        new_pid = current_pid + compare_timestamps(random_pic.date)
        DiscordPicture.objects.filter(id=random_pic.id).update(pid=new_pid)
        return random_pic.url
    else:
        DiscordPicture.objects.all().update(pid=0)
        return get_random_picture()

def botExceptionCatch(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(func.__name__ +  str(e))
            return str(e)
    return wrapper

def admin_command(func):
    """Checks if command executed by admin or bot's owner"""
    @wraps(func)
    async def decorated(*args, **kwargs):
        try:
            admin_list = DiscordUser.objects.filter(admin=1).values_list('id', flat=True)
            if args[0].message.author.id in admin_list:
                return await func(*args, **kwargs)
        except Exception as e:
            logger.error(e)
    return decorated

def mod_command(func):
    """Checks if command executed by mod"""
    @wraps(func)
    async def decorated(*args, **kwargs):
        try:
            mod_list = DiscordUser.objects.filter(mod_group=1).values_list('id', flat=True)
            if args[0].message.author.id in mod_list:
                return await func(*args, **kwargs)
        except Exception as e:
            logger.info()
            logger.error(e)
    return decorated

# monkaS
async def wisdom_info_formatter(cache):
    pyformat = '```py\n{}```'
    message = '{0:<4} : {1:^18} : {2:^35}\n'.format(
                'ID','Author','Wisdom Text')
    
    latest_wisdom = Wisdom.objects.latest('id')
    wisdom_count = Wisdom.objects.count()
    
    if len(wisdom_history) != 0:
        message += '\nLast wisdoms (Max limit: {0})\n'.format(wisdom_history.maxlen)
        for item in wisdom_history:
            author_name = check_author_name(item.author_id, cache)
            wisdom = item.text.replace('\n', '')
            if len(wisdom) > 35:
                wisdom = '{0:.32}...'.format(wisdom)
            message += '{0.id:<4} : {1:^18} : {2:35}\n'.format(item, author_name, wisdom)

    message += '\nLatest wisdom:\n{0.id:<4} : {1:^18} : {0.text:35}\n\nTotal wisdoms: {2}'.format(
                    latest_wisdom, check_author_name(latest_wisdom.author_id, cache), wisdom_count)
    return pyformat.format(message)

def check_author_name(id, cache):
    return cache[id] if id in cache else id

def compare_timestamps(timestamp):
    difference = time.time() - timestamp
    if difference > 16070400:
        return 3
    elif difference > 7776000:
        return 2
    else:
        return 1

async def ow_rank(id, playerBase):
    """OW rank checker"""
    if id in playerBase:
        blizzID = playerBase[id]
        link = 'https://playoverwatch.com/en-gb/career/pc/eu/' + blizzID
        async with aiohttp.get(link) as r:
            try:
                text = await r.text()
                soup = BeautifulSoup(text, 'html.parser')
                result = soup.find("div", {"class": "competitive-rank"}).text
            except:
                result = None
        return result
    else:
        result = "Can't find player in database"
    return result

    wikipedia.set_lang('ru')

def wiki(article):
    try:
        wikiresult = wikipedia.summary(article).split('\n')[0]
        wikilink = wikipedia.page(article).url
    except wikipedia.exceptions.DisambiguationError as e:
        wikiresult = str(str(e).split(': \n')[1].split('\n')).strip('[]')
        if len(wikiresult) >= 250:
            wikiresult = 'Слишком много результатов, попробуй запрос поточнее'
        wikilink = 'Слишком много результатов чтобы выдать ссылку, попробуй поточнее'
    except Exception as ex:
        wikiresult = str(ex)
        wikilink = str(ex)
    return wikiresult, wikilink


def wikibotlang(language):
    wronglang = False
    tempdict = {}
    try:
        if language.lower() in ('english', 'en', 'eng', 'английский'):
            language = 'en'
            tempdict['en'] = 'Английский'
        elif language.lower() in ('russian', 'ru', 'rus', 'русский'):
            language = 'ru'
            tempdict['ru'] = 'Русский'
        elif language.lower() in ('ukraininan', 'ua', 'ukr', 'uk', 'украинский'):
            language = 'uk'
            tempdict['uk'] = 'Украинский'
        elif language.lower() in ('greek', 'gr', 'el', 'греческий'):
            language = 'el'
            tempdict['el'] = 'Греческий'
        else:
            wronglang = True
            language = 'ru'
            tempdict['ru'] = 'Русский'
        if wronglang:
            wikilangerror = '`Доступные варианты языков - Английский, Русский, Украинский и Греческий (en,ru,uk,el)`'
            return wikilangerror
        else:
            wikipedia.set_lang(language)
            wikilangerror = '`Язык изменен на {}`'.format(tempdict[language])
            return wikilangerror
    except Exception as e:
        logger.error(str(e))
        wikilangerror = '`Не могу изменить язык на {}`'.format(language)
        return wikilangerror