from oddstrader_selenium import *
from fangraphs_scrape import *
from mlb import *
import pandas as pd
from datetime import datetime, timedelta

today = datetime.today().strftime('%Y-%m-%d')
yesterday = (datetime.today() - timedelta(days=186)).strftime('%Y-%m-%d')

## function to generate df with odds data for a given date
def daily_odds(date):
    try:
        oddstrader_df = scrape_oddstrader_results(date)
        fangraphs_df = scrape_fangraphs_odds(date)
        results_df = scrape_fangraphs_results(date)

        df1 = pd.merge(
            fangraphs_df,
            oddstrader_df,
            on=['home_team', 'away_team'],
            how='left',
            suffixes=('_fangraphs', '_oddstrader')
        )
        df = pd.merge(
            df1,
            results_df,
            on=['home_team', 'away_team'],
            how='left',
        ).dropna()


        df['home_diff'] = df['home_win_pct_fangraphs'] - df['home_win_pct_oddstrader']
        df['away_diff'] = df['away_win_pct_fangraphs'] - df['away_win_pct_oddstrader']
        df['home_ev'] = df.apply(lambda row: calculate_ev(row['home_odds'],row['home_win_pct_fangraphs']),axis=1)
        df['away_ev'] = df.apply(lambda row: calculate_ev(row['away_odds'],row['away_win_pct_fangraphs']),axis=1)
        df['home_payout'] = df['home_odds'].apply(calculate_payoff)
        df['away_payout'] = df['away_odds'].apply(calculate_payoff)
        return df
    except Exception as e:
        return pd.DataFrame()

## function to calculate payoff of a $1 bet hitting given posted odds
def calculate_payoff(odds):
    odds = int(odds)
    if odds > 0:
        return odds / 100
    else:
        return 100 / abs(odds)

## function to calculate expected value of placing a $1 bet with a certain estimated probability of hitting
## given posted odds
def calculate_ev(odds, probability):
    #print(odds)
    odds = int(odds)
    #print(odds)
    # Convert American odds to decimal odds for positive and negative values
    if odds > 0:
        profit_if_win = odds / 100
    else:
        profit_if_win = 100 / abs(odds)

    # Calculate probability of failure
    probability_of_failure = 1 - probability

    # Calculate EV for a $1 bet
    ev = (probability * profit_if_win) - (probability_of_failure * 1)

    return ev

## given an odds df, calculates profit of placing $1 bets on all games where model win pct exceeds vegas win pct by
## more than a certain threshold
def strategy_prob_dif(df,threshold):
    investment = 0
    profit = 0
    for i in range(len(df)):
        if df['home_diff'].iloc[i] >= threshold:
            investment += 1
            if df['home_team_win'].iloc[i] == 1:
                profit += df['home_payout'].iloc[i]
            else:
                profit += -1

        if df['away_diff'].iloc[i] >= threshold:
            investment += 1
            if df['home_team_win'].iloc[i] == 0:
                profit += df['away_payout'].iloc[i]
            else:
                profit += -1
    print('$' + str(profit) + ' on $' + str(investment) + ' investment')
    return profit

## given an odds df, calculates profit of placing $1 bets on all games where based on model win pct, estimated EV of
## a $1 bet is above a certain threshold
def strategy_ev(df,threshold):
    investment = 0
    profit = 0
    for i in range(len(df)):
        if df['home_ev'].iloc[i] >= threshold:
            investment += 1
            if df['home_team_win'].iloc[i] == 1:
                profit += df['home_payout'].iloc[i]
            else:
                profit += -1

        if df['away_ev'].iloc[i] >= threshold:
            investment += 1
            if df['home_team_win'].iloc[i] == 0:
                profit += df['away_payout'].iloc[i]
            else:
                profit += -1
    print('$'+str(profit)+' on $'+str(investment)+' investment')
    return profit

## generates an odds df containing all games in the past n days and writes to a csv
def historic_data_gen(n):
    df_list = []
    for i in range(n):
        print('day: '+str(i)+'/'+str(n))
        day = (datetime.today() - timedelta(days=i + 1)).strftime('%Y-%m-%d')
        day_df = daily_odds(day)  # Assuming daily_odds() is defined elsewhere
        #print(len(day_df))
        if not day_df.empty:
            df_list.append(day_df)  # Append each day's DataFrame to the list

    # Concatenate all DataFrames in the list
    final_df = pd.concat(df_list, ignore_index=True)
    #print(len(final_df))
    #print(final_df.to_string())
    # Save the final DataFrame to a CSV file
    filename = 'odds_data_' + str(n) + '.csv'
    final_df.to_csv(filename, index=False)

#historic_data_gen(160)
#df = daily_odds(yesterday)
#print(df)
df = pd.read_csv('odds_data_100.csv')
strategy_prob_dif(df,.1)
strategy_ev(df,.1)