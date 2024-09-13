'''
Script to pull odds from draftkings.com. Deprecated upon discovery that site does not provide historical data
'''

import requests
from bs4 import BeautifulSoup
import pandas as pd


def scrape_draftkings_odds():
    url = 'https://sportsbook.draftkings.com/leagues/baseball/mlb'  # DraftKings MLB page URL
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch DraftKings page. Status code: {response.status_code}")
        return None

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize list to store game data
    game_data = []

    # Find all rows that represent games
    today = soup.find('tbody',{'class':'sportsbook-table__body'})
    #print(today)
    teams = soup.find_all('tr')  # Adjust the class or tag if needed
    #print(len(teams))
    home = 0
    for team in teams:
        try:
            # Extract team names (home and away)
            #print(team.find_all('div', {'class': 'event-cell__name'})[0])
            if home == 0:
                away_team = team.find_all('div', {'class': 'event-cell__name-text'})[0].text.strip()[3:]
                away_odds = team.find_all('span', {'class': 'sportsbook-odds american no-margin default-color'})[0].text.strip()
                away_win_pct = convert_odds_to_pct(float_unicode(away_odds))
                home = 1
            else:
                #print(1)
                home_team = team.find_all('div', {'class': 'event-cell__name-text'})[0].text.strip()[3:]
                home_odds = team.find_all('span', {'class': 'sportsbook-odds american no-margin default-color'})[0].text.strip()
                home_win_pct = convert_odds_to_pct(float_unicode(home_odds))
                game_data.append([home_team, away_team, home_win_pct, away_win_pct])
                home = 0

        except (AttributeError, IndexError):
            continue  # Skip rows that don't match the expected structure

    # Convert to DataFrame
    df = pd.DataFrame(game_data, columns=['home_team', 'away_team', 'home_win_pct', 'away_win_pct'])

    return df


# Function to convert American odds to probability
def convert_odds_to_pct(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return -odds / (-odds + 100)

def float_unicode(arg_str):
    return float(arg_str.replace(u"\u2212", "-"))
#print(float_unicode('−298'))
# Test the function
draftkings_df = scrape_draftkings_odds()
#print(df)
