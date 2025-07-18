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
            

    # Tab 6: Manage
    with main_tabs[5]:
        manage_view = st.selectbox("Manage Section:", [
            "Edit Ultimate List", "Edit Anime List", "Edit Manga List",
            "Edit Anime Started", "Edit Manga Started",
            "Edit Future Anime", "Edit Future Manga"
        ], key="manage_select")

        if manage_view == "Edit Anime List":
            st.subheader("Manage Your Watched Anime List")

            new_anime = st.text_input("Add an Anime to Your Watched List", key="anime_input")
            status_value = st.selectbox("Select status:", ["Finished", "Continuous", "Seasonal", "Incomplete"], key="anime_status")
            currently_watching = st.checkbox("Mark as Currently Watching", key="currently_watching_checkbox")
            if st.button("Add to Watched", key="anime_add_button"):
                if new_anime and new_anime not in st.session_state["anime_list"]:
                    st.session_state["anime_list"][new_anime] = {"status": status_value, "watching": currently_watching}
                    save_data(st.session_state["anime_list"], WATCHED_ANIME_FILE)
                    save_data(st.session_state["anime_started"], "anime_started_v2.json")
                    st.success(f"'{new_anime}' added!")
                    if new_anime not in st.session_state["ultimate_list"]:
                        st.session_state["ultimate_list"].append(new_anime)
                        save_data(st.session_state["ultimate_list"], "ultimate_list_v2.json")

            st.write("Reorder your anime list:")
            reordered_list = sort_items(list(st.session_state["anime_list"].keys()), direction="vertical", key="anime_reorder")
            if reordered_list != list(st.session_state["anime_list"].keys()):
                reordered_anime_list = {anime: st.session_state["anime_list"][anime] for anime in reordered_list}
                st.session_state["anime_list"] = reordered_anime_list
                save_data(reordered_anime_list, WATCHED_ANIME_FILE)
                st.success("Order saved!")

            if st.session_state["anime_list"]:
                st.write("Update status of an existing anime:")
                anime_to_edit = st.selectbox("Select anime:", list(st.session_state["anime_list"].keys()), key="anime_edit_select")
                new_status = st.selectbox("New status:", ["Finished", "Continuous", "Seasonal", "Incomplete"], key="anime_edit_status")
                update_currently_watching = st.checkbox("Mark as Currently Watching", key="update_currently_watching_checkbox")
                if st.button("Update Status", key="anime_update_button"):
                    st.session_state["anime_list"][anime_to_edit]["status"] = new_status
                    st.session_state["anime_list"][anime_to_edit]["watching"] = update_currently_watching
                    save_data(st.session_state["anime_list"], WATCHED_ANIME_FILE)
                    st.success("Status updated!")

        elif manage_view == "Edit Ultimate List":
            st.subheader("Reorder Your Combined Anime & Manga List")
            combined = list(st.session_state["anime_list"].keys()) + list(st.session_state["manga_list"].keys())
            seen = set()
            unique_combined = []
            for title in combined:
                if title not in seen:
                    unique_combined.append(title)
                    seen.add(title)
            current_order = st.session_state.get("ultimate_list", unique_combined)
            reordered = sort_items(current_order, direction="vertical", key="ultimate_sort")
            if reordered != current_order:
                st.session_state["ultimate_list"] = reordered
                save_data(reordered, "ultimate_list_v2.json")
                st.success("Ultimate list order saved!")

        elif manage_view == "Edit Manga List":
            st.subheader("Manage Your Manga List")

            new_manga = st.text_input("Add a Manga to Your List", key="manga_input")
            status_value = st.selectbox("Select status:", ["Finished", "Continuous", "Inconsistent", "Incomplete"], key="manga_status")
            currently_reading = st.checkbox("Mark as Currently Reading", key="currently_reading_checkbox")
            if st.button("Add to Manga List", key="manga_add_button"):
                if new_manga and new_manga not in st.session_state["manga_list"]:
                    st.session_state["manga_list"][new_manga] = {"status": status_value, "reading": currently_reading}
                    save_data(st.session_state["manga_list"], "manga_list_v2.json")
                    save_data(st.session_state["manga_started"], "manga_started_v2.json")
                    st.success(f"'{new_manga}' added!")
                    if new_manga not in st.session_state["ultimate_list"]:
                        st.session_state["ultimate_list"].append(new_manga)
                        save_data(st.session_state["ultimate_list"], "ultimate_list_v2.json")

            st.write("Reorder your manga list:")
            reordered_manga_list = sort_items(list(st.session_state["manga_list"].keys()), direction="vertical", key="manga_reorder")
            if reordered_manga_list != list(st.session_state["manga_list"].keys()):
                st.session_state["manga_list"] = {m: st.session_state["manga_list"][m] for m in reordered_manga_list}
                save_data(st.session_state["manga_list"], "manga_list_v2.json")
                st.success("Order saved!")

            if st.session_state["manga_list"]:
                manga_to_remove = st.selectbox("Select manga to remove:", list(st.session_state["manga_list"].keys()), key="manga_remove_select")

                st.write("Update status of an existing manga:")
                manga_to_edit = st.selectbox("Select manga:", list(st.session_state["manga_list"].keys()), key="manga_edit_select")
                new_status = st.selectbox("New status:", ["Finished", "Continuous", "Inconsistent", "Incomplete"], key="manga_edit_status")
                update_currently_reading = st.checkbox("Mark as Currently Reading", key="update_currently_reading_checkbox")
                if st.button("Update Manga Status", key="manga_update_button"):
                    st.session_state["manga_list"][manga_to_edit]["status"] = new_status
                    st.session_state["manga_list"][manga_to_edit]["reading"] = update_currently_reading
                    save_data(st.session_state["manga_list"], "manga_list_v2.json")
                    st.success("Manga status updated!")

                st.write("Remove a manga from your list:")
                if st.button("Remove Manga", key="manga_remove_button"):
                    del st.session_state["manga_list"][manga_to_remove]
                    save_data(st.session_state["manga_list"], "manga_list_v2.json")
                st.success(f"'{manga_to_remove}' removed!")
            

        elif manage_view == "Edit Anime Started":
            st.subheader("Manage Anime Started List")
            new_anime = st.text_input("Add anime to started list:", key="anime_started_input")
            if st.button("Add Anime Started", key="anime_started_add"):
                if new_anime and new_anime not in st.session_state["anime_started"]:
                    st.session_state["anime_started"].append(new_anime)
                    save_data(st.session_state["anime_started"], "anime_started_v2.json")
                    st.success(f"'{new_anime}' added!")

            if st.session_state["anime_started"]:
                remove_anime = st.selectbox("Remove anime:", st.session_state["anime_started"], key="anime_started_remove")
                if st.button("Remove Anime", key="anime_started_remove_button"):
                    st.session_state["anime_started"].remove(remove_anime)
                    save_data(st.session_state["anime_started"], "anime_started_v2.json")
                    st.success(f"'{remove_anime}' removed!")

        elif manage_view == "Edit Manga Started":
            st.subheader("Manage Manga Started List")
            new_manga = st.text_input("Add manga to started list:", key="manga_started_input")
            if st.button("Add Manga Started", key="manga_started_add"):
                if new_manga and new_manga not in st.session_state["manga_started"]:
                    st.session_state["manga_started"].append(new_manga)
                    save_data(st.session_state["manga_started"], "manga_started_v2.json")
                    st.success(f"'{new_manga}' added!")

            if st.session_state["manga_started"]:
                remove_manga = st.selectbox("Remove manga:", st.session_state["manga_started"], key="manga_started_remove")
                if st.button("Remove Manga", key="manga_started_remove_button"):
                    st.session_state["manga_started"].remove(remove_manga)
                    save_data(st.session_state["manga_started"], "manga_started_v2.json")
                    st.success(f"'{remove_manga}' removed!")

        elif manage_view == "Edit Future Anime":
            st.subheader("Manage Future Anime List")
            new_future_anime = st.text_input("Add anime to future list:", key="future_anime_input")
            if st.button("Add Future Anime", key="future_anime_add"):
                if new_future_anime and new_future_anime not in st.session_state["future_anime"]:
                    st.session_state["future_anime"].append(new_future_anime)
                    save_data(st.session_state["future_anime"], "future_anime_v2.json")
                    st.success(f"'{new_future_anime}' added!")

            st.write("Reorder future anime list:")
            reordered_future_anime = sort_items(
                st.session_state["future_anime"], direction="vertical", key="future_anime_reorder"
            )
            if reordered_future_anime != st.session_state["future_anime"]:
                st.session_state["future_anime"] = reordered_future_anime
                save_data(reordered_future_anime, "future_anime_v2.json")
                st.success("Order updated!")

            if st.session_state["future_anime"]:
                remove_anime = st.selectbox("Remove anime:", st.session_state["future_anime"], key="future_anime_remove")
                if st.button("Remove Anime", key="future_anime_remove_button"):
                    st.session_state["future_anime"].remove(remove_anime)
                    save_data(st.session_state["future_anime"], "future_anime_v2.json")
                    st.success(f"'{remove_anime}' removed!")

        elif manage_view == "Edit Future Manga":
            st.subheader("Manage Future Manga List")
            new_future_manga = st.text_input("Add manga to future list:", key="future_manga_input")
            if st.button("Add Future Manga", key="future_manga_add"):
                if new_future_manga and new_future_manga not in st.session_state["future_manga"]:
                    st.session_state["future_manga"].append(new_future_manga)
                    save_data(st.session_state["future_manga"], "future_manga_v2.json")
                    st.success(f"'{new_future_manga}' added!")

            st.write("Reorder future manga list:")
            reordered_future_manga = sort_items(
                st.session_state["future_manga"], direction="vertical", key="future_manga_reorder"
            )
            if reordered_future_manga != st.session_state["future_manga"]:
                st.session_state["future_manga"] = reordered_future_manga
                save_data(reordered_future_manga, "future_manga_v2.json")
                st.success("Order updated!")

            if st.session_state["future_manga"]:
                remove_manga = st.selectbox("Remove manga:", st.session_state["future_manga"], key="future_manga_remove")
                if st.button("Remove Manga", key="future_manga_remove_button"):
                    st.session_state["future_manga"].remove(remove_manga)
                    save_data(st.session_state["future_manga"], "future_manga_v2.json")
                    st.success(f"'{remove_manga}' removed!")

        else:
            st.write(f"You selected: {manage_view}")
