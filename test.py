from datetime import datetime

# Get today's date
today = datetime.now()
formatted_date = f"{today.month}/{today.day}/{today.year}"
print(formatted_date)  # Outputs: 4/17/2025 (if today is April 17, 2025)
