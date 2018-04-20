import json
import requests
import plotly.plotly as py
from bs4 import BeautifulSoup
import sqlite3

## init database ------------------------------------------

DB_NAME = 'soccer.db'

# function to init database and create tables
def init_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    def execute(statements):
        for statement in statements:
            cur.execute(statement)
        conn.commit()

    execute([
        "DROP TABLE IF EXISTS 'Leagues';",
        "DROP TABLE IF EXISTS 'Teams';",
        "DROP TABLE IF EXISTS 'Games';",
        "DROP TABLE IF EXISTS 'Players';"
    ])

    execute([
        '''
          CREATE TABLE 'Leagues' (
              'id' INTEGER PRIMARY KEY AUTOINCREMENT,
              'name' TEXT NOT NULL,
              'country' TEXT NOT NULL
          );
        '''
        ,

        '''
          CREATE TABLE 'Teams' (
              'id' INTEGER PRIMARY KEY AUTOINCREMENT,
              'name' TEXT NOT NULL,
              'league' INTEGER NOT NULL,
              'points' INTEGER NOT NULL,
              'win' INTEGER ,
              'draw' INTEGER ,
              'loss' INTEGER ,
              'rank' INTEGER NOT NULL,
              FOREIGN KEY(league) REFERENCES Leagues(id)
          );
        '''
        ,

        '''
          CREATE TABLE 'Games' (
              'id' INTEGER PRIMARY KEY AUTOINCREMENT,
              'home_team' INTEGER NOT NULL,
              'away_team' INTEGER NOT NULL,
              'home_goal' INTEGER NOT NULL,
              'away_goal' INTEGER NOT NULL,
              'league' INTEGER NOT NULL,
              FOREIGN KEY(home_team) REFERENCES Teams(id),
              FOREIGN KEY(away_team) REFERENCES Teams(id),
              FOREIGN KEY(league) REFERENCES Leagues(id)
              
          );
        '''
        ,

        '''
          CREATE TABLE 'Players' (
              'id' INTEGER PRIMARY KEY AUTOINCREMENT,
              'name' TEXT NOT NULL,
              'goals' INTEGER NOT NULL,
              'team' INTEGER NOT NULL,
              'league' INTEGER NOT NULL,
              FOREIGN KEY(team) REFERENCES Teams(id),
              FOREIGN KEY(league) REFERENCES Leagues(id)
              
          );
        '''
    ])

    conn.close()
  

# function to populate league table
def init_league(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    leagues = [
        ['Premier League', 'England'],
        ['Serie A', 'Italy'],
        ['La Liga', 'Spain'],
        ['Bundesliga', 'Germany'],
        ['Ligue 1', 'France']
    ]

    stmt = '''
        INSERT INTO 'Leagues' (name, country)
        VALUES (?,?)
    '''

    for league in leagues:
        values = (league[0], league[1])
        cur.execute(stmt, values)
        conn.commit()

    conn.close()

## classes to handle data ------------------------------------------

#class to handle all database process
class Database():
    def __init__(self, db_name):
        self.name = db_name

    def init(self):
        init_db(self.name)
        init_league(self.name)

    def get_leagues(self):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute('SELECT id, name, country FROM Leagues;')

        countries = []
        for country in cur.fetchall():
            countries.append({
                'id': country[0],
                'name': country[1],
                'country': country[2],
            })

        conn.close()
        return countries

    def get_teams_id(self):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute('SELECT id FROM Teams;')

        teams = []

        for team in cur.fetchall():
            teams.append(team[0])

        conn.close()
        return teams

    def get_team_id_by_name(self, name):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("SELECT id FROM 'Teams' WHERE name = ?", (name,))

        team_id = cur.fetchone()[0]

        conn.close()
        return team_id

    def get_team_result(self, team_id):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        statement = '''
            SELECT * FROM (
                SELECT COUNT(*) as home_team_win_count  FROM Games WHERE home_team = ? AND home_goal > away_goal
            ), (
                SELECT COUNT(*) as away_team_win_count FROM Games WHERE away_team = ? AND away_goal > home_goal 
            ), (
                SELECT COUNT(*) as home_team_draw_count  FROM Games WHERE home_team = ? AND home_goal = away_goal
            ), (
                SELECT COUNT(*) as away_team_draw_count FROM Games WHERE away_team = ? AND home_goal = away_goal
            ), (
                SELECT COUNT(*) as home_team_loss_count  FROM Games WHERE home_team = ? AND home_goal < away_goal
            ), (
                SELECT COUNT(*) as away_team_loss_count FROM Games WHERE away_team = ? AND away_goal < home_goal
            );
        '''

        cur.execute(statement, tuple([team_id] * 6))

        result = cur.fetchone()

        win = result[0] + result[1]
        draw = result[2] + result[3]
        loss = result[4] + result[5]

        conn.close()
        return {
            'win': win,
            'draw': draw,
            'loss': loss,
        }

    def update_team_result(self, team_id, result):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        cur.execute('''
          UPDATE Teams
            SET win=?, draw=?, loss=?
            WHERE id = ?
        ''', (result['win'], result['draw'], result['loss'], team_id))

        conn.commit()
        conn.close()
        return

    def save_teams_data(self, team_list):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        stmt = '''
                INSERT INTO 'Teams' (name, league, points, rank)
                VALUES (?,?,?,?)
            '''

        for team in team_list:
            values = (team.name, team.league, team.points, team.rank)
            cur.execute(stmt, values)
            conn.commit()

        conn.close()
        return

    def save_games_data(self, games):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        stmt = '''
                INSERT INTO 'Games' (home_team, away_team, home_goal, away_goal, league)
                VALUES (?,?,?,?,?)
            '''

        for game in games:
            home_team_id = self.get_team_id_by_name(game.home_team)
            away_team_id = self.get_team_id_by_name(game.away_team)
            values = (home_team_id, away_team_id, game.home_goal, game.away_goal, game.league)
            cur.execute(stmt, values)
            conn.commit()

        conn.close()
        return

    def save_players_data(self, players):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        stmt = '''
            INSERT INTO 'Players' (name, goals, team, league)
            VALUES (?,?,?,?)
        '''

        for player in players:
            values = (player.name, player.goals, player.team, player.league)
            cur.execute(stmt, values)
            conn.commit()

        conn.close()
        return

# class used to handle team data
class Team():
    def __init__(self, name, league, points, rank, url):
        base_url = 'http://www.soccerstats.com/'
        self.name = name
        self.league = league
        self.points = points
        self.rank = rank
        self.url = base_url + url

#class used to handle game data
class Game():
    def __init__(self, home_team, away_team, home_goal, away_goal, league):
        self.home_team = home_team
        self.away_team = away_team
        self.home_goal = home_goal
        self.away_goal = away_goal
        self.league = league

#class used to handle player data
class Player():
    def __init__(self, name, goals, team, league):
        self.name = name
        self.goals = goals
        self.team = team
        self.league = league


## crawling data and caching ------------------------------------------

CACHE_FNAME = 'cache.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

# function for request and caching
def request_page(url):
    if url in CACHE_DICTION:
        print ('getting cached data...')
        return CACHE_DICTION.get(url)
    else:
        print ('fetching new data...')
        resp = requests.get(url)
        CACHE_DICTION[url] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION, indent=4)
        write_cache = open(CACHE_FNAME,"w")
        write_cache.write(dumped_json_cache)
        write_cache.close() 
        return CACHE_DICTION.get(url)

