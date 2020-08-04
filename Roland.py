import discord
from discord.ext import commands
import RolandSQL
import pyodbc
import logging
import cordlog

# connecting to Roland
cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=MJÖLNIR;'
                      'Database=Roland;'
                      'Trusted_Connection=yes;')
cursor = cnxn.cursor()

# create Client connection
client = discord.Client()

# set prefix
bot_prefix = "!"

client = commands.Bot(command_prefix=bot_prefix)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def campaignadd(ctx, usr_campgn_nm):
    chk_failed = RolandSQL.add_new_campgn_nm(usr_campgn_nm)
    campgn_list = RolandSQL.old_campgn_nm_pull(usr_campgn_nm)
    print(campgn_list)
    print(chk_failed)
    if chk_failed == True:
        await ctx.send('Campaign already exists!')
    else:
        await ctx.send('Campaign added!')
    RolandSQL.chk_new_campgn_add(usr_campgn_nm)

    try:
        cursor = cnxn.cursor()
        print(cursor)
    except Exception as e:
        cordlog.logger.exception("An exception occured in discord..")
        print(cursor)

client.run(TOKEN)
