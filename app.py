import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Video Game Sales Dashboard",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Video Game Sales Dashboard")
st.markdown("### Video Game Sales Analysis")

# Load Dataset
@st.cache_data
def load_data():
    df = pd.read_csv("vgsales.csv")
    df["Year"] = df["Year"].fillna(0).astype("int64")
    df["Publisher"] = df["Publisher"].fillna("Unknown")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset not found. Please check the CSV file path.")
    st.stop()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Sidebar Filters
st.sidebar.header("Dashboard Filters")

platforms = sorted(df["Platform"].dropna().unique())
genres = sorted(df["Genre"].dropna().unique())

platform = st.sidebar.multiselect(
    "Select Platform",
    platforms,
    default=platforms
)

genre = st.sidebar.multiselect(
    "Select Genre",
    genres,
    default=genres
)

data = df[
    df["Platform"].isin(platform) &
    df["Genre"].isin(genre)
].copy()

if data.empty:
    st.warning("No data available. Please select a platform and genre.")
    st.stop()

# Outlier Removal
if st.sidebar.checkbox("Remove Outliers"):
    for i in ["NA_Sales", "EU_Sales", "JP_Sales"]:
        q1 = data[i].quantile(0.25)
        q3 = data[i].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        data = data[
            data[i].between(lower, upper)
        ]

    if data.empty:
        st.warning("No records remain after outlier removal.")
        st.stop()

# Dashboard Metrics
st.header("📊 Dashboard Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Games", len(data))
c2.metric("Platforms", data["Platform"].nunique())
c3.metric("Genres", data["Genre"].nunique())
c4.metric("Global Sales", f"{data['Global_Sales'].sum():,.2f} M")

# Dataset
st.header("📁 Dataset Overview")
st.dataframe(data, use_container_width=True)

c1, c2 = st.columns(2)

with c1:
    st.subheader("Missing Values")
    st.dataframe(data.isnull().sum().to_frame("Missing Values"))

with c2:
    st.subheader("Data Types")
    st.dataframe(data.dtypes.astype(str).to_frame("Data Types"))

st.subheader("Statistical Summary")
st.dataframe(data.describe(), use_container_width=True)

# Regional Sales
st.header("🌎 Regional Sales Analysis")

c1, c2 = st.columns(2)

with c1:
    fig, ax = plt.subplots()
    sb.histplot(data["NA_Sales"], kde=True, ax=ax)
    ax.set_title("North America Sales")
    st.pyplot(fig)
    plt.close(fig)

with c2:
    fig, ax = plt.subplots()
    sb.histplot(data["EU_Sales"], kde=True, ax=ax)
    ax.set_title("Europe Sales")
    st.pyplot(fig)
    plt.close(fig)

fig, ax = plt.subplots()
sb.boxplot(
    data=data[["NA_Sales", "EU_Sales", "JP_Sales"]],
    ax=ax
)
ax.set_title("Regional Sales Boxplot")
st.pyplot(fig)
plt.close(fig)

# Platform Analysis
st.header("🎮 Platform Analysis")

platform_sales = data.groupby(
    "Platform"
)["Global_Sales"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 5))
sb.barplot(x=platform_sales.index, y=platform_sales.values, ax=ax)
ax.set_title("Platform-wise Global Sales")
ax.set_ylabel("Global Sales (Millions)")
ax.tick_params(axis="x", rotation=90)
st.pyplot(fig)
plt.close(fig)

st.dataframe(platform_sales.to_frame("Global Sales"))

# Genre Analysis
st.header("🎯 Genre Analysis")

genre_sales = data.groupby(
    "Genre"
)["Global_Sales"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 5))
sb.barplot(x=genre_sales.index, y=genre_sales.values, ax=ax)
ax.set_title("Genre-wise Global Sales")
ax.set_ylabel("Global Sales (Millions)")
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)
plt.close(fig)

st.dataframe(genre_sales.to_frame("Global Sales"))

# Publisher Analysis
st.header("🏢 Publisher Analysis")

publisher_sales = data.groupby(
    "Publisher"
)["Global_Sales"].sum().nlargest(10)

fig, ax = plt.subplots(figsize=(12, 5))
sb.barplot(
    x=publisher_sales.values,
    y=publisher_sales.index,
    ax=ax
)
ax.set_title("Top 10 Publishers")
st.pyplot(fig)
plt.close(fig)

st.dataframe(publisher_sales.to_frame("Global Sales"))

# Regional Comparison
st.header("📈 Regional Sales Comparison")

regional_sales = data[
    ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
].sum()

fig, ax = plt.subplots()
sb.barplot(
    x=regional_sales.index,
    y=regional_sales.values,
    ax=ax
)
ax.set_title("Total Sales by Region")
st.pyplot(fig)
plt.close(fig)

# Top Selling Games
st.header("🏆 Top 10 Selling Games")

st.dataframe(
    data.sort_values(
        "Global_Sales",
        ascending=False
    ).head(10),
    use_container_width=True
)

# Download
st.download_button(
    "⬇️ Download Cleaned Dataset",
    data.to_csv(index=False).encode("utf-8"),
    file_name="vgsales_cleaned.csv",
    mime="text/csv"
)

st.markdown("---")
st.success("Dashboard Loaded Successfully!")
st.caption("Developed using Python, Pandas, NumPy, Seaborn and Streamlit")
