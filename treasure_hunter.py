# import required libraries
import streamlit as st # for UI
import pydeck as pdk # for geospatial visualizations (map)
import pandas as pd # for data handling
import requests #for API calls
import random #for random selections

# Fetch countries data with caching
@st.cache(suppress_st_warning=True, allow_output_mutation=True)

def fetch_countries_data():
    url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(url) #fetching data from API
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        countries = [{
            'CountryName': country['name']['common'],
            'Latitude': country['latlng'][0] if country['latlng'] else 0,
            'Longitude': country['latlng'][1] if country['latlng'] else 0,
        } for country in data if 'latlng' in country and country.get('name')]
        return pd.DataFrame(countries)
    except requests.RequestException as e:
        st.error(f"Error fetching countries data: {e}")
        return pd.DataFrame()

# a welcome page to greet users
#using custom HTML and CSS for styling
def welcome_page():
    st.markdown("""
        <style> 
            .big_title { color: #f5f5dc; font-size: 50px; text-align: center; }
            .subtitle { color: #add8e6; font-size: 30px; text-align: center; }
            .stButton>button { font-size: 20px; 
            border: 2px solid; 
            border-radius: 20px; padding: 10px 24px; margin-top: 20px; }
        </style>
        """, unsafe_allow_html=True)
    st.markdown('<div class="big_title">Welcome to Treasure Hunter...</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Double Click to Embark on Your Next Adventure...</div>', unsafe_allow_html=True)
# # Use a button to transition from the welcome page
    if st.button('Allons-y!'):
        st.session_state.show_welcome = False

# # Managing country selection and favorites. Using session state for persistence across reruns
def manage_country_selection(selected_country):
    if selected_country:
        st.subheader(f"Selected Country: {selected_country}")
        favorite_button, unfavorite_button = st.columns(2)
        with favorite_button:
            ## add to favorites with a check to avoid duplicates
            if st.button("💗", help="Add to favorites!"):
                if selected_country not in st.session_state.favorites:
                    st.session_state.favorites.append(selected_country)
                    st.success(f"Added {selected_country} to favorites!")
                else:
                    st.warning("Country already in favorites.")
        with unfavorite_button:
            # remove from favorites
            if st.button("💔", help="Remove from favorites..."):
                if selected_country in st.session_state.favorites:
                    st.session_state.favorites.remove(selected_country)
                    st.success(f"Removed {selected_country} from favorites.")
                else:
                    st.info("Country not in favorites.")


# fetch country information using the REST Countries API
def get_country_information(destination):
    rest_countries_api_url = f"https://restcountries.com/v3.1/name/{destination}?fullText=true"
    response = requests.get(rest_countries_api_url)
    data = response.json()
    # a dictionary with default values
    details = {
        "Name": "Not available",
        "Capital": "Not available",
        "Population": "Not available",
        "Region": "Not available",
        "Subregion": "Not available",
        "Flag": "Not available",
        "Borders": "Not available",
        "Languages": "Not available",
        "Timezones": "Not available",
    }
    # update details with actual data if available
    if data and isinstance(data, list):
        country_data = data[0]

        details["Name"] = country_data.get("name", {}).get("common", "Not available")
        details["Capital"] = country_data.get("capital", ["Not available"])[0]
        details["Population"] = country_data.get("population", "Not available")
        details["Region"] = country_data.get("region", "Not available")
        details["Subregion"] = country_data.get("subregion", "Not available")
        details["Flag"] = country_data.get("flags", {}).get("png", "Not available")
        details["Borders"] = ", ".join(country_data.get("borders", ["Not available"]))
        details["Languages"] = ", ".join([value for key, value in country_data.get("languages", {}).items()])
        details["Timezones"] = ", ".join(country_data.get("timezones", ["Not available"]))
    return details # always returning a structured response, even if data might be partially missing

def display_country_information(selected_country):
    if selected_country:
        country_info = get_country_information(selected_country)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(country_info['Flag'], caption=f"Flag of {country_info['Name']}", use_column_width=True)
        with col2:
            st.subheader(f"Information about {selected_country}:")
            # directly display each piece of country information
            st.write(f"Capital: {country_info['Capital']}")
            st.write(f"Population: {country_info['Population']}")
            st.write(f"Region: {country_info['Region']}")
            st.write(f"Subregion: {country_info['Subregion']}")
            st.write(f"Borders: {country_info['Borders']}")
            st.write(f"Languages: {country_info['Languages']}")
            st.write(f"Timezones: {country_info['Timezones']}")
