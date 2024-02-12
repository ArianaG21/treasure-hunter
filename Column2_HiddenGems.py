import streamlit as st
import requests
# Hardcoded Yelp API key
API_KEY = st.secrets ["YELP_API_KEY"]

# Function to call Yelp API and get hidden gems
def get_hidden_gems(country):
    # Set Yelp API endpoint
    api_endpoint = "https://api.yelp.com/v3/businesses/search"
    # Set parameters for the Yelp API request
    #Terms = ['hidden gems', 'treasure', 'unique', 'rare']
    #categories= ['restaurants', 'castles', 'galleries', 'museums']
    params = {
        "term": "hidden gems",
        "location": country,
        "categories": "restaurants",
        "sort_by": "rating",
        "radius": 20000,  # Increased radius to 20 km (adjust as needed)
        "limit": 5
    }

    # Set headers with Yelp API key
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Make the Yelp API request
    response = requests.get(api_endpoint, params=params, headers=headers)
    col1, col2, col3 = st.columns([1, 2, 2])
    # Check if the request was successful
    if response.status_code == 200:
        return response.json().get("businesses", [])
    else:
        col2.error(f"No Hidden Gems found :(")
        return []


# Streamlit app
def show_treasures():
    st.title("Treasure Hunter")
    country = st.text_input("Enter the country:")
    col1, col2, col3 = st.columns([1, 2, 1])
    # Get user input for the country

    # Check if the user has provided the country
    if country:
        col2.info("Fetching hidden gems...")

        # Call the function to get hidden gems
        hidden_gems = get_hidden_gems(country)

        # Display the hidden gems
        if hidden_gems:
            col2.success("Found them!"
                         f" Treasure spots for you to visit in {country} :)")
            for gem in hidden_gems:
                col2.write(f"Name: {gem['name']}"),
                col2.write(f"Rating: {gem['rating']}"),
                col2.write(f"Address: {', '.join(gem['location']['display_address'])}")
        else:
            col2.warning("That's a great choice :). But unfortunately we don't have enough information on this location yet. Soon to be updated ;)")

if __name__ == "__main__":
    show_treasures()
