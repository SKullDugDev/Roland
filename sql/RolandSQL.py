# for paths
import pathlib

# for configuration file
import toml

# for class variable type hints
from typing import ClassVar, Optional, TypedDict, List

# for connection
import pyodbc

# for logging
import sqlog

# import database
import SQLRunner

# get configuration file

ROLAND_ACADEMY_FILE: pathlib.Path = pathlib.Path.cwd() / "data" / "configuration" / "roland academy.toml"
ROLAND_ACADEMY: TypedDict = toml.loads(ROLAND_ACADEMY_FILE.read_text(encoding="utf-8"))

# establish dictionaries

sql_variables: TypedDict = ROLAND_ACADEMY['SQLVariables']


class CampaignInfo:
    # connection to the database

    database = SQLRunner.SQLRunner()

    # get sql variables

    CHECK_IF_CAMPAIGN_NAME_IN_DATABASE: ClassVar[str] = sql_variables['CHECK_IF_CAMPAIGN_NAME_IN_DATABASE']
    INSERT_NEW_CAMPAIGN_NAME: ClassVar[str] = sql_variables['INSERT_NEW_CAMPAIGN_NAME']
    GET_CAMPAIGN_LIST: ClassVar[str] = sql_variables['GET_CAMPAIGN_LIST']
    DELETE_CAMPAIGN_BY_NAME: ClassVar[str] = sql_variables['DELETE_CAMPAIGN_BY_NAME']
    DELETE_CAMPAIGNS: ClassVar[str] = sql_variables['DELETE_CAMPAIGNS']

    def __init__(self):

        # variables

        self.campaign_name: List[str] = []
        self.check_failed: bool = True
        self.campaign_list: List[str] = []

    def process_to_add_new_campaign_name(self, user_campaign_name: str, server_name: str) -> bool:
        # begins campaign name adding and rejecting logic; produces a check variable
        # check if the campaign name is in the db and store the results in the campaign list variable

        self.campaign_name = self.check_if_campaign_name_is_in_database(user_campaign_name, server_name)

        # check if the campaign name isn't already in use

        self.check_if_campaign_name_is_new(self.campaign_name, user_campaign_name, server_name)
        return self.check_failed

    def check_if_campaign_name_is_in_database(self, user_campaign_name, server_name) -> list:
        # check database for campaign name and return the result

        result = self.database.cursor.execute(self.CHECK_IF_CAMPAIGN_NAME_IN_DATABASE, user_campaign_name, server_name)

        # log any errors

        sqlog.logger.info("%s\n Parameters: %s, %s", self.CHECK_IF_CAMPAIGN_NAME_IN_DATABASE, user_campaign_name,
                          server_name)
        campaign_name = result.fetchall()
        return campaign_name

    def check_if_campaign_name_is_new(self, campaign_name, user_campaign_name, server_name) -> bool:
        # if it failed the check, it is not new and 02 it will automatically close the transaction and log it

        self.check_failed = True

        # if the name wasn't found in the database that means it is new and things can move on

        if not campaign_name:

            # begin progress to add the new campaign name to the database

            self.add_new_campaign_name_to_database(user_campaign_name, server_name)

            # set the check as not having failed

            self.check_failed = False
            sqlog.logger.info('Passed Check...adding name...')
        else:
            sqlog.logger.info('Transaction Closed. Name already exists.')
        return self.check_failed

    def add_new_campaign_name_to_database(self, user_campaign_name, server_name):
        # add new campaign name
        self.database.cursor.execute(self.INSERT_NEW_CAMPAIGN_NAME, user_campaign_name, server_name)
        sqlog.logger.info("%s\n Parameters: %s, %s", self.INSERT_NEW_CAMPAIGN_NAME,
                          user_campaign_name, server_name)

    def check_campaign_name_before_committing(self, user_campaign_name, server_name):
        # find new campaign and store result

        sqlog.logger.info('Checking database for name...')
        self.database.cursor.execute(self.CHECK_IF_CAMPAIGN_NAME_IN_DATABASE, user_campaign_name, server_name)
        check_campaign_name_added = self.database.cursor.fetchone()

        # If new campaign name now found in database

        if check_campaign_name_added:
            sqlog.logger.info('Committing campaign name to database...')
            try:
                self.database.connection.commit()
                sqlog.logger.info('Campaign name successfully committed to database')
            except pyodbc.DatabaseError:
                sqlog.logger.exception("Commit Error Occurred...")
            finally:
                self.database.cursor.close()
        else:
            sqlog.logger.info('ERROR: Campaign name not found in database to commit...')

    def get_campaign_list(self, server_name):

        self.database.cursor.execute(self.GET_CAMPAIGN_LIST, server_name)
        result = self.database.cursor.fetchall()

        # make list of campaign names
        if result:
            self.campaign_list = [row.CampaignName for row in result]
            campaign_list_string = ', '.join(self.campaign_list)
        else:
            campaign_list_string = 'There are no campaigns yet! Add one!'
        return campaign_list_string

    def delete_campaign_by_name(self, campaign_names_to_be_removed_list: List[str], server_name: str) -> str:
        # variable is a string
        self.get_campaign_list(server_name)
        campaign_list = self.campaign_list
        self.campaign_names_being_removed: str

        # for each campaign name in the list being removed
        for self.campaign_names_being_removed in campaign_names_to_be_removed_list:

            # check that the campaign name is even a thing in the database
            campaign_name_to_be_deleted: List[str] = self.check_if_campaign_name_is_in_database(
                self.campaign_names_being_removed,
                server_name)

            if campaign_name_to_be_deleted:
                # if the campaign name exists in the database, delete it
                sqlog.logger.info('Deleting campaign name from database...')
                self.database.cursor.execute(self.DELETE_CAMPAIGN_BY_NAME, server_name,
                                             self.campaign_names_being_removed)
                sqlog.logger.info("%s\n Parameters: %s, %s", self.DELETE_CAMPAIGN_BY_NAME, server_name,
                                  self.campaign_names_being_removed)
                # check if the campaign name still exists in the database

                delete_check = self.check_if_campaign_name_is_in_database(self.campaign_names_being_removed,
                                                                          server_name)

                if not delete_check:
                    # if delete_check is empty, the name is no longer in the database, commit and close
                    self.database.finalize()
                    test = ', '.join(campaign_names_to_be_removed_list)
                    deletion_message = f"{test} successfully deleted"
                else:
                    deletion_message = f"{self.campaign_names_being_removed} not successful"
            else:
                deletion_message = f"{self.campaign_names_being_removed} not in database"
        return deletion_message

    def delete_all_campaigns_in_server(self, server_name):
        self.database.cursor.execute(self.DELETE_CAMPAIGNS, server_name)
        self.database.finalize()
