import os
import pandas as pd
from datetime import datetime


def convert_date_format(date_str):
    # Parse the input date (MM/DD/YYYY)
    date_obj = datetime.strptime(date_str, "%m/%d/%Y")
    # Convert to YYYY-MM-DD
    return date_obj.strftime("%Y-%m-%d")


# Define the dates used in the original script
startDate = "3/1/2025"
endDate = "4/17/2025"

# Construct the CSV filename
downloads_path = os.path.expanduser("~/Downloads")  # Default Downloads folder
start_date_str = convert_date_format(startDate)
end_date_str = convert_date_format(endDate)
csv_file_name = f"Hitting_{start_date_str}_to_{end_date_str}.csv"
csv_file_path = os.path.join(downloads_path, csv_file_name)

try:
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_file_path)
    print("CSV file loaded into DataFrame")
    print("DataFrame preview:")
    # print(df.head())

    # Remove NameASCII, PlayerId, and MLBAMID columns
    columns_to_remove = ['NameASCII', 'PlayerId', 'MLBAMID']
    existing_columns = [col for col in columns_to_remove if col in df.columns]
    if existing_columns:
        df = df.drop(existing_columns, axis=1)
        print(f"Removed columns: {existing_columns}")

    # Get an array of column names as strings
    column_names = df.columns.tolist()
    print("Column names:", column_names)

    # Remove rows where PA < 10
    initial_rows = len(df)
    df = df[df['PA'] >= 10]
    print(f"Removed {initial_rows - len(df)} rows where PA < 10")
    print(f"Remaining rows: {len(df)}")

    print("Updated DataFrame preview:")
    print(df.head())

    cleaned_csv = os.path.join(os.path.dirname(
        __file__), f"cleaned_hitting_{start_date_str}_to_{end_date_str}.csv")
    df.to_csv(cleaned_csv, index=False)
    print(f"Cleaned data saved to: {cleaned_csv}")

    # Reorder columns to have Team precede Name
    cols = df.columns.tolist()
    cols.remove('Team')
    cols.remove('Name')
    new_cols = ['Team', 'Name'] + [col for col in cols]
    df = df[new_cols]

    # Sort rows by Team in alphabetical order
    df = df.sort_values(by='Team', ascending=True)

    # Assuming df is your DataFrame from the CSV
    # Select only numeric columns to normalize
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

    # Columns to invert normalization
    invert_cols = ['BABIP+', 'Soft%+', 'K%+', 'O-Swing%', 'SwStr%']

    # Apply Z-score normalization
    for col in numeric_cols:
        if col == 'PA':
            continue  # Skip PA
        if col in invert_cols:
            df[col] = -1 * (df[col] - df[col].mean()) / \
                df[col].std()  # Inverted normalization
        else:
            df[col] = (df[col] - df[col].mean()) / \
                df[col].std()  # Regular normalization

    # Truncate all data to 4 decimals
    df = df.round(4)

    print("Normalized DataFrame preview:")
    print(df.head())

    norm_csv = os.path.join(os.path.dirname(
        __file__), f"norm_hitting_{start_date_str}_to_{end_date_str}.csv")
    df.to_csv(norm_csv, index=False)
    print(f"Normalized data saved to: {norm_csv}\n")

    names = df[['Team', 'Name']]

    names_csv = os.path.join(os.path.dirname(
        __file__), f"names_{start_date_str}_to_{end_date_str}.csv")
    names.to_csv(names_csv, index=False)
    print(f"Batter Names saved to: {names_csv}\n")


except FileNotFoundError:
    print(f"Error: File not found at {csv_file_path}")
except Exception as e:
    print(f"An error occurred: {e}")

    # # Create roster array
    # # Get unique teams in alphabetical order
    # roster = {team: df[df['Team'] == team]['Name'].tolist()
    #           for team in sorted(df['Team'].unique())}

    # # for team, players in roster.items():
    # #     print(f"{team}: {players}")
