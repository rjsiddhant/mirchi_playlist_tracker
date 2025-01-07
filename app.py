import streamlit as st
import pandas as pd
from yt import fetch_view_count
from spo import get_playcount
from datetime import datetime

# Helper function to format YouTube views
def format_youtube_views(view_count):
    if isinstance(view_count, int):
        millions = view_count / 1_000_000
        if millions < 1:
            return f"{millions:.1f}"
        return f"{int(millions)}"
    return view_count

# Display logo
st.image("logo.png", width=100)

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
        # Replace hyperlinks with actual links
        yt_df[yt_column] = replace_hyperlinks(yt_df, yt_column)
        sheet_data["YouTube"] = (yt_df, yt_column)

    if "Spotify Play Counts" in options:
        spo_sheet = st.selectbox("Select the sheet for Spotify links", xls.sheet_names, key="spo_sheet")
        spo_df = pd.read_excel(uploaded_file, sheet_name=spo_sheet)
        spo_column = st.selectbox("Select the column with Spotify links", spo_df.columns, key="spo_column")
        # Replace hyperlinks with actual links
        spo_df[spo_column] = replace_hyperlinks(spo_df, spo_column)
        sheet_data["Spotify"] = (spo_df, spo_column)

    # Step 3: Fetch metrics
    if st.button("Fetch Metrics"):
        st.write("Fetching data... Please wait ⏳")
        progress_bar = st.progress(0)
        total_steps = sum(len(df) for df, _ in sheet_data.values())
        completed_steps = 0

        # Display fetched data in real-time
        for metric, (df, column) in sheet_data.items():
            st.write(f"Fetching {metric} data...")

            if metric == "YouTube":
                yt_views = []
                for idx, link in enumerate(df[column]):
                    view_count = fetch_view_count(link)
                    formatted_view_count = format_youtube_views(view_count)
                    yt_views.append(formatted_view_count)
                    completed_steps += 1
                    progress_bar.progress(completed_steps / total_steps)

                    # Real-time display
                    st.write(f"Row {idx + 1}: YouTube Link: {link} - Views: {formatted_view_count}")

                df["YouTube Views (Millions)"] = yt_views

            if metric == "Spotify":
                spo_playcounts = []
                for idx, link in enumerate(df[column]):
                    try:
                        track_id = link.split("track/")[1].split("?")[0]
                        playcount = get_playcount(track_id)
                        spo_playcounts.append(playcount)
                    except:
                        playcount = None
                        spo_playcounts.append(playcount)

                    completed_steps += 1
                    progress_bar.progress(completed_steps / total_steps)

                    # Real-time display
                    st.write(f"Row {idx + 1}: Spotify Link: {link} - Play Count: {playcount}")

                df["Spotify Play Counts"] = spo_playcounts

            # Add timestamp
            df["Updated On"] = datetime.now()

        # Step 4: Display updated data
        st.write("Final Updated Data:")
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
