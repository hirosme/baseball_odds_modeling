'''
Script to pull mlb game results for a given day through fangraphs scoreboard page
'''

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime, timedelta

def scrape_fangraphs_results(date):
    # Set up the Selenium WebDriver
    driver = webdriver.Chrome()

    # Get the previous day's date
    #previous_day = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # Construct the URL for Fangraphs live scoreboard for the previous day
    url = f'https://www.fangraphs.com/scoreboard.aspx?date={date}'
    #print(url)

    # Use Selenium to open the URL
    driver.get(url)
    time.sleep(1)

    # Initialize list to store results
    game_results = []

    # Find the relevant elements containing the game info
    games = driver.find_elements(By.CSS_SELECTOR, 'text.highcharts-title')
    #print(len(games))

    for game in games:
        try:
            # Extract text from the tspan, e.g., "9/3/2024 - Dodgers(6) @ Angels(2)"
            game_info = game.text.strip()

            # Extract teams and scores
            game_details = game_info.split(" - ")[1]
            teams_scores = game_details.split(" @ ")

            home_team, home_score = teams_scores[1].split("(")
            away_team, away_score = teams_scores[0].split("(")

            home_score = int(home_score[:-1])  # Remove closing parenthesis
            away_score = int(away_score[:-1])  # Remove closing parenthesis

            # Determine if home team won
            home_team_win = int(home_score > away_score)

            # Append to results
            game_results.append([home_team.strip(), away_team.strip(), home_team_win])

        except (AttributeError, IndexError):
            continue  # Skip games that don't match the expected structure

    # Close the browser
    driver.quit()

    # Create a DataFrame
    df = pd.DataFrame(game_results, columns=['home_team', 'away_team', 'home_team_win'])
    df['home_team'] = df['home_team'].str.replace(r'\s+', '', regex=True)
    df['away_team'] = df['away_team'].str.replace(r'\s+', '', regex=True)

    return df

# Run the function
#print(scrape_fangraphs_results())