# Display a map with the selected country's location, pydeck integration in Streamlit for geographic data visualization
def display_country_map(df_countries, selected_country):
    country_data = df_countries[df_countries["CountryName"] == selected_country].iloc[0] if selected_country in \
    df_countries[
        "CountryName"].values else None
    # defining initial view state with a fallback if country data is not available

    view_state = pdk.ViewState(
        latitude=country_data["Latitude"] if country_data is not None else 0,
        longitude=country_data["Longitude"] if country_data is not None else 0,
        zoom=4 if country_data is not None else 1,
        pitch=0,
        bearing=0
    )
    # ScatterplotLayer for visualizing countries
    country_layer = pdk.Layer(
        "ScatterplotLayer",
        df_countries,
        get_position="[Longitude, Latitude]",
        get_color="[255, 255, 255, 25]",
        get_radius=25000,
        pickable=True,
    )
    # Display the map with configured layers.
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=[country_layer],
        tooltip={"html": "<b>Country:</b> {CountryName}", "style": {"color": "white"}},
    ))

# main function for the app's home page. Incorporates search, map display, and information visualization.
def main_app():
    df_countries = fetch_countries_data()
    # use session state to manage user selections and favorites across reruns
    st.session_state.setdefault("selected_country", "")
    st.session_state.setdefault("favorites", [])

    st.header("Treasure Hunter 🗺️")  # Set the page title
    # Input field for country search
    selected_country = st.text_input("Search for a Country 🌍🌎🌏",
                                     value=st.session_state.selected_country,
                                     key="country_input")

    # Layout for action buttons
    country_action, clear_action = st.columns([3, 1])
    # Random country selection
    with country_action:
        if st.button("Randomize!🌀", help="Click to Randomly Land on a Country!"):
            st.session_state.selected_country = random.choice(df_countries["CountryName"].tolist())
            selected_country = st.session_state.selected_country

    # Clear selection and resetting the app
    with clear_action:
        if st.button("Clear!", help="Clear the Input!"):
            st.session_state.selected_country = ""
            st.experimental_rerun()

    manage_country_selection(selected_country)
    display_country_map(df_countries, selected_country)
    display_country_information(selected_country)

# Function to fetch and display hidden gems
def show_treasures():
    api_key = "bE0a_pzegp0eu7eBqF0N1hoXSjxtjBh7O9fTRFPMYM0l6ZPD76GYDDgeX4WG6S-qLgGDfwj67LpGNGW-uoEtZxiCuMJEjXKwcI9DZoGE3e84u4vrpQufaGg-5_3yZXYx"
    st.title("Treasure Hunter - Hidden Gems")
    country = st.text_input("Enter the country to find hidden gems:")

    if country:
        st.info("Hunting the treasures...") # Keeping the user informed about the app's process
        hidden_gems = get_hidden_gems(country, api_key) # fetch hidden gems based on the country specified by the user

        if hidden_gems:
            st.success(f"Found them! Treasure spots for you to visit in {country}:")
            for gem in hidden_gems:
                with st.container(): # organizing the layout neatly
                    st.markdown(f"**Name:** {gem['name']}")
                    st.markdown(f"**Rating:** {gem['rating']}")
                    st.markdown(f"**Address:** {', '.join(gem['location']['display_address'])}")
                    st.markdown("---")  # Adds a horizontal line for better separation
        else:
            st.warning("That's a great choice :). But unfortunately, "
                       "we don't have enough information on this location yet. Soon to be updated ;)")

def get_hidden_gems(country, api_key):
    api_endpoint = "https://api.yelp.com/v3/businesses/search"
    params = {
        "term": "hidden gems",
        "location": country,
        "categories": "restaurants",
        "sort_by": "rating",
        "radius": 20000,  # Increased radius to 20 km (adjust as needed)
        "limit": 5
    }
    headers = {"Authorization": f"Bearer {api_key}"} # authorization header required by Yelp API
    response = requests.get(api_endpoint, params=params, headers=headers)  # making the API request

    if response.status_code == 200:
        return response.json().get("businesses", []) # extracting businesses from the JSON response
    else:
        st.error("Treasure Hunter is empty handed :(") # inform the user about the failure
        return []

# Display favorites in the sidebar
def display_favorites_sidebar():
    # Initialize favorites list in session state if it doesn't exist
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    st.sidebar.title("My Favorites") # sidebar section for favorites
    if st.session_state.favorites:
        for country in st.session_state.favorites:
            row = st.sidebar.container() # each favorite country gets its own container in the sidebar
            row.text(country) # Display the country name
            # Provide an option to remove from favorites
            if row.button(f"Remove {country}", key=f"btn_remove_{country}"):
                st.session_state.favorites.remove(country)
                st.sidebar.success(f"Removed {country} from favorites")
    else:
        st.sidebar.write("No favorite countries yet. Add some!") # encouraging user interaction

# Navigation and Page Management
def main():
    display_favorites_sidebar()  # displaying the favorites sidebar for quick access.
    st.sidebar.title("Navigation")  # sidebar section for navigation
    # allowing the user to choose between the Home page and the Discover Hidden Gems page
    page = st.sidebar.radio("Go to", ["Home", "Discover Hidden Gems"])

    # entry point of the application
    if page == "Home":
        main_app() # display the main app functionality
    elif page == "Discover Hidden Gems": # display the hidden gems functionality
        show_treasures()

# show the welcome page only
if "show_welcome" not in st.session_state or st.session_state.show_welcome:
    welcome_page()
else:
    main() # proceed to the main content of the app
