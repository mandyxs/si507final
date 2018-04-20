import unittest
from final_main import *

class TestRequest(unittest.TestCase):

    def test_page_request(self):
        url = 'http://www.soccerstats.com/latest.asp?league=germany'
        res = request_page(url)
        self.assertIn(url, CACHE_DICTION)

class TestDatabase(unittest.TestCase):

    def test_league_table(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        sql = 'SELECT name FROM Leagues'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Bundesliga',), result_list)
        self.assertEqual(len(result_list), 5)

        conn.close()

    def test_team_table_join(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        sql = '''
            SELECT Teams.name FROM Teams 
            JOIN Leagues
            ON Teams.league = Leagues.id
            WHERE Leagues.country = 'Germany'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Bayern Munich',), result_list)
        self.assertEqual(len(result_list), 18)

        conn.close()


    def test_players_table_join(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        sql = '''
            SELECT name FROM Players 
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('D. Silva',), result_list)
        self.assertEqual(len(result_list), 1194)

        sql = '''
            SELECT Players.name FROM Players 
            JOIN Leagues
            ON Players.league = Leagues.id
            WHERE Leagues.country = 'Germany'
            ORDER BY Players.goals DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchone()
        self.assertEqual('R. Lewandowski', result_list[0])

        conn.close()

class TestDataProcessing(unittest.TestCase):

    def test_get_team_rank(self):
        db = database_select(DB_NAME)
        res = db.get_team_rank('Germany')
        self.assertEqual('Bayern Munich', res[-1][0])
        self.assertEqual('FC Köln', res[0][0])

    def test_get_goal_dis(self):
        db = database_select(DB_NAME)
        res = db.get_goal_dis('Germany')
        self.assertEqual((1,1,37), res[0])
        self.assertEqual(len(res), 30)

    def test_get_chart_stats(self):
        db = database_select(DB_NAME)
        res = db.get_chart_stats('Bayern Munich')
        self.assertEqual((24,3,3), res)

    def test_get_top_players(self):
        db = database_select(DB_NAME)
        res = db.get_top_players('Germany')
        self.assertIn('Bayern Munich', res)
        self.assertEqual(len(res['Bayern Munich']), 3)

unittest.main()