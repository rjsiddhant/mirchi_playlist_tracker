import streamlit as st
import pandas as pd
from yt import fetch_view_count
from spo import get_playcount
from datetime import datetime

st.title("Mirchi Playlist Tracker 🎵")
st.write("Track YouTube views and Spotify play counts for your playlist.")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Data Preview:")
    st.dataframe(df)

    yt_column = st.text_input("Enter column name for YouTube links")
    spo_column = st.text_input("Enter column name for Spotify links")

    if st.button("Fetch Metrics"):
        st.write("Fetching YouTube views and Spotify play counts... This might take a while ⏳")

        if yt_column in df.columns:
            df["YouTube Views"] = df[yt_column].apply(fetch_view_count)
        if spo_column in df.columns:
            df["Spotify Play Counts"] = df[spo_column].apply(lambda x: get_playcount(x.split("track/")[1].split("?")[0]))

        df["Updated On"] = datetime.now()
        st.write("Updated Data:")
        st.dataframe(df)

        st.download_button(
            label="Download Updated File",
            data=df.to_excel(index=False),
            file_name="updated_playlist.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