# function to get url of main page of each league
def get_league_url(country):
    return 'http://www.soccerstats.com/latest.asp?league=' + country.lower()

# function to get html content of all league main page
def get_league_pages():
    results = {}

    for league in database.get_leagues():
        url = get_league_url(league['country'])
        results[league['id']]=request_page(url)
    return results

# function to iterate html content of all league main page and returns a list of team classes
def get_team_data():
    league_html = get_league_pages()
    teams = []
    for league_id, html in league_html.items():
        league = league_id
        soup = BeautifulSoup(html,'html.parser')
        league_table = soup.find_all('table', {'id':'btable'})
        team_rows = league_table[2].find_all('tr', {'class': 'odd'})
        for team in team_rows:
            #name, league, points, rank, url
            name = team.find_all('td')[1].get_text().strip()
            points = int(team.find_all('td')[9].get_text().strip())
            rank = int(team.find_all('td')[0].get_text().strip())
            url = team.find_all('td')[1].a['href']
            teams.append(Team(name=name, league=league, points=points, rank=rank, url=url))
    return teams


# function to get game page urls
def get_game_url(country):
    return 'http://www.soccerstats.com/team_results.asp?pmtype=bydate&league=' + country.lower()

# request html content from game pages
def get_game_pages():
    results = {}

    for league in database.get_leagues():
        url = get_game_url(league['country'])
        results[league['id']] = request_page(url)

    return list(results.items())

# extract data from game pages html
def get_games_data():
    games = []

    for league_id, html in get_game_pages():
        soup = BeautifulSoup(html, 'html.parser')
        tables_of_games = soup.find_all('table', {'id': 'btable'})
        games_with_finished = tables_of_games[0].find_all('tr', {'class': 'odd'})

        for game in games_with_finished:
            sections = game.find_all('td')
            teams = sections[2].get_text().strip().split(' - ')
            goals = sections[3].get_text().strip().split(' - ')

            games.append(Game(
                home_team=teams[0],
                away_team=teams[1],
                home_goal=goals[0],
                away_goal=goals[1],
                league=league_id
            ))

    return games


def get_teams_soup(html):
    soup = BeautifulSoup(html, 'html.parser')
    league_table = soup.find_all('table', {'id': 'btable'})
    teams_soup = league_table[2].find_all('tr', {'class': 'odd'})
    return teams_soup

def get_player_soup(team_soup):
    url = 'http://www.soccerstats.com/' + team_soup.find_all('td')[1].find('a')['href']
    soup = BeautifulSoup(request_page(url), 'html.parser')
    players_table = soup.find_all('table', {'id': 'btable'})[0]
    player_rows = players_table.find_all('tr', {'class': 'odd'})
    return player_rows

# get player data
def get_players_data():
    players = []
    league_html = get_league_pages()

    for league_id, html in league_html.items():

        for team_soup in get_teams_soup(html):
            team_name = team_soup.find_all('td')[1].get_text().strip()
            team_id = database.get_team_id_by_name(team_name)

            for player_soup in get_player_soup(team_soup):
                name = player_soup.find_all('td')[0].get_text().strip()
                goals = player_soup.find_all('td')[3].get_text().strip()

                players.append(Player(
                    name=name,
                    goals=goals,
                    team=team_id,
                    league=league_id
                ))

    return players

# calculate win/defeat/draw data of each team
def count_team_result():

    for team_id in database.get_teams_id():
        result = database.get_team_result(team_id)
        database.update_team_result(team_id, result)

database = Database(DB_NAME)