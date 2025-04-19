# app.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Load data from SQL database
engine = create_engine('sqlite:///redbus_data.db')
df = pd.read_sql_table('bus_routes', con=engine)

st.title("Redbus Data Filtering Application")

# Filters for user input
bustype_filter = st.selectbox("Select Bus Type:", options=df['bustype'].unique())
price_range = st.slider("Select Price Range:", min_value=int(df['price'].min()), max_value=int(df['price'].max()), value=(int(df['price'].min()), int(df['price'].max())))
star_rating_filter = st.selectbox("Select Star Rating:", options=[0] + sorted(df['star_rating'].unique().tolist()))

# Apply filters to the DataFrame
filtered_df = df[(df['bustype'] == bustype_filter) & 
                  (df['price'] >= price_range[0]) & 
                  (df['price'] <= price_range[1])]

if star_rating_filter > 0:
    filtered_df = filtered_df[filtered_df['star_rating'] >= star_rating_filter]

# Display filtered results
st.write("Filtered Bus Results:")
st.dataframe(filtered_df)

# Optionally allow download of filtered results as CSV
if st.button("Download Filtered Results"):
    filtered_df.to_csv('filtered_results.csv', index=False)
    st.success("Filtered results downloaded as filtered_results.csv")
