import streamlit as st
import pandas as pd
from yt import fetch_view_count
from spo import get_playcount
from datetime import datetime

# Display logo (smaller size and updated parameter)
st.image("logo.png", use_container_width=True, width=200)

st.title("Mirchi Playlist Tracker 🎵")
st.write("Track YouTube views and Spotify play counts for your playlist.")

# Step 1: Ask user what they want to do
options = st.multiselect(
    "What metrics do you want to fetch?",
    ["YouTube Views", "Spotify Play Counts"]
)

# Step 2: Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file and options:
    # Load Excel file and display available sheets
    xls = pd.ExcelFile(uploaded_file)
    sheet_data = {}

    # Dynamically ask for sheets and columns based on user options
    if "YouTube Views" in options:
        yt_sheet = st.selectbox("Select the sheet for YouTube links", xls.sheet_names, key="yt_sheet")
        yt_df = pd.read_excel(uploaded_file, sheet_name=yt_sheet)
        yt_column = st.selectbox("Select the column with YouTube links", yt_df.columns, key="yt_column")
        sheet_data["YouTube"] = (yt_df, yt_column)

    if "Spotify Play Counts" in options:
        spo_sheet = st.selectbox("Select the sheet for Spotify links", xls.sheet_names, key="spo_sheet")
        spo_df = pd.read_excel(uploaded_file, sheet_name=spo_sheet)
        spo_column = st.selectbox("Select the column with Spotify links", spo_df.columns, key="spo_column")
        sheet_data["Spotify"] = (spo_df, spo_column)

    # Step 3: Fetch metrics
    if st.button("Fetch Metrics"):
        st.write("Fetching data... Please wait ⏳")
        progress_bar = st.progress(0)
        total_steps = sum(len(df) for df, _ in sheet_data.values())
        completed_steps = 0

        for metric, (df, column) in sheet_data.items():
            if metric == "YouTube":
                yt_views = []
                for idx, link in enumerate(df[column]):
                    yt_views.append(fetch_view_count(link))
                    completed_steps += 1
                    progress_bar.progress(completed_steps / total_steps)
                df["YouTube Views"] = yt_views

            if metric == "Spotify":
                spo_playcounts = []
                for idx, link in enumerate(df[column]):
                    try:
                        track_id = link.split("track/")[1].split("?")[0]
                        spo_playcounts.append(get_playcount(track_id))
                    except:
                        spo_playcounts.append(None)
                    completed_steps += 1
                    progress_bar.progress(completed_steps / total_steps)
                df["Spotify Play Counts"] = spo_playcounts

            # Add timestamp
            df["Updated On"] = datetime.now()

        # Step 4: Display updated data
        st.write("Updated Data:")
        for metric, (df, _) in sheet_data.items():
            st.write(f"{metric} Data:")
            st.dataframe(df)

        # Step 5: Allow user to download updated file
        output_file = "updated_metrics.xlsx"
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for metric, (df, _) in sheet_data.items():
                df.to_excel(writer, sheet_name=f"{metric}_Updated", index=False)
        with open(output_file, "rb") as file:
            st.download_button(
                label="Download Updated File",
                data=file,
                file_name="updated_metrics.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
