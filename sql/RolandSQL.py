# for paths
import pathlib

# for configuration file
import toml

# for class variable type hints
from typing import ClassVar, TypedDict, List, Set

# for connection
import pyodbc
import SQLRunner
import itertools

# for logging
import sqlog

# get configuration file

ROLAND_ACADEMY_FILE: pathlib.Path = pathlib.Path.cwd() / "data" / "configuration" / "roland academy.toml"
ROLAND_ACADEMY: TypedDict = toml.loads(ROLAND_ACADEMY_FILE.read_text(encoding="utf-8"))

# establish dictionaries

sql_variables: TypedDict = ROLAND_ACADEMY['SQLVariables']

# connection to the database

database = SQLRunner.SQLRunner()


class CampaignInfo:
    # get sql variables

    INSERT_NEW_CAMPAIGN_NAME: ClassVar[str] = sql_variables['INSERT_NEW_CAMPAIGN_NAME']
    GET_CAMPAIGN_LIST: ClassVar[str] = sql_variables['GET_CAMPAIGN_LIST']
    DELETE_CAMPAIGN_BY_NAME: ClassVar[str] = sql_variables['DELETE_CAMPAIGN_BY_NAME']
    DELETE_CAMPAIGNS: ClassVar[str] = sql_variables['DELETE_CAMPAIGNS']

    def __init__(self):

        # variables

        self.campaigns: List[str] = []
        self.check_failed: bool = True

    def add_campaign_validation(self, campaigns_adding, server_name: str) -> str:
        # for every campaign submitted, take the caseless version and put it in a set
        sqlog.logger.info('Setting up new campaigns...')
        campaigns_adding = {name.casefold() for name in campaigns_adding}
        # for every current campaign, take the caseless version and put it in a set
        sqlog.logger.info('Getting current campaigns...')
        current_campaigns = {name.casefold() for name in self.get_campaigns(server_name)}
        # campaigns already in the database shouldn't be added; this intersection reveals that set
        sqlog.logger.info('Validating...')
        invalid_campaigns = current_campaigns.intersection(campaigns_adding)
        # from the set campaign set we want to add, remove what we have already, title them and make a new set
        valid_campaigns = {name.title() for name in
                           campaigns_adding.difference(invalid_campaigns)}
        # gonna try something here to make a string and return that instead
        return self.add_campaign_process(valid_campaigns, server_name, invalid_campaigns)

    def add_campaign_process(self, valid_campaigns, server_name, invalid_campaigns):
        # if there are no valid campaigns, end and return a failure message
        if not valid_campaigns:
            return f"Already exists on {server_name}"
        # else, add the campaigns in
        sqlog.logger.info('Adding new campaigns...')
        self.add_new_campaigns(valid_campaigns, server_name)
        sqlog.logger.info('Campaigns successfully added...Checking commit requirements...')
        # check they were added before committing
        return self.add_campaign_commit_check(set(self.get_campaigns(server_name)), valid_campaigns, invalid_campaigns)

    def add_new_campaigns(self, campaigns_adding, server_name):
        # add each campaign that is listed as valid
        try:
            param = zip(itertools.repeat(server_name), campaigns_adding)
            database.cursor.executemany(self.INSERT_NEW_CAMPAIGN_NAME, param)
            sqlog.logger.info("%s\n Parameters: %s, %s", self.INSERT_NEW_CAMPAIGN_NAME,
                              campaigns_adding, server_name)
        except pyodbc.DatabaseError:
            sqlog.logger.exception('Error Exception Occurred')

    def add_campaign_commit_check(self, current_campaigns, valid_campaigns, invalid_campaigns):
        if not current_campaigns.intersection(valid_campaigns):
            # if the set is empty, they weren't added so fail
            return 'Campaigns not added. Talk to Ra.'
        # else
        sqlog.logger.info('Commit requirements passed..committing...')
        database.finalize()
        sqlog.logger.info('Committed...')
        # by this point, we know there is a valid campaign so if there are no invalids, the message is just what's added
        if not invalid_campaigns:
            return f"{', '.join([str(s) for s in valid_campaigns])} added"
        # if there is an invalid, mention it wasn't added
        return f"{', '.join([str(s) for s in valid_campaigns])} added;" \
               f" {', '.join([str(s) for s in invalid_campaigns])} already exist "

    def get_campaigns(self, server_name):
        # get campaigns
        sqlog.logger.info('Getting list of campaigns...')
        database.cursor.execute(self.GET_CAMPAIGN_LIST, server_name)
        sqlog.logger.info("%s\n Parameters: %s", self.GET_CAMPAIGN_LIST, server_name)
        sqlog.logger.info("Campaigns retrieved...")
        query = database.cursor.fetchall()
        # make list of campaigns
        campaign_list = [row.CampaignName for row in query]
        return campaign_list

    def remove_campaigns_process(self, campaigns_removing, server_name: str) -> str:
        # for every campaign submitted for removal, take the caseless version and put it in a set
        sqlog.logger.info('Setting up campaigns for removal...')
        campaigns_removing = {name.casefold() for name in campaigns_removing}
        # get the caseless set of current campaigns
        sqlog.logger.info('Getting current campaigns...')
        current_campaigns = {name.casefold() for name in self.get_campaigns(server_name)}
        # find which campaigns are in the current list, which thus can be removed
        sqlog.logger.info('Validating...')
        valid_campaigns = campaigns_removing.intersection(current_campaigns)
        # invalid campaigns will not be removed; is not a campaign
        invalid_campaigns = campaigns_removing.difference(valid_campaigns)
        sqlog.logger.info('Deleting campaigns...')
        # gets a set of the campaigns being removed
        return self.check_campaign_removal(server_name, self.campaign_removal(valid_campaigns, server_name),
                                           invalid_campaigns)

    def campaign_removal(self, campaigns_removing, server_name):
        # remove, from the database, each campaign that is in the valid for removal list
        try:
            param = zip(itertools.repeat(server_name), campaigns_removing)
            database.cursor.executemany(self.DELETE_CAMPAIGN_BY_NAME, param)
            sqlog.logger.info("%s\n Parameters: %s, %s", self.DELETE_CAMPAIGN_BY_NAME, server_name, campaigns_removing)
        except pyodbc.DatabaseError:
            sqlog.logger.exception('Error Exception Occurred')
        # then return the set of names we just removed which should only be the valid names
        return campaigns_removing

    def check_campaign_removal(self, server_name, valid_campaigns,
                               invalid_campaigns):
        # checks to see if the deleted set is still in the database
        if set(self.get_campaigns(server_name)).intersection(valid_campaigns):
            test = set(self.get_campaigns(server_name)).intersection(valid_campaigns)
            # if it isn't empty, stop and return a failure
            return 'Campaigns not removed properly. See Ra.'
        # an empty set means the campaigns were properly removed
        sqlog.logger.info('Committing...')
        database.finalize()
        sqlog.logger.info('Committed...')
        if invalid_campaigns:
            return f"{', '.join([str(s) for s in valid_campaigns])} removed;" \
                   f" {', '.join([str(s) for s in invalid_campaigns])} doesn't exist."
        return f"{', '.join([str(s) for s in valid_campaigns])} removed."

    def delete_server_campaigns(self, server_name):
        sqlog.logger.info('Deleting Campaigns...')
        database.cursor.execute(self.DELETE_CAMPAIGNS, server_name)
        sqlog.logger.info('Campaigns Deleted...')
        database.finalize()
