import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

st.set_page_config(page_title="Video Game Sales Analysis", layout="wide")

st.title("🎮 Video Game Sales Analysis")

df = pd.read_csv('vgsales.csv')

# Data Cleaning
df['Year'] = df.Year.fillna(0)
df['Publisher'] = df.Publisher.fillna('Unknown')
df.Year = df.Year.astype('int64')

# Sidebar Filters
st.sidebar.header("Filters")

platform = st.sidebar.multiselect(
    "Select Platform",
    df.Platform.unique(),
    default=df.Platform.unique()
)

genre = st.sidebar.multiselect(
    "Select Genre",
    df.Genre.unique(),
    default=df.Genre.unique()
)

df = df[
    (df.Platform.isin(platform)) &
    (df.Genre.isin(genre))
].copy()

# Outlier Removal
if st.sidebar.checkbox("Remove Outliers"):

    for i in ['NA_Sales', 'EU_Sales', 'JP_Sales']:

        q1 = np.percentile(df[i], 25)
        q3 = np.percentile(df[i], 75)

        iqr = q3 - q1

        c1 = q1 - 1.5 * iqr
        c2 = q3 + 1.5 * iqr

        df = df[(df[i] >= c1) & (df[i] <= c2)]

# Dataset Overview
st.header("Dataset Overview")

st.write("Total Records:", len(df))
st.write("Total Columns:", len(df.columns))

st.dataframe(df)

st.subheader("Columns")
st.write(df.columns)

st.subheader("Data Types")
st.write(df.dtypes)

st.subheader("Missing Values")
st.write(df.isnull().sum())

st.subheader("Statistical Summary")
st.write(df.describe())

# Regional Sales Analysis
st.header("Regional Sales Analysis")

p = df.groupby('Platform')[['NA_Sales', 'EU_Sales', 'JP_Sales']].sum()

g = df.groupby('Genre')[['NA_Sales', 'EU_Sales', 'JP_Sales']].sum()

fig, ax = plt.subplots()
sb.histplot(df[['NA_Sales', 'EU_Sales', 'JP_Sales']], ax=ax)
st.pyplot(fig)
plt.close(fig)

fig, ax = plt.subplots()
sb.boxplot(data=df[['NA_Sales', 'EU_Sales', 'JP_Sales']], ax=ax)
st.pyplot(fig)
plt.close(fig)

# Outlier Analysis
st.subheader("Sales After Outlier Removal")

fig, ax = plt.subplots()
sb.boxplot(data=df[['NA_Sales', 'EU_Sales', 'JP_Sales']], ax=ax)
st.pyplot(fig)
plt.close(fig)

# Global Sales Analysis
st.header("Global Sales Analysis")

st.write("Total Global Sales:", df['Global_Sales'].sum())

st.subheader("Platform-wise Global Sales")

s = df.groupby('Platform')['Global_Sales'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 5))
sb.barplot(x=s.index, y=s.values, ax=ax)
plt.xticks(rotation=90)
st.pyplot(fig)
plt.close(fig)

st.subheader("Genre-wise Global Sales")

y = df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 5))
sb.barplot(x=y.index, y=y.values, ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)
plt.close(fig)

# Year Analysis
st.header("Year Analysis")

st.write(df.groupby('Genre')['Year'].sum())

# Publisher Analysis
st.header("Publisher Analysis")

st.subheader("Top 10 Publishers")

publisher = df.groupby('Publisher')['Global_Sales'].sum().nlargest(10)

st.write(publisher)

fig, ax = plt.subplots(figsize=(12, 5))
sb.barplot(x=publisher.values, y=publisher.index, ax=ax)
st.pyplot(fig)
plt.close(fig)

# Regional Sales Comparison
st.header("Regional Sales Comparison")

a = df[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].agg('sum')

fig, ax = plt.subplots()
sb.barplot(x=a.index, y=a.values, ax=ax)
st.pyplot(fig)
plt.close(fig)

st.write(a)

# Top Selling Games
st.header("Top Selling Games")

st.dataframe(
    df.sort_values('Global_Sales', ascending=False)
)

# Regional Sales Sorting
st.header("Regional Sales Sorting")

st.dataframe(
    df.sort_values(
        ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'],
        ascending=False
    )
)

# Download Dataset
st.download_button(
    "Download CSV",
    df.to_csv(index=False),
    "vgsales_cleaned.csv",
    "text/csv"
)


       
    

    
  
   
