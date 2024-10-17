import pandas as pd
from sqlalchemy import create_engine

df_temp = pd.read_csv('new_data_100.csv')

# Create a SQLAlchemy engine
# Format: 'mysql+pymysql://<username>:<password>@<host>:<port>/<database>'
engine = create_engine('mysql+pymysql://root:Virupict#123@localhost:3306/news')

# Define a maximum length for the 'full_content' column (for example, 65535 characters for TEXT)
max_length = 65535

# Filter the DataFrame to exclude rows where 'full_content' exceeds the maximum length
df_filtered = df_temp[df_temp['full_content'].str.len() <= max_length]

# Write the filtered DataFrame to the SQL table
df_filtered.to_sql('api_article', con=engine, if_exists='append', index=False)

print("Data loaded successfully!")