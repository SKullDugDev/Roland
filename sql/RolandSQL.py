# pull sql vars

from RolandSQLvar import *

# for Roland connection
import pyodbc
import logging
import sqlog


class SQLRunner:
    # connecting to Roland

    def __init__(self):
        self.cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                   'Server=MJÖLNIR;'
                                   'Database=Roland;'
                                   'Trusted_Connection=yes;')
        self.cursor = self.cnxn.cursor()
        self.result = None
        self.campaign_list = None
        self.check_failed = None

    def close(self):
        # close other cursors and then close the connection

        cursor = self.cnxn.cursor()
        self.cursor.close()
        self.cnxn.close()

    def process_to_add_new_campaign_name(self, user_campaign_name):
        # begins campaign name adding and rejecting logic

        cursor = self.cnxn.cursor()

        # check if the campaign name is in the db and store the results in the campaign list variable

        self.campaign_list = self.check_if_campaign_name_is_in_database(user_campaign_name)
        self.check_if_campaign_name_is_new(self.campaign_list, user_campaign_name)
        return

    def check_if_campaign_name_is_in_database(self, user_campaign_name):
        # check database for campaign name and return the result

        cursor = self.cnxn.cursor()
        self.result = self.cursor.execute(sql_check_if_campaign_name_in_database, user_campaign_name)
        sqlog.logger.info("%s\n Parameters: %s", sql_check_if_campaign_name_in_database, user_campaign_name)
        campaign_list = self.result.fetchall()
        return campaign_list

    def check_if_campaign_name_is_new(self, campgn_list, user_campaign_name):
        # if it failed the check it will automatically close the transaction and log it

        self.check_failed = True

        # if the name wasn't found in the database that means it is new and things can move on

        if not campgn_list:
            # get the new campaign id and store it

            new_campaign_id = self.make_new_campaign_id()

            # begin progress to add the new campaign name to the database

            self.add_new_campaign_name_to_database(user_campaign_name, new_campaign_id)

            # set the check as not having failed

            self.check_failed = False
            sqlog.logger.info('Passed Check...adding name...')
        else:
            sqlog.logger.info('Transaction Closed. Name already exists')
        return self.check_failed

    def make_new_campaign_id(self):
        # get max CampaignId, +1, store and return

        cursor = self.cnxn.cursor()
        cursor.execute(sql_get_max_campaign_id)
        current_max_campaign_id = cursor.fetchone()[0]
        new_campaign_id = current_max_campaign_id + 1
        return new_campaign_id

    def add_new_campaign_name_to_database(self, user_campaign_name, new_campaign_id):
        # add new campaign name
        cursor = self.cnxn.cursor()
        cursor.execute(sql_insert_new_campaign_name, new_campaign_id, user_campaign_name)
        sqlog.logger.info("%s\n Parameters: %s, %s", sql_insert_new_campaign_name, new_campaign_id, user_campaign_name)
        return

    def check_campaign_name_before_committing(self, user_campaign_name):
        # find new campaign
        cursor = self.cnxn.cursor()
        cursor.execute(sql_check_if_campaign_name_in_database, user_campaign_name)
        check_new_campgn_jrney = cursor.fetchone()
        if check_new_campgn_jrney:
            try:
                self.cnxn.commit()
            except Exception as e:
                logging.exception("Commit Error Occurred")
        else:
            logging.info('New campaign journey failed. Lost along the way.')
            return

db = SQLRunner()
db.process_to_add_new_campaign_name('Frankenshrub')
db.close()
