'''
Updated oddstrader script utilizing selenium (with 1s delay) to pull vegas odds from oddstrader.com for a given day.
Returns the sportsbook and odds from the book that gives the best deal.
'''

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime, timedelta

# today = datetime.today().strftime('%Y-%m-%d')
# yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

def scrape_oddstrader_results(date):
    url = f'https://www.oddstrader.com/mlb/?date={date}'

    # Set up the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Load the webpage
    driver.get(url)

    # Initialize list to store data
    game_data = []
    time.sleep(1)

    # Find all the game containers
    teams = driver.find_elements(By.CSS_SELECTOR, 'tr[data-cy="participant-row"]')

    home = 0
    for team in teams:
        try:
            if home == 0:
                away_team = team.find_element(By.CSS_SELECTOR, 'span.teamName').text.strip()
                away_odds = team.find_element(By.CSS_SELECTOR, 'span.best-line').text.strip()
                away_sportsbook = team.find_element(By.CSS_SELECTOR, 'span.subtitle').text.strip()
                # print(away_team)
                # print(away_odds)
                # print(away_sportsbook)
                away_win_pct = convert_odds_to_pct(int(away_odds))
                home = 1
            else:
                home_team = team.find_element(By.CSS_SELECTOR, 'span.teamName').text.strip()
                home_odds = team.find_element(By.CSS_SELECTOR, 'span.best-line').text.strip()
                home_sportsbook = team.find_element(By.CSS_SELECTOR, 'span.subtitle').text.strip()
                # print(home_team)
                # print(home_odds)
                # print(home_sportsbook)
                home_win_pct = convert_odds_to_pct(int(home_odds))
                game_data.append(
                    [home_team, away_team, home_sportsbook, home_odds, home_win_pct,away_sportsbook, away_odds,
                     away_win_pct])
                home = 0
        except Exception as e:
            print(f"Error: {e}")
            continue

    # Create a DataFrame
    df = pd.DataFrame(game_data,
                      columns=['home_team', 'away_team', 'home_sportsbook', 'home_odds', 'home_win_pct', 'away_sportsbook',
                               'away_odds', 'away_win_pct'])
    df['home_team'] = df['home_team'].map(team_mapping)
    df['away_team'] = df['away_team'].map(team_mapping)

    # Quit the driver
    driver.quit()

    return df

team_mapping = {
    'AZ': 'Diamondbacks',
    'ATL': 'Braves',
    'BAL': 'Orioles',
    'BOS': 'RedSox',
    'CHC': 'Cubs',
    'CWS': 'WhiteSox',
    'CIN': 'Reds',
    'CLE': 'Guardians',
    'COL': 'Rockies',
    'DET': 'Tigers',
    'HOU': 'Astros',
    'KC': 'Royals',
    'LAA': 'Angels',
    'LAD': 'Dodgers',
    'MIA': 'Marlins',
    'MIL': 'Brewers',
    'MIN': 'Twins',
    'NYM': 'Mets',
    'NYY': 'Yankees',
    'OAK': 'Athletics',
    'PHI': 'Phillies',
    'PIT': 'Pirates',
    'SD': 'Padres',
    'SEA': 'Mariners',
    'SF': 'Giants',
    'STL': 'Cardinals',
    'TB': 'Rays',
    'TEX': 'Rangers',
    'TOR': 'BlueJays',
    'WSH': 'Nationals'
}


# Function to convert American odds to probability
def convert_odds_to_pct(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return -odds / (-odds + 100)


def float_unicode(arg_str):
    return float(arg_str.replace(u"\u2212", "-"))
# Get today's date and run the function
# today_date = datetime.today().strftime('%Y-%m-%d')
#df = scrape_oddstrader_results(yesterday).to_string()
#print(df)