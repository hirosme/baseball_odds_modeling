'''
Script to pull win probability statistics for a given date from fangraphs live scoreboard page
'''

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd


def scrape_fangraphs_odds(date):
    # Construct today's URL
    url = f'https://www.fangraphs.com/livescoreboard.aspx?date={date}'

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch Fangraphs page. Status code: {response.status_code}")
        return None

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize list to store game data
    game_data = []

    # Find all relevant divs and tables for game information
    games = soup.find_all('td', style=lambda x: x and 'text-align:center' in x)

    for game in games:
        try:
            # Extract team names (home and away)
            teams = game.find_all('b')
            home_team = teams[1].text.strip()
            away_team = teams[0].text.strip()

            # Extract win probabilities
            win_probs = game.find_next('table').find_all('td')
            home_win_pct = float(win_probs[1].text.strip('%'))
            away_win_pct = float(win_probs[0].text.strip('%'))

            game_data.append([home_team, away_team, home_win_pct/100, away_win_pct/100])

        except AttributeError:
            continue  # Skip rows that don't match the expected structure

    # Convert to DataFrame
    df = pd.DataFrame(game_data, columns=['home_team', 'away_team', 'home_win_pct', 'away_win_pct'])
    df['home_team'] = df['home_team'].str.replace(r'\s+', '', regex=True)
    df['away_team'] = df['away_team'].str.replace(r'\s+', '', regex=True)
    return df


# Test the function
#fangraphs_df = scrape_fangraphs_odds()
#print(fangraphs)
