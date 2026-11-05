import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="Video Game Sales Analysis",
    page_icon="🎮",
    layout="wide"
)

# Title
st.title("🎮 Video Game Sales Analysis")
st.write("Interactive dashboard for analyzing video game sales across different regions.")

# Load Dataset
uploaded_file = st.sidebar.file_uploader(
    "Upload Video Game Sales CSV",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("vgsales.csv")
    except FileNotFoundError:
        st.warning("Please upload the vgsales.csv dataset.")
        st.stop()

# Data Cleaning
df["Year"] = df["Year"].fillna(0)
df["Publisher"] = df["Publisher"].fillna("Unknown")
df["Year"] = df["Year"].astype("int64")

# Sidebar Filters
st.sidebar.header("Dashboard Filters")

platforms = st.sidebar.multiselect(
    "Select Platform",
    options=sorted(df["Platform"].dropna().unique()),
    default=sorted(df["Platform"].dropna().unique())
)

genres = st.sidebar.multiselect(
    "Select Genre",
    options=sorted(df["Genre"].dropna().unique()),
    default=sorted(df["Genre"].dropna().unique())
)

# Filter Dataset
data = df[
    (df["Platform"].isin(platforms)) &
    (df["Genre"].isin(genres))
].copy()

# Outlier Removal
remove_outliers = st.sidebar.checkbox("Remove Sales Outliers")

if remove_outliers:
    sales_columns = ["NA_Sales", "EU_Sales", "JP_Sales"]

    for col in sales_columns:
        q1 = data[col].quantile(0.25)
        q3 = data[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        data = data[
            (data[col] >= lower) &
            (data[col] <= upper)
        ]

# Dataset Overview
st.header("📊 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Games", len(data))
col2.metric("Total Platforms", data["Platform"].nunique())
col3.metric("Total Genres", data["Genre"].nunique())
col4.metric(
    "Global Sales",
    f"{data['Global_Sales'].sum():,.2f} M"
)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Dataset",
    "Regional Sales",
    "Platform & Genre",
    "Publisher Analysis"
])

# TAB 1: Dataset
with tab1:

    st.subheader("Dataset Information")

    st.dataframe(data, use_container_width=True)

    st.subheader("Data Types")
    st.dataframe(data.dtypes.astype(str).to_frame("Data Type"))

    st.subheader("Missing Values")
    st.dataframe(data.isnull().sum().to_frame("Missing Values"))

    st.subheader("Statistical Summary")
    st.dataframe(data.describe().T)

    st.download_button(
        "Download Cleaned Dataset",
        data.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_vgsales.csv",
        mime="text/csv"
    )

# TAB 2: Regional Sales
with tab2:

    st.subheader("Regional Sales Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        sb.histplot(data["NA_Sales"], kde=True, ax=ax)
        ax.set_title("North America Sales Distribution")
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots()
        sb.histplot(data["EU_Sales"], kde=True, ax=ax)
        ax.set_title("Europe Sales Distribution")
        st.pyplot(fig)
        plt.close(fig)

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        sb.histplot(data["JP_Sales"], kde=True, ax=ax)
        ax.set_title("Japan Sales Distribution")
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots()
        sb.boxplot(
            data=data[["NA_Sales", "EU_Sales", "JP_Sales"]]
        )
        ax.set_title("Regional Sales Boxplot")
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Regional Sales Comparison")

    regional_sales = data[
        ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
    ].sum()

    fig, ax = plt.subplots()
    sb.barplot(x=regional_sales.index, y=regional_sales.values, ax=ax)
    ax.set_ylabel("Sales (Millions)")
    ax.set_xlabel("Regions")
    st.pyplot(fig)
    plt.close(fig)

# TAB 3: Platform & Genre
with tab3:

    st.subheader("Platform-wise Global Sales")

    platform_sales = data.groupby(
        "Platform"
    )["Global_Sales"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 5))
    sb.barplot(
        x=platform_sales.index,
        y=platform_sales.values,
        ax=ax
    )
    ax.tick_params(axis="x", rotation=90)
    ax.set_ylabel("Global Sales (Millions)")
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Genre-wise Global Sales")

    genre_sales = data.groupby(
        "Genre"
    )["Global_Sales"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 5))
    sb.barplot(
        x=genre_sales.index,
        y=genre_sales.values,
        ax=ax
    )
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("Global Sales (Millions)")
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Platform-wise Regional Sales")

    platform_region = data.groupby("Platform")[
        ["NA_Sales", "EU_Sales", "JP_Sales"]
    ].sum()

    st.dataframe(platform_region)

    st.subheader("Genre-wise Regional Sales")

    genre_region = data.groupby("Genre")[
        ["NA_Sales", "EU_Sales", "JP_Sales"]
    ].sum()

    st.dataframe(genre_region)

    st.subheader("Top Selling Video Games")

    st.dataframe(
        data.sort_values(
            "Global_Sales",
            ascending=False
        ).head(10),
        use_container_width=True
    )

# TAB 4: Publisher Analysis
with tab4:

    st.subheader("Top 10 Publishers")

    publisher_sales = data.groupby(
        "Publisher"
    )["Global_Sales"].sum().nlargest(10)

    fig, ax = plt.subplots(figsize=(12, 5))
    sb.barplot(
        x=publisher_sales.values,
        y=publisher_sales.index,
        ax=ax
    )
    ax.set_xlabel("Global Sales (Millions)")
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Publisher Sales Details")

    publisher_region = data.groupby("Publisher")[
        ["NA_Sales", "EU_Sales", "JP_Sales", "Global_Sales"]
    ].sum().sort_values("Global_Sales", ascending=False)

    st.dataframe(publisher_region.head(20))

    st.subheader("Total Global Sales")

    st.metric(
        "Total Global Sales",
        f"{data['Global_Sales'].sum():,.2f} Million"
    )

# Footer
st.markdown("---")
st.markdown(
    "🎮 **Video Game Sales Analysis Dashboard** | "
    "Video Game Sales Analysis Dashboard Loaded Successfully!"
)
