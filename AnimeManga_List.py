import streamlit as st
import json
from streamlit_sortables import sort_items
import os

# Files to store data
WATCHED_ANIME_FILE = "anime_list_v2.json"
WATCHLIST_ANIME_FILE = "anime_watchlist_v2.json"
EXPECTED_RETURN_FILE = "expected_return_v2.json"

# Function to load data and ensure correct format
def load_data(file, as_dict=False):
    try:
        with open(file, "r") as f:
            data = json.load(f)
            if as_dict:
                if isinstance(data, list):
                    return {item: {"status": "Finished", "watching": False} for item in data}
                if isinstance(list(data.values())[0], str):
                    return {k: {"status": v, "watching": False} for k, v in data.items()}
                return data
            else:
                return data if isinstance(data, list) else []
    except FileNotFoundError:
        return {} if as_dict else []

# Function to save data
def save_data(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

# Initialize session state for all lists
if "anime_list" not in st.session_state:
    st.session_state["anime_list"] = load_data(WATCHED_ANIME_FILE, as_dict=True)
if "manga_list" not in st.session_state:
    st.session_state["manga_list"] = load_data("manga_list_v2.json", as_dict=True)
if "watchlist_anime" not in st.session_state:
    st.session_state["watchlist_anime"] = load_data(WATCHLIST_ANIME_FILE)
if "expected_return" not in st.session_state:
    st.session_state["expected_return"] = load_data(EXPECTED_RETURN_FILE, as_dict=True)

if "ultimate_list" not in st.session_state:
    try:
        st.session_state["ultimate_list"] = load_data("ultimate_list_v2.json")
    except Exception:
        combined = list(st.session_state.get("anime_list", {}).keys()) + list(st.session_state.get("manga_list", {}).keys())
        seen = set()
        unique_combined = []
        for title in combined:
            if title not in seen:
                unique_combined.append(title)
                seen.add(title)
        st.session_state["ultimate_list"] = unique_combined
        save_data(unique_combined, "ultimate_list_v2.json")

if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "home"

# Home Screen
if st.session_state["current_tab"] == "home":
    st.title("My Weeaboo Shelf")
    st.header("Welcome to Your Anime & Manga Tracker")

    try:
        st.image("GoingMerryOGCrew.jpg", use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load image: {e}")

    if st.button("Enter Tracker"):
        st.session_state["current_tab"] = "tracker"
        st.rerun()

else:
    st.title("My Weeaboo Shelf")

    if st.button("Return to Home Screen"):
        st.session_state["current_tab"] = "home"
        st.rerun()

    # New layout with 5 main dropdown tabs
    main_tabs = st.tabs(["List", "Current", "Started", "Future", "Info", "Manage"])

    # Tab 1: List
    with main_tabs[0]:
        list_view = st.selectbox("Choose a view:", ["Ultimate List", "Anime List", "Manga List"], key="list_select")

        if list_view == "Anime List":
            st.subheader("Your Watched Anime List")
            filter_option = st.selectbox(
                "Filter by status:", ["All", "Finished", "Continuous", "Seasonal", "Incomplete"], key="anime_filter"
            )
            filtered_list = [
                anime for anime, meta in st.session_state["anime_list"].items()
                if filter_option == "All" or meta["status"] == filter_option
            ]
            if filtered_list:
                for i, anime in enumerate(filtered_list, start=1):
                    st.write(f"{i}. {anime}")
            else:
                st.write("No anime to display with the selected filter.")

        elif list_view == "Manga List":
            st.subheader("Your Manga List")
            filter_option = st.selectbox(
                "Filter by status:", ["All", "Finished", "Continuous", "Inconsistent", "Incomplete"], key="manga_filter"
            )
            filtered_list = [
                manga for manga, meta in st.session_state["manga_list"].items()
                if filter_option == "All" or meta["status"] == filter_option
            ]
            if filtered_list:
                for i, manga in enumerate(filtered_list, start=1):
                    st.write(f"{i}. {manga}")
            else:
                st.write("No manga to display.")

        elif list_view == "Ultimate List":
            st.subheader("Your Combined Anime & Manga List")
            combined = list(st.session_state["anime_list"].keys()) + list(st.session_state["manga_list"].keys())
            seen = set()
            unique_combined = []
            for title in combined:
                if title not in seen:
                    unique_combined.append(title)
                    seen.add(title)

            ordered_list = st.session_state.get("ultimate_list", unique_combined)
            # Keep only items that still exist in either list
            ordered_list = [item for item in ordered_list if item in seen]

            for i, item in enumerate(ordered_list, start=1):
                st.write(f"{i}. {item}")

        else:
            st.write(f"You selected: {list_view}")

    # Tab 2: Current
    with main_tabs[1]:
        current_view = st.selectbox("Currently Watching/Reading:", ["Currently Watching", "Currently Reading"], key="current_select")
        if current_view == "Currently Watching":
            st.subheader("Anime You're Currently Watching")
            watching_list = [anime for anime, meta in st.session_state["anime_list"].items() if meta.get("watching")]
            if watching_list:
                for i, anime in enumerate(watching_list, start=1):
                    st.write(f"{i}. {anime}")
            else:
                st.write("No anime currently marked as watching.")

        elif current_view == "Currently Reading":
            st.subheader("Manga You're Currently Reading")
            reading_list = [manga for manga, meta in st.session_state["manga_list"].items() if meta.get("reading")]
            if reading_list:
                for i, manga in enumerate(reading_list, start=1):
                    st.write(f"{i}. {manga}")
            else:
                st.write("No manga currently marked as reading.")

    # Tab 3: Started
    with main_tabs[2]:
        started_view = st.selectbox("Started Lists:", ["Anime Started", "Manga Started"], key="started_select")
        if "anime_started" not in st.session_state:
            st.session_state["anime_started"] = load_data("anime_started_v2.json")
        if "manga_started" not in st.session_state:
            st.session_state["manga_started"] = load_data("manga_started_v2.json")

        if started_view == "Anime Started":
            st.subheader("Anime You've Started")
            if st.session_state["anime_started"]:
                for i, anime in enumerate(st.session_state["anime_started"], 1):
                    st.write(f"{i}. {anime}")
            else:
                st.write("No anime started yet.")

        elif started_view == "Manga Started":
            st.subheader("Manga You've Started")
            if st.session_state["manga_started"]:
                for i, manga in enumerate(st.session_state["manga_started"], 1):
                    st.write(f"{i}. {manga}")
            else:
                st.write("No manga started yet.")

    # Tab 4: Future
    with main_tabs[3]:
        future_view = st.selectbox("Future Plans:", ["Future Anime", "Future Manga"], key="future_select")
        if "future_anime" not in st.session_state:
            st.session_state["future_anime"] = load_data("future_anime_v2.json")
        if "future_manga" not in st.session_state:
            st.session_state["future_manga"] = load_data("future_manga_v2.json")

        if future_view == "Future Anime":
            st.subheader("Anime You Plan to Watch")
            if st.session_state["future_anime"]:
                for i, anime in enumerate(st.session_state["future_anime"], 1):
                    st.write(f"{i}. {anime}")
            else:
                st.write("No anime in your future watchlist.")

        elif future_view == "Future Manga":
            st.subheader("Manga You Plan to Read")
            if st.session_state["future_manga"]:
                for i, manga in enumerate(st.session_state["future_manga"], 1):
                    st.write(f"{i}. {manga}")
            else:
                st.write("No manga in your future readlist.")

    # Tab 5: Info
    with main_tabs[4]:
        info_view = st.selectbox("Select Info Type:", ["Release Date", "Release Time"], key="info_select")

        if info_view == "Release Date":
            st.subheader("Release Date Tracker")
            st.markdown("### Anime")
            for anime, meta in st.session_state["anime_list"].items():
                if meta["status"] == "Seasonal":
                    key_name = anime + "_date"
                    default_val = st.session_state["expected_return"].get(key_name, "")
                    updated_val = st.text_input(f"{anime}", value=default_val, key=f"anime_date_{anime}")
                    st.session_state["expected_return"][key_name] = updated_val

            save_data(st.session_state["expected_return"], EXPECTED_RETURN_FILE)

        elif info_view == "Release Time":
            st.subheader("Release Time Tracker")
            st.markdown("### Anime")
            for anime, meta in st.session_state["anime_list"].items():
                if meta["status"] in ["Seasonal", "Continuous"] and meta.get("watching"):
                    st.session_state["expected_return"].setdefault(anime + "_time", "")
                    st.session_state["expected_return"][anime + "_time"] = st.text_input(f"{anime}", st.session_state["expected_return"][anime + "_time"], key=f"anime_time_{anime}")

            st.markdown("### Manga")
            for manga, meta in st.session_state["manga_list"].items():
                if meta["status"] == "Continuous" and meta.get("reading"):
                    st.session_state["expected_return"].setdefault(manga + "_time", "")
                    st.session_state["expected_return"][manga + "_time"] = st.text_input(f"{manga}", st.session_state["expected_return"][manga + "_time"], key=f"manga_time_{manga}")
            

