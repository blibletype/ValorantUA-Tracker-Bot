import requests
import re
import sqlite3
import asyncio
import datetime
from nextcord.ext import commands, tasks
from constants import *

class RegisterUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} started')
        db = sqlite3.connect('Users.db')
        sql = db.cursor()
        sql.execute('CREATE TABLE IF NOT EXISTS users(' 
        + 'discord_id TEXT, ' 
        + 'discord_name TEXT, '
        + 'valorant_name TEXT, '
        + 'valorant_tag TEXT, '
        + 'current_tier_patched TEXT, '
        + 'elo TEXT, '
        + 'puuid TEXT, '
        + 'region TEXT, '
        + 'account_level TEXT, '
        + 'image_large_url TEXT, '
        + 'image_wide_url TEXT, '
        + 'image_small_url TEXT, '
        + 'updated TEXT)')
        db.commit()

    @commands.command()
    async def reg(self, ctx, *, arg):
        if ctx.channel.id == REGISTER_CHANNEL_ID:
            name, tag = re.split('[.,/\#-]', arg)

            db = sqlite3.connect('Users.db')
            sql = db.cursor()

            sql.execute(f'SELECT discord_name FROM users WHERE discord_id={ctx.author.id}')
            row = sql.fetchone()

            if row is None:
                url = DOMEN + f'account/{name}/{tag}'
                res = requests.get(url)

                if res.status_code == 429:
                    delete_message = await ctx.reply(f'{ctx.author.mention}, Вибач, але тут ми безсилі, '
                    + 'у серверів Riot є ліміт для того щоб зменшити нагрузку на сервер, спробуй через декілька хвилин')
                    await ctx.message.delete()
                    await asyncio.sleep(5)
                    await delete_message.delete()
                    return

                if res.status_code == 200: 
                    json = res.json()
                    puuid = json['data']['puuid']
                    region = json['data']['region']
                    account_level = json['data']['account_level']
                    image_large_url = json['data']['card']['large']
                    image_wide_url = json['data']['card']['wide']
                    image_small_url = json['data']['card']['small']

                    mmr_url = DOMEN + f'by-puuid/mmr/{region}/{puuid}'
                    mmr_res = requests.get(mmr_url)
                    mmr_json = mmr_res.json()
                    current_tier_patched = mmr_json['data']['currenttierpatched']
                    elo = mmr_json['data']['elo']

                    date_now = datetime.datetime.now()
                    date = date_now.strftime('%d:%m:%Y:%H:%M')

                    sql.execute(f'INSERT INTO users VALUES('
                    + f'\'{ctx.author.id}\', '
                    + f'\'{ctx.author.name}\', '
                    + f'\'{name}\', '
                    + f'\'{tag}\', '
                    + f'\'{current_tier_patched}\', '
                    + f'\'{elo}\', '
                    + f'\'{puuid}\', '
                    + f'\'{region}\', '
                    + f'\'{account_level}\', '
                    + f'\'{image_large_url}\', '
                    + f'\'{image_wide_url}\', '
                    + f'\'{image_small_url}\', ' 
                    + f'\'{date}\')')

                    db.commit()
                    delete_message = await ctx.reply(f'✅{ctx.author.mention}, Вітаю, ти успішно прив\'язав аккаунт')
                    await ctx.message.delete()
                    await asyncio.sleep(5)
                    await delete_message.delete()

                else: #Problems on server or incorrect name and tag
                    delete_message = await ctx.reply(f'❓{ctx.author.mention}, Щось пішло не так ❗ '
                    + '\n Перевір будь ласка чи правильно вказаний нік та тег, '
                    + '\nось приклад ```!reg sendnudes#6770``` ' 
                    + 'якщо все вірно - звернись за допомогою до модератора')
                    await ctx.message.delete()
                    await asyncio.sleep(10)
                    await delete_message.delete()

            else: #User already exists
                delete_message = await ctx.reply(f'❗{ctx.author.mention}, Ти уже зареєстрований, '
                + 'якщо все правильно - напиши модератору, '
                + 'можливо він нам допоможе вирішити твою проблему ❗')
                await ctx.message.delete()
                await asyncio.sleep(5)
                await delete_message.delete()
        else:
            guild = ctx.guild
            stats_channel = guild.get_channel(REGISTER_CHANNEL_ID)
            delete_message = await ctx.reply(f'❗{ctx.author.mention}, у цьому каналі заборонено використання цієї команди.'
            + f'\nЇї потрібно використовувати у {stats_channel.mention}')
            await ctx.message.delete()
            await asyncio.sleep(5)
            await delete_message.delete()
        

