import pandas as pd
import re
from table_scraper import get_table_by_caption

def convert_discount_rates_to_float(df):
    """
    Convert discount rate to float and account for wiki formatting.
    Adjusts for footnotes etc.
    """
    df['rate'] = (df['rate'].apply(
        lambda x: float(re.search(r'[\d.]+', x).group())
    )) / 100

    return df

def determine_fomc_action(x):
    
    # Determines if fomc decision was a cut, hike, or hold.
    
    if pd.isna(x):
        return None
    elif x > 0:
        return 'hike'
    elif x < 0:
        return 'cut'
    else:
        return 'hold'
    
def validation_checks(df):
   
    # Check if df is a DataFrame
    assert isinstance(df, pd.DataFrame), "Input is not a DataFrame"

    # Check required columns are present
    required_columns = ['date', 'fed_band', 'rate', 'shift', 'action']
    for col in required_columns:
        assert col in df.columns, f"Missing expected column: {col}"

    # Check correct dtypes
    expected_dtypes = {
        'date': 'datetime64[ns]',
        'fed_band': 'object',
        'rate': 'float64',
        'shift': 'float64',
        'action': 'object'
    }
    for col, expected_type in expected_dtypes.items():
        actual_type = str(df[col].dtype)
        assert actual_type == expected_type, \
                 f"Column '{col}' has dtype '{actual_type}',expected '{expected_type}'"
        
    # Check appropriate actions
    assert set(df['action'].unique()) <= {'cut', 'hold', 'hike'}, \
        "Unexpected values in 'action'"

def save_fomc_actions(df, file_path = 'data/fomc_actions.csv'):
    
    # Name file and save as csv in VolkerBot
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"FOMC actions saved to {file_path}")

def fetch_fomc_action():
    """
    Main function that pulls data from wikipedia, cleans it, and saves the data
    in VolkerBot\Data.
    """

    #These are the instructions for the dynamic table search 
    url = 'https://en.wikipedia.org/wiki/History_of_Federal_Open_Market_Committee_actions'
    caption = "FOMC Federal Funds Rate History"
    
    df = get_table_by_caption(url, caption)

    # format dataframe.
    df = df.rename(columns={
        'Date':'date',
        'Fed. Funds Rate':'fed_band',
        'Discount Rate':'rate',
        'Votes':'votes',
        'Notes':'notes'
    })
    df = df.astype({'date':'datetime64[ns]'})
    df = convert_discount_rates_to_float(df)
    df = df.drop(columns=['notes', 'votes'])

    # Determine FOMC action.
    df['shift'] = df['rate'].diff(periods=-1)
    df['action'] = df['shift'].apply(determine_fomc_action)
    df = df.dropna()

    # Save data as csv in VolkerBot\data
    validation_checks(df)
    save_fomc_actions(df)


if __name__ == '__main__':
    fetch_fomc_action()