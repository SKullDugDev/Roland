sql_chk_campgn_nm = '''
    SELECT
        CampaignName
    FROM
        Campaign
    WHERE
        CampaignName Like ?'''

sql_max_campgnid = "SELECT MAX(CampaignID) FROM Campaign"


sql_new_usr_campgn = '''
INSERT INTO
    Campaign (CampaignID, CampaignName, DMName, PlayerOneName)
VALUES
    (?,?, 'unknown_player','unknown_player') '''

