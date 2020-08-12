# main module & ext
from discord.ext import commands

# connect to backend
import RolandSQL

# connect to Commander
import RolandCommander

# typing hint
from typing import NewType

message = NewType('message', str)

# set prefix
bot_prefix = "!"

# create Client connection
client = commands.Bot(command_prefix=bot_prefix)

# back end connection
back_end = RolandSQL.CampaignInfo()

# rallying commander
RC = RolandCommander


def campaignadd(ctx, campaigns_adding):
    # if it passes the command check, run the function; else return command failure
    if RC.check_command(campaigns_adding):
        return start_campaign_add(campaigns_adding, ctx)
    return 'You did not enter a campaign'


def start_campaign_add(campaigns_adding, ctx):
    return back_end.add_campaign_validation(campaigns_adding, ctx.guild.name)


def campaignlist(ctx) -> str:
    return campainlist_message(back_end.get_campaigns(ctx.guild.name))


def campainlist_message(campaign_list):
    if campaign_list:
        return ', '.join(campaign_list)
    return 'There are no campaigns yet! Add one!'


def campaignremove(ctx, campaigns_removing) -> str:
    if RC.check_command(campaigns_removing):
        return back_end.remove_campaigns_process(campaigns_removing, ctx.guild.name)
    return 'You did not enter a campaign name'


def campaignclear(ctx):
    back_end.delete_server_campaigns(ctx.guild.name)
    return 'Campaigns cleared out.'
