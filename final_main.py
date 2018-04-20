from final_data import *
import plotly.plotly as py
import plotly.graph_objs as go

# ----------------------------------------------------
# class to extract different data from database
class database_select():
    def __init__(self, name):
        self.name = name

    def get_team_rank(self, country):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        country_name = country.title()

        stmt = '''
            SELECT Teams.name, Teams.points 
            FROM Teams JOIN Leagues
            ON Teams.league = Leagues.id
            WHERE Leagues.country = ?
            ORDER BY Teams.points 
        '''

        cur.execute(stmt, (country_name,))
        results = cur.fetchall()
        conn.close()
        return results

    def get_league_by_country(self, country):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        country_name = country.title()

        stmt = '''
            SELECT name 
            FROM Leagues
            WHERE Leagues.country = ?
        '''

        cur.execute(stmt, (country_name,))
        result = cur.fetchone()[0]
        conn.close()
        return result

    def get_goal_dis(self, country):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        country_name = country.title()

        stmt = '''
            SELECT Games.home_goal, Games.away_goal, COUNT(*)
            FROM Games JOIN Leagues
            ON Leagues.id = Games.league
            WHERE Leagues.country = ?
            GROUP BY Games.home_goal, Games.away_goal
            ORDER BY COUNT(*) DESC
        '''

        cur.execute(stmt, (country_name,))
        result = cur.fetchall()
        conn.close()
        return result

    def get_teams(self, country):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        country_name = country.title()

        stmt = '''
            SELECT Teams.name
            FROM Teams JOIN Leagues
            ON Leagues.id = Teams.league
            WHERE Leagues.country = ?
            ORDER BY Teams.rank 
        '''

        cur.execute(stmt, (country_name,))
        result = cur.fetchall()
        conn.close()
        return result

    def get_chart_stats(self, team_name):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        stmt = '''
            SELECT win, draw, loss
            FROM Teams 
            WHERE name = ?
        '''

        cur.execute(stmt, (team_name,))
        result = cur.fetchone()
        conn.close()
        return result

    def get_top_players(self, country):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()

        country_name = country.title()
        teams = self.get_teams(country_name)
        teams.reverse()

        stmt = '''
            SELECT Players.name as pname, 
                   Players.goals as pgoal
            FROM Players JOIN Leagues JOIN Teams
                ON Players.league = Leagues.id 
                    AND Players.team = Teams.id
            WHERE Teams.name = ?
                AND Players.id in (
                    SELECT T2.id FROM Players as T2
                    WHERE Players.team = T2.team 
                    ORDER BY t2.goals DESC 
                    LIMIT 3)   
            ORDER BY pgoal DESC
        '''

        result = {}
        for team in teams:
            cur.execute(stmt, (team[0], ))
            players = cur.fetchall()
            result[team[0]] = players

        conn.close()
        return result

db_select = database_select(DB_NAME)

# ----------------------------------------------------
## functions to plot graphs

#function to process rank command
def plot_rank(country):
    rank_result = db_select.get_team_rank(country)
    league = db_select.get_league_by_country(country)
    teams = []
    points = []
    for result in rank_result:
        teams.append(result[0])
        points.append(result[1])

    trace = go.Bar(
        y = teams,
        x = points,
        name = 'Current Season Points',
        orientation = 'h',
        width = 0.5,
        text = points,
        textposition = 'inside',
        textfont = dict(
            color = 'white'
        ),
        hoverinfo = 'y',

        marker = dict(
            color = 'rgba(221, 26, 26, 1)'
        )
    )

    layout = go.Layout(
        margin = dict(
            l = 200 ),
        title = 'Ranking of ' + league,
        xaxis=dict(
            side = 'top',
            range=[0, points[-1]+10],
            fixedrange = True ),
        yaxis=dict( 
            fixedrange = True),
        showlegend = True
    )

    data = [trace]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Ranking of ' + league)

#plot_rank('england')

# function to process goal command
def plot_goal(country):
    goal_dis = db_select.get_goal_dis(country)
    league = db_select.get_league_by_country(country)

    home = []
    away = []
    count = []
    color = []
    size = []

    for goal in goal_dis:
        home.append(goal[0])
        away.append(goal[1])
        if goal[2] == 1:
            count.append(str(goal[2]) + ' game')
        else:
            count.append(str(goal[2]) + ' games')
        color.append(goal[2]+ 150)
        size.append(goal[2] + 30)

    trace = go.Scatter(
        x=home,
        y=away,
        name = 'Goal Distribution of ' + league + ' games',
        mode='markers+text',
        text = count,
        textposition = 'inside',
        marker=dict(
            color=color,
            size=size,
        )
    )

    layout = go.Layout(
        width = 1000,
        height = 700,

        title = 'Goal Distribution of ' + league,
        xaxis=dict(
            title = 'Home Goal',
            fixedrange = True ),
        yaxis=dict( 
            title = 'Away Goal',
            fixedrange = True)
        
    )

    data = [trace]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Goal Distribution of ' + league)


