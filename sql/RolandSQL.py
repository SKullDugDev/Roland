# pull sql vars

from RolandSQLvar import *

# for Roland connection
import pyodbc
import logging
import sqlog


class SQLRunner:
    # connecting to Roland

    def __init__(self):
        pass

    def add_new_campgn_nm(self, usr_campgn_nm):
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                   'Server=MJÖLNIR;'
                                   'Database=Roland;'
                                   'Trusted_Connection=yes;')
        cursor = cnxn.cursor()
        self.old_campgn_nm_pull(usr_campgn_nm)
        self.campgn_list = old_campgn_nm_pull.campgn_list
        self.chk_failed = add_new_campgn_chk(campgn_list, usr_campgn_nm)
        return self.chk_failed

    def old_campgn_nm_pull(self, usr_campgn_nm):
        # check db for CampaignName; store in rchable var
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                   'Server=MJÖLNIR;'
                                   'Database=Roland;'
                                   'Trusted_Connection=yes;')
        cursor = cnxn.cursor()
        result = cursor.execute(sql_chk_campgn_nm, usr_campgn_nm)
        sqlog.logger.info("%s\n Parameters: %s", sql_chk_campgn_nm, usr_campgn_nm)
        self.old_campgn_nm_pull.campgn_list = result.fetchall()
        return self.old_campgn_nm_pull.campgn_list

    def add_new_campgn_chk(self, campgn_list, usr_campgn_nm):
        output = True
        if not campgn_list:
            mk_new_campgnid()
            new_campgnid = mk_new_campgnid.new_campgnid
            sqladd_new_campgn_nm(usr_campgn_nm, new_campgnid)
            output = False
        else:
            sqlog.logger.info('Transaction Closed. Name already exists')
        return output

    def mk_new_campgnid(self):
        # get max CampaignId, +1, store in rchable var
        cursor.execute(sql_max_campgnid)
        current_max_campgnid = cursor.fetchone()[0]
        mk_new_campgnid.new_campgnid = current_max_campgnid + 1
        return

    def sqladd_new_campgn_nm(self, usr_campgn_nm, new_campgnid):
        # add new CampaignName
        result = cursor.execute(sql_new_usr_campgn, new_campgnid, usr_campgn_nm)
        sqlog.logger.info("%s\n Parameters: %s, %s", sql_new_usr_campgn, new_campgnid, usr_campgn_nm)
        return

    def chk_new_campgn_add(self, usr_campgn_nm):
        # find new campaign
        result = cursor.execute(sql_chk_campgn_nm, usr_campgn_nm)
        check_new_campgn_jrney = cursor.fetchone()
        if check_new_campgn_jrney:
            try:
                cnxn.commit()
            except Exception as e:
                logging.exception("Commit Error Occurred")
        else:
            logging.info('New campaign journey failed. Lost along the way.')
            return

test_run = SQLRunner()
print(test_run.add_new_campgn_nm('TheShrub'))
test_run.close()
