import pandas as pd


Advertising_Email_Deliveries = '/Users/prasanthbalaji/desktop/MCCS-Project Files/Advertising_Email_Deliveries_2024.xlsx'
Advertising_Email_Performance = '/Users/prasanthbalaji/desktop/MCCS-Project Files/Advertising_Email_Performance_2024.xlsx'
Advertising_Email_Engagement = '/Users/prasanthbalaji/desktop/MCCS-Project Files/Advertising_Email_Engagement_2024.xlsx'
Social_Media_Performance = '/Users/prasanthbalaji/desktop/MCCS-Project Files/Social_Media_Performance_2024.xlsx'

Advertising_Email_Deliveries_df = pd.read_excel(Advertising_Email_Deliveries, sheet_name='Email Deliveries Details', skiprows=4, skipfooter=1, engine='openpyxl')
Advertising_Email_Performance_df = pd.read_excel(Advertising_Email_Performance, sheet_name='Email Performance Email Sends T', skiprows=4, skipfooter=1, engine='openpyxl')
Advertising_Email_Engagement_df = pd.read_excel(Advertising_Email_Engagement, sheet_name='Email Engagement Details', skiprows=4, skipfooter=1, engine='openpyxl')
Social_Media_Performance_df = pd.read_excel(Social_Media_Performance, sheet_name    ='Post Engagement Scorecard', skiprows=2, skipfooter=1, engine='openpyxl')
print("Data from 'Advertising_Email_Deliveries':")
print(Advertising_Email_Deliveries_df.head())
print("Data from 'Advertising_Email_Performance':")
print(Advertising_Email_Performance_df.head())
print("Data from 'Advertising_Email_Engagement':")
print(Advertising_Email_Engagement_df.head())
print("Data from 'Social_Media_Performance':")
print(Social_Media_Performance_df.head())