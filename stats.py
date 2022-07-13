from msilib.schema import File
import nextcord
from nextcord.ext import commands, tasks
from constants import *
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import asyncio
import requests

class UserStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx):
        if not ctx.channel.id == STATS_CHANNEL_ID:
            guild = ctx.guild
            stats_channel = guild.get_channel(STATS_CHANNEL_ID)
            delete_message = await ctx.reply(f'❗{ctx.author.mention}, у цьому каналі заборонено використання цієї команди.'
            + f'\nЇї потрібно використовувати у {stats_channel.mention}')
            await ctx.message.delete()
            await asyncio.sleep(5)
            await delete_message.delete()
            return
        
        db = sqlite3.connect('Users.db')
        sql = db.cursor()
        sql.execute('SELECT valorant_name, '
        + 'valorant_tag, '
        + 'current_tier_patched, '
        + 'elo, '
        + 'region, '
        + 'account_level, '
        + 'image_large_url '
        + f'FROM users WHERE discord_id={ctx.author.id}')
        row = sql.fetchone()

        if row is None:
            delete_message = await ctx.reply(f'❗{ctx.author.mention}, Я не можу знайти тебе у базі даних, ти впевнений що зареєструвався?')
            await ctx.message.delete()
            await asyncio.sleep(5)
            await delete_message.delete()
            return

        valorant_name = row[0] + '#' + row[1]
        discord_name = ctx.author.name
        current_tier_patched = row[2]
        elo = row[3]
        region = row[4]
        account_level = row[5]
        image_large_url = row[6]

        response = requests.get(image_large_url)
        open('border.png', 'wb').write(response.content)

        font = ImageFont.truetype('fonts\EternalUiRegular.ttf', 16)

        card = Image.open('img\playercardempty.png')
        border = Image.open('border.png')
        rank = Image.open('img/ranks/' + current_tier_patched + '.png')
        card.paste(border, (268,0))
        card.paste(rank, (103,156), rank)

        draw = ImageDraw.Draw(card)
        draw.text((45,294), valorant_name, (175, 198, 220), font=font)
        draw.text((45,394), elo, (175, 198, 220), font=font)
        draw.text((45,494), account_level, (175, 198, 220), font=font)
        draw.text((234,616), region, (175, 198, 220), font=font)
        draw.text((8,616), discord_name, (175, 198, 220), font=font)
        w, h = font.getsize(current_tier_patched)
        x = (268 - w)/2
        draw.text((x,94), current_tier_patched, (175, 198, 220), font=font)

        card.save('playercard.png')
        await ctx.reply(file=nextcord.File('playercard.png'))

        roles_list = [
            'Ascendant 1', 
            'Ascendant 2',
            'Ascendant 3',
            'Bronze 1',
            'Bronze 2',
            'Bronze 3',
            'Diamond 1',
            'Diamond 2',
            'Diamond 3',
            'Gold 1',
            'Gold 2',
            'Gold 3',
            'Immortal 1',
            'Immortal 2',
            'Immortal 3',
            'Iron 1',
            'Iron 2',
            'Iron 3',
            'Platinum 1',
            'Platinum 2',
            'Platinum 3',
            'Radiant',
            'Silver 1',
            'Silver 2',
            'Silver 3',
            'None']
        member_roles = ctx.author.roles
        for role in roles_list:
            for member_role in member_roles:
                if member_role.name == role:
                    await ctx.author.remove_roles(member_role)
                else:
                    pass
            
        guild_roles = ctx.guild.roles

        for role in guild_roles:
            print(f'{role.name} == {current_tier_patched}')
            if role.name == current_tier_patched:
                await ctx.author.add_roles(role)


        await ctx.message.delete()

        
