import asyncio
import datetime
import re
import requests
import sqlite3
from nextcord.ext import commands, tasks
from constants import *

class UpdateUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            delete_message = await ctx.reply(f'❗{ctx.author.mention}, ви можете використовувати цю команду раз в **10 хвилин**')
            await ctx.message.delete()
            await asyncio.sleep(5)
            await delete_message.delete()

    @commands.command()
    @commands.cooldown(1, 600.0, commands.BucketType.user)
    async def update(self, ctx):
        if ctx.channel.id == STATS_CHANNEL_ID:
            db = sqlite3.connect('Users.db')
            sql = db.cursor()
            sql.execute(f'SELECT valorant_name, valorant_tag FROM users WHERE discord_id={ctx.author.id}')
            row = sql.fetchone()
                                    
            if row is None:
                delete_message = await ctx.reply(f'❗{ctx.author.mention}, Я не можу знайти тебе у базі даних, ти впевнений що зареєструвався?')
                await ctx.message.delete()
                await asyncio.sleep(5)
                await delete_message.delete()
                                    
            else:
                name = row[0]
                tag = row[1]

                url = DOMEN + f'account/{name}/{tag}'
                res = requests.get(url)

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

                    sql.execute(f'UPDATE users SET '
                    + f'current_tier_patched=\'{current_tier_patched}\', '
                    + f'elo=\'{elo}\', '
                    + f'account_level=\'{account_level}\', '
                    + f'image_large_url=\'{image_large_url}\', '
                    + f'image_wide_url=\'{image_wide_url}\', '
                    + f'image_small_url=\'{image_small_url}\', '
                    + f'updated=\'{date}\' '
                    + f'WHERE discord_id={ctx.author.id}')
                    db.commit()

                    delete_message = await ctx.reply('Ви успішно оновили інформацію')
                    await ctx.message.delete()
                    await asyncio.sleep(5)
                    await delete_message.delete()


                else:
                    ctx.reply(f'Помилка на сервері, або він просто лежить XD')

        else:
            guild = ctx.guild
            stats_channel = guild.get_channel(STATS_CHANNEL_ID)
            delete_message = await ctx.reply(f'❗{ctx.author.mention}, у цьому каналі заборонено використання цієї команди.'
            + f'\nЇї потрібно використовувати у {stats_channel.mention}')
            await ctx.message.delete()
            await asyncio.sleep(5)
            await delete_message.delete()