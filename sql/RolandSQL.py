# for paths
from pathlib import Path
import pathlib

# for configuration file
import toml

# for class variable type hints
from typing import ClassVar

# for connection
import pyodbc

# for logging
import logging
import sqlog

# get configuration file

ROLAND_ACADEMY_FILE: Path = pathlib.Path.cwd() / "data" / "configuration" / "roland academy.toml"
ROLAND_ACADEMY: dict = toml.loads(ROLAND_ACADEMY_FILE.read_text(encoding="utf-8"))

# establish dictionaries

connection_settings: dict = ROLAND_ACADEMY['ConnectionSettings']
sql_variables: dict = ROLAND_ACADEMY['SQLVariables']


class SqlRunner:
    # get connection string and settings

    DRIVER: ClassVar = connection_settings['DRIVER']
    SERVER: ClassVar = connection_settings['SERVER']
    DATABASE: ClassVar = connection_settings['DATABASE']
    TRUSTED_CONNECTION: ClassVar = connection_settings['TRUSTED_CONNECTION']
    CONNECTION_STRING: ClassVar = f"DRIVER={DRIVER}; SERVER={SERVER}; DATABASE={DATABASE}; \
    Trusted_Connection={TRUSTED_CONNECTION}"

    # get sql variables

    CHECK_IF_CAMPAIGN_NAME_IN_DATABASE: ClassVar = sql_variables['CHECK_IF_CAMPAIGN_NAME_IN_DATABASE']
    INSERT_NEW_CAMPAIGN_NAME: ClassVar = sql_variables['INSERT_NEW_CAMPAIGN_NAME']

    def __init__(self):
        # start connection

        self.connection = pyodbc.connect(self.CONNECTION_STRING)
        self.cursor = self.connection.cursor()

        # variables

        self.result: object = None
        self.campaign_list: list = None
        self.check_failed: bool = None

    def close(self):
        # close other cursors and then close the connection

        cursor = self.connection.cursor()
        cursor.close()
        self.connection.close()

    def process_to_add_new_campaign_name(self, user_campaign_name: str) -> bool:
        # begins campaign name adding and rejecting logic; produces a check variable
        # check if the campaign name is in the db and store the results in the campaign list variable

        self.campaign_list = self.check_if_campaign_name_is_in_database(user_campaign_name)

        # check if the campaign name isn't already in use

        self.check_if_campaign_name_is_new(self.campaign_list, user_campaign_name)
        return self.check_failed

    def check_if_campaign_name_is_in_database(self, user_campaign_name) -> list:
        # check database for campaign name and return the result

        cursor = self.connection.cursor()
        self.result = cursor.execute(self.CHECK_IF_CAMPAIGN_NAME_IN_DATABASE, user_campaign_name)
        print(type(self.result))
        # log any errors

        sqlog.logger.info("%s\n Parameters: %s", self.CHECK_IF_CAMPAIGN_NAME_IN_DATABASE, user_campaign_name)
        campaign_list = self.result.fetchall()
        print(type(campaign_list))
        return campaign_list

    def check_if_campaign_name_is_new(self, campgn_list, user_campaign_name) -> bool:
        # if it failed the check, it is not new and 02 it will automatically close the transaction and log it

        self.check_failed = True

        # if the name wasn't found in the database that means it is new and things can move on

        if not campgn_list:

            # begin progress to add the new campaign name to the database

            self.add_new_campaign_name_to_database(user_campaign_name)

            # set the check as not having failed

            self.check_failed = False
            sqlog.logger.info('Passed Check...adding name...')
        else:
            sqlog.logger.info('Transaction Closed. Name already exists.')
        return self.check_failed

    def add_new_campaign_name_to_database(self, user_campaign_name):
        # add new campaign name
        cursor = self.connection.cursor()
        cursor.execute(self.INSERT_NEW_CAMPAIGN_NAME, user_campaign_name)
        sqlog.logger.info("%s\n Parameters: %s,", self.INSERT_NEW_CAMPAIGN_NAME,
                          user_campaign_name)

    def check_campaign_name_before_committing(self, user_campaign_name):
        # find new campaign and store result

        cursor = self.connection.cursor()
        sqlog.logger.info('Checking database for name...')
        cursor.execute(self.CHECK_IF_CAMPAIGN_NAME_IN_DATABASE, user_campaign_name)
        check_campaign_name_added = cursor.fetchone()

        # If new campaign name now found in database

        if check_campaign_name_added:
            sqlog.logger.info('Committing campaign name to database...')
            try:
                self.connection.commit()
                sqlog.logger.info('Campaign name successfully committed to database')
            except pyodbc.DatabaseError:
                sqlog.logger.exception("Commit Error Occurred...")
            finally:
                cursor.close()
        else:
            logging.info('ERROR: Campaign name not found in database to commit...')
