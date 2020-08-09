# for paths
import pathlib

# for configuration file
import toml

# main module & ext
from discord.ext import commands

# connect to backend
import RolandSQL

back_end = RolandSQL.CampaignInfo()

# typing hint
from typing import NewType

message = NewType('message', str)

# config info

CONFIGURATION_FILE = pathlib.Path.cwd() / "data" / "configuration" / "token.toml"
TOKEN = toml.loads(CONFIGURATION_FILE.read_text())
TOKEN = TOKEN['TOKEN']

# set prefix
bot_prefix = "!"

# create Client connection
client = commands.Bot(command_prefix=bot_prefix)


def campaignadd(ctx, *new_campaigns_from_user):
    tricky_empty_string = " "
    tricky_empty_set = set(tricky_empty_string)
    campaign_added_message = campaign_add_initial_check(new_campaigns_from_user, tricky_empty_set, ctx)
    return campaign_added_message


def campaign_add_initial_check(new_campaigns_from_user, tricky_empty_set, ctx):
    if new_campaigns_from_user and set(new_campaigns_from_user) != tricky_empty_set:
        # if the set/tuple of names provided is not empty, run new campaign adding process and store in check_failed
        check_failed = back_end.process_to_add_new_campaigns(new_campaigns_from_user, ctx.guild.name)
        campaign_added_message = campaign_add_second_check(check_failed, ctx)
    else:
        campaign_added_message = 'You did not enter any campaign names'
    return campaign_added_message


def campaign_add_second_check(check_failed, ctx):
    if check_failed:
        campaign_added_message = f"Already exists on {ctx.guild.name}!"
    elif back_end.invalid_campaigns_not_to_add:
        campaign_added_string = ', '.join((str(s) for s in back_end.valid_campaigns_to_add))
        campaign_invalid_string = ', "'.join((str(s) for s in back_end.invalid_campaigns_not_to_add))
        campaign_added_message = f"{campaign_added_string} added; {campaign_invalid_string} exist(s)."
    else:
        campaign_added_string = ', '.join((str(s) for s in back_end.valid_campaigns_to_add))
        campaign_added_message = f"{campaign_added_string} added."
    return campaign_added_message


def campaignlist(ctx) -> message:
    # get campaign list
    campaign_list = back_end.get_campaigns(ctx.guild.name)

    # get campaign list string
    campaign_list_string = make_campaign_list_string(campaign_list)
    # send message
    return campaign_list_string


def make_campaign_list_string(campaign_list):
    if campaign_list:
        campaign_list_string = ', '.join(campaign_list)
    else:
        campaign_list_string = 'There are no campaigns yet! Add one!'
    return campaign_list_string


def campaignremove(ctx, *campaigns_set_for_removal) -> message:
    tricky_empty_string = " "
    tricky_empty_set = set(tricky_empty_string)
    if campaigns_set_for_removal and set(campaigns_set_for_removal) != tricky_empty_set:
        campaign_deletion_message = back_end.delete_campaign_by_name(campaigns_set_for_removal, ctx.guild.name)
    else:
        campaign_deletion_message = 'You did not enter a campaign name'
    return campaign_deletion_message


def campaignclear(ctx):
    back_end.delete_all_campaigns_in_server(ctx.guild.name)
    campaign_clear_message = 'Campaigns cleared out.'
    return campaign_clear_message
