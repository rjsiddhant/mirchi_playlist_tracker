import streamlit as st
import pandas as pd
from yt import fetch_view_count
from spo import get_playcount
from datetime import datetime

st.title("Mirchi Playlist Tracker 🎵")
st.write("Track YouTube views and Spotify play counts for your playlist.")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    # Load Excel file and display available sheets
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("Select Sheet", xls.sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    st.write("Data Preview:")
    st.dataframe(df)

    # Dropdowns for column selection
    yt_column = st.selectbox("Select column with YouTube links", df.columns)
    spo_column = st.selectbox("Select column with Spotify links", df.columns)

    # Fetch metrics
    if st.button("Fetch Metrics"):
        st.write("Fetching YouTube views and Spotify play counts... Please wait ⏳")
        progress_bar = st.progress(0)

        # Fetch YouTube views
        if yt_column in df.columns:
            total_rows = len(df)
            yt_views = []
            for idx, link in enumerate(df[yt_column]):
                yt_views.append(fetch_view_count(link))
                progress_bar.progress((idx + 1) / total_rows)
            df["YouTube Views"] = yt_views

        # Fetch Spotify play counts
        if spo_column in df.columns:
            total_rows = len(df)
            spo_playcounts = []
            for idx, link in enumerate(df[spo_column]):
                try:
                    track_id = link.split("track/")[1].split("?")[0]
                    spo_playcounts.append(get_playcount(track_id))
                except:
                    spo_playcounts.append(None)
                progress_bar.progress((idx + 1) / total_rows)
            df["Spotify Play Counts"] = spo_playcounts

        # Add timestamp and show updated data
        df["Updated On"] = datetime.now()
        st.write("Updated Data:")
        st.dataframe(df)

        # Allow user to download updated Excel file
        st.download_button(
            label="Download Updated File",
            data=df.to_excel(index=False, engine="openpyxl"),
            file_name="updated_playlist.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