#plot_goal('england')

# function to process 'list' command
def list_teams(country):
    league = db_select.get_league_by_country(country)
    teams = db_select.get_teams(country)
    print ('Teams in ' + league)
    for i, team in enumerate(teams):
        print('{}. {}'.format(i+1, team[0]))

# function to process 'chart' command
def team_chart(team_name):
    stats = db_select.get_chart_stats(team_name)

    labels = ['Win','Draw','Loss']
    values = [stats[0],stats[1],stats[2]]

    trace = go.Pie(
        labels=labels, 
        values=values,
        text = values,
        hoverinfo = 'label+value+percent',
        marker = dict(
            colors = ['#5cd177', '#ffde5b', '#ef6262']
        )
    )

    layout = go.Layout(

        title = 'Win / Draw / Loss Rate of ' + team_name,
        width = 1200,
        height = 700
    )

    data = [trace]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Team_Chart')


# function to process players command
def plot_players(country):
    player_dict = db_select.get_top_players(country)
    league = db_select.get_league_by_country(country)
    teams = []
    player1 = []
    player2 = []
    player3 = []
    goal1 = []
    goal2 = []
    goal3 = []

    for t, p in player_dict.items():
        teams.append(t)
        player1.append(p[0][0])
        goal1.append(p[0][1])

        player2.append(p[1][0])
        goal2.append(p[1][1])

        player3.append(p[2][0])
        goal3.append(p[2][1])

    trace1 = go.Scatter(
        x=goal1,
        y=teams,
        mode='markers',
        name='No.1 Player',
        text= player1,
        marker=dict(
            color='#e50000',
            symbol='circle',
            size=14
        )
    )

    trace2 = go.Scatter(
        x=goal2,
        y=teams,
        mode='markers',
        name='No.2 Player',
        text= player2,
        marker=dict(
            color='#ffd162',
            symbol='circle',
            size=14
        )
    )

    trace3 = go.Scatter(
        x=goal3,
        y=teams,
        mode='markers',
        name='No.3 Player',
        text= player3,
        marker=dict(
            color='#fbe4d2',
            symbol='circle',
            size=14
        )
    )

    layout = go.Layout(
        title="Top 3 Players of Each Team In "+league,
        xaxis=dict(
            title='Goal Numbers',
            fixedrange = True ),
        yaxis=dict(
            title='Teams',
            fixedrange = True),
        margin = dict(
            l = 200 ),
        width = 1200,
        height = 700
    )

    data = [trace1,trace2,trace3]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Top_Players')


# ----------------------------------------------------
## functions to implement command line interaction 

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    response = input ('Enter a command: (Enter "help" to see available commands) ')
    list_res = None
    countries = ['england',
                 'spain',
                 'germany',
                 'italy',
                 'france']
    while True:
        if response == 'help':
            print(help_text)

        elif response == 'exit':
            print ('Bye!')
            break

        elif response.split()[0] == 'rank':
            try:
                if response.split()[1].lower() not in countries:
                    print ('Please enter a valid country')
                else:
                    plot_rank(response.split()[1])
            except:
                print('please enter a valid command')

        elif response.split()[0] == 'goal':
            try:
                if response.split()[1].lower() not in countries:
                    print ('Please enter a valid country')
                else:
                    plot_goal(response.split()[1])
            except:
                print('please enter a valid command')
            

        elif response.split()[0] == 'players':
            try:
                if response.split()[1].lower() not in countries:
                    print ('Please enter a valid country')
                else:
                    plot_players(response.split()[1])
            except:
                print('please enter a valid command')

        elif response.split()[0] == 'list':
            try:
                if response.split()[1].lower() not in countries:
                    print ('Please enter a valid country')
                else:
                    list_res = db_select.get_teams(response.split()[1])
                    list_teams(response.split()[1])
            except:
                print('please enter a valid command')
            #continue

        elif response.split()[0] == 'chart':
            try:
                if list_res:
                    try:
                        num=int(response.split()[1])
                        team_chart(list_res[num-1][0])
                    except:
                        print ("Please enter a valid result number")
                    
                else:
                    print ("Please use the list command and list a country first")
            except:
                print('please enter a valid command')

        else:
            print('please enter a valid command')
            

        response = input ('Enter a command: ')




if __name__ == '__main__':
    # ----------------------------------------------------
    ## code to init database and collect data from web pages
    ## these functions are from final_data.py


     
    database.init()

    teams_data = get_team_data()
    database.save_teams_data(teams_data)

    games_data = get_games_data()
    database.save_games_data(games_data)

    players_data = get_players_data()
    database.save_players_data(players_data)

    count_team_result() 
    # ----------------------------------------------------

    interactive_prompt()




    










