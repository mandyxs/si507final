# Mandy Shen's Final Project

This program crawls soccer data from html pages and displays analysis on plotly graphs

## Data Source: http://www.soccerstats.com/
* The program crawls 100+ pages from this source, it will take a while to crawl
* If you crawl all of them at the same time the website may go down (this happened when I crawled the pages, not sure if I was the reason that the site was down)

## Plotly API
* This programs uses 4 graphs on Plotly, you will need to have Plotly installed and an API key in order to access the graphs. Please visit this link: https://plot.ly/python/getting-started/ to setup Plotly

## Code Walkthrough

### final_data.py
This is the file that handles all the crawling and inserting data into database
* class Database: this class includes methods needed to init the data base as well as inserting html data into database
* functions start with 'get': these functions crawls html pages and extracts useful data from html content

### final_main.py
This is the file that you would run to interact with the program. This file calls all the functions in final_data.py. It also manages all the command line interactions as well as plotly functions. 
* class databse_select: this is the class that has all the methods needed to analyze and select data from the database to implemenet the plotly functions
* functions plot_rank & plot_goal & team_chart & plot_player: these are the functions that generate plotly graphs
* function interactive_prompt: this is the function that implements command line interaction

### final_unittest.py
Unittest file

## User Guide
Run the final_main.py file to interact with the program. 
Here are the possible commands: (you can enter 'help' in the command line to see these instructions)

-------------------------------
rank

	What it does: Shows a bar chart of team ranking with 
	each team’s score in a specific league

	Param:
		* <country> (England / Spain / Germany / Italy / France)
		Description: Specifies the country of the league that 
		you want to see
		Default: no default, please input 1 and only 1 country name

	Example: rank Germany

-------------------------------

goal

	What it does: Show a bubble chart of home/away goal 
	distribution of all the games in current season in a 
	specific league

	Param:
		* <country> (England / Spain / Germany / Italy / France)
		Description: Specifies the country of the league 
		that you want to see
		Default: no default, please input 1 and only 1 country name

	Example: goal Germany

-------------------------------

list

	What it does: returns a list of team names in a league

	Param:
		* <country> (England / Spain / Germany / Italy / France)
		Description: Specifies the country of the league that 
		you want to see
		Default: no default, please input 1 and only 1 country name

	Example: list Germany

	---------------------------

	Sub-command:

		chart

			Available only when there is an active list 
			result of teams
			What it does: Shows a pie chart of win/draw/loss 
			rate of a specific team

			Param:
			* <result_number> (the result number of the 
			team returned to your 'list' command)

			Example: chart 1

-------------------------------

players

	What it does: Shows a dot plot of top 3 players' goal number 
	distruibution of each team in a league

	Param:
		* <country> (England / Spain / Germany / Italy / France)
		Description: Specifies the country of the league that 
		you want to see
		Default: no default, please input 1 and only 1 country name

	Example: players Germany

-------------------------------

exit
 
 	What it does: exit the program

-------------------------------
