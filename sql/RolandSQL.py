# for paths
import pathlib

# for configuration file
import toml

# for class variable type hints
from typing import ClassVar, TypedDict, List

# for connection
import SQLRunner

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

    CHECK_IF_CAMPAIGN_NAME_IN_DATABASE: ClassVar[str] = sql_variables['CHECK_IF_CAMPAIGN_NAME_IN_DATABASE']
    INSERT_NEW_CAMPAIGN_NAME: ClassVar[str] = sql_variables['INSERT_NEW_CAMPAIGN_NAME']
    GET_CAMPAIGN_LIST: ClassVar[str] = sql_variables['GET_CAMPAIGN_LIST']
    DELETE_CAMPAIGN_BY_NAME: ClassVar[str] = sql_variables['DELETE_CAMPAIGN_BY_NAME']
    DELETE_CAMPAIGNS: ClassVar[str] = sql_variables['DELETE_CAMPAIGNS']

    def __init__(self):

        # variables

        self.campaigns: List[str] = []
        self.check_failed: bool = True
        self.invalid_campaigns_not_to_add: set = set()
        self.valid_campaigns_to_add: set = set()
        self.valid_campaign_for_removal: set = set()

    def process_to_add_new_campaigns(self, new_campaigns_from_user, server_name: str) -> bool:
        # add or reject new campaigns

        # sets campaigns to be added, literally
        campaigns_to_be_added: set = set(new_campaigns_from_user)

        # get campaign list set
        current_campaigns: set = set(self.get_campaigns(server_name))

        # campaigns not to add
        self.invalid_campaigns_not_to_add = current_campaigns.intersection(campaigns_to_be_added)

        # campaigns to add
        self.valid_campaigns_to_add = campaigns_to_be_added.difference(self.invalid_campaigns_not_to_add)

        # add campaigns to database, return status
        self.check_failed = self.add_campaigns_to_database(self.valid_campaigns_to_add, server_name)

        return self.check_failed

    def add_campaigns_to_database(self, valid_campaigns_to_add, server_name):
        if valid_campaigns_to_add:
            # if there are valid campaigns to add
            sqlog.logger.info('Adding new campaigns...')
            # add new campaigns
            self.add_new_campaigns(valid_campaigns_to_add, server_name)
            sqlog.logger.info('Campaigns successfully added...Checking commit requirements...')
            current_campaigns = set(self.get_campaigns(server_name))
            # check they were added before committing
            self.add_campaign_commit_check(current_campaigns, valid_campaigns_to_add)
        else:
            # all the new names failed the check
            self.check_failed = True
        return self.check_failed

    def add_new_campaigns(self, valid_campaigns_to_add, server_name):
        # add each campaign that is listed as valid
        for valid_campaigns in valid_campaigns_to_add:
            database.cursor.execute(self.INSERT_NEW_CAMPAIGN_NAME, valid_campaigns, server_name)
            sqlog.logger.info("%s\n Parameters: %s, %s", self.INSERT_NEW_CAMPAIGN_NAME,
                              valid_campaigns, server_name)

    def add_campaign_commit_check(self, current_campaigns, valid_campaigns_to_add):
        if current_campaigns.intersection(valid_campaigns_to_add):
            # if valid campaigns are now in database, commit
            sqlog.logger.info('Commit requirements passed..committing...')
            database.finalize()
            sqlog.logger.info('Committed...')
            self.check_failed = False

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

    def delete_campaign_by_name(self, campaigns_set_for_removal: tuple, server_name: str) -> str:
        # set campaigns to be removed, literally
        campaigns_set_for_removal: set = set(campaigns_set_for_removal)
        # get the set of current campaigns
        current_campaigns: set = set(self.get_campaigns(server_name))
        # find which campaigns are in the current list, which thus can be removed
        self.valid_campaign_for_removal = campaigns_set_for_removal.intersection(current_campaigns)
        # invalid campaigns will not be removed; is not a campaign
        invalid_campaign_for_removal = campaigns_set_for_removal.difference(self.valid_campaign_for_removal)
        sqlog.logger.info('Deleting campaigns...')
        # gets a set of the campaigns being removed
        campaigns_being_removed_set: set = self.individual_campaign_deletion(self.valid_campaign_for_removal,
                                                                             server_name)
        # check if the campaigns are really deleted and commit
        self.are_campaigns_deleted_properly(server_name, campaigns_being_removed_set)
        # get deletion message and return it
        deletion_message = self.get_campaign_deletion_message(invalid_campaign_for_removal)
        return deletion_message

    def individual_campaign_deletion(self, valid_campaign_name_for_removal, server_name):
        # create empty set to hold info
        campaign_names_being_removed_set = set()
        # remove, from the database, each campaign that is in the valid for removal list
        for campaign_names_being_removed in valid_campaign_name_for_removal:
            database.cursor.execute(self.DELETE_CAMPAIGN_BY_NAME, server_name, campaign_names_being_removed)
            sqlog.logger.info("%s\n Parameters: %s, %s", self.DELETE_CAMPAIGN_BY_NAME, server_name,
                              campaign_names_being_removed)
            # each time we do so, store away the name of the campaign we're removing
            campaign_names_being_removed_set.add(campaign_names_being_removed)
        # returns the set of campaigns we removed
        return campaign_names_being_removed_set

    def are_campaigns_deleted_properly(self, server_name, campaign_names_being_removed):
        # checks to see if the deleted set is still in the database
        campaigns_still_there_check = set(self.get_campaigns(server_name)).intersection(campaign_names_being_removed)
        if campaigns_still_there_check == set():
            # an empty set means no campaigns set for deletion found in database
            sqlog.logger.info('Committing...')
            database.finalize()
            sqlog.logger.info('Committed...')

    def get_campaign_deletion_message(self, invalid_campaign_for_removal):
        # get the campaigns as a string of campaigns
        valid_string = ', '.join(str(s) for s in self.valid_campaign_for_removal)
        invalid_string = ', '.join(str(s) for s in invalid_campaign_for_removal)
        if self.valid_campaign_for_removal and invalid_campaign_for_removal:
            # if both exist, give me both
            deletion_message = f"{valid_string} removed; {invalid_string} non-existent."
        elif self.valid_campaign_for_removal and not invalid_campaign_for_removal:
            # if the input was only things to be removed
            deletion_message = f"{valid_string} removed."
        elif not self.valid_campaign_for_removal and invalid_campaign_for_removal:
            # if the input was non-existent campaigns
            deletion_message = f"{invalid_string} non-existent."
        else:
            deletion_message = f"'something went wrong: {valid_string} and {invalid_string}"
        return deletion_message
        # when do I want to show just invalid string

    def delete_all_campaigns_in_server(self, server_name):
        sqlog.logger.info('Deleting Campaign...')
        database.cursor.execute(self.DELETE_CAMPAIGNS, server_name)
        sqlog.logger.info('Campaign Deleted...')
        database.finalize()
