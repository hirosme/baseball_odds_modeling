'''
Script to pull odds from oddstrader.com via BeautifulSoup. Deprecated on realization that oddstrader utilizes a dynamic
webpage that soup fails to take an image of.
'''

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def scrape_oddstrader_results(date):
    url = f'https://www.oddstrader.com/mlb/?data={date}'  # Adjust based on the actual page URL for historical odds
    response = requests.get(url)
    print(url)
    if response.status_code != 200:
        print(f"Failed to fetch OddsTrader page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    # Initialize list to store the data
    game_data = []

    teams = soup.find_all('tr', {'data-cy': 'participant-row'})  # Adjust the class or tag if needed
    print(len(teams))
    home = 0
    for team in teams:
        try:
            # Extract team names (home and away)
            # print(team.find_all('div', {'class': 'event-cell__name'})[0])
            if home == 0:
                away_team = team.find_all('span', {'class': 'teamName'})[0].text.strip()
                away_odds = team.find_all('td', {'data-cy':'odds-row-container'})[
                    -1].text.strip()
                away_win_pct = convert_odds_to_pct(int(away_odds[1:]))
                home = 1
            else:
                # print(1)
                home_team = team.find_all('span', {'class': 'teamName'})[0].text.strip()
                home_odds = team.find_all('td', {'data-cy':'odds-row-container'})[
                    -1].text.strip()
                home_win_pct = convert_odds_to_pct(int(home_odds[1:]))
                game_data.append([home_team, away_team, home_win_pct, away_win_pct])
                home = 0
        except (AttributeError, IndexError):
            continue  # Skip rows that don't match the expected structure

    # Create a DataFrame
    df = pd.DataFrame(game_data, columns=['home_team', 'away_team', 'home_odds', 'away_odds'])

    return df

# Function to convert American odds to probability
def convert_odds_to_pct(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return -odds / (-odds + 100)

today_date = datetime.today().strftime('%Y-%m-%d')
# Run the function
print(scrape_oddstrader_results(today_date))
