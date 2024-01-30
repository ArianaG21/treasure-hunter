import streamlit as st
import requests

# Function to get information about a country from REST Countries API
def get_country_information(destination):
    rest_countries_api_url = f"https://restcountries.com/v3.1/name/{destination}?fullText=true"
    response = requests.get(rest_countries_api_url)
    data = response.json()

    # Initialize details with default values
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

    # Check if valid data is returned
    if data and isinstance(data, list):
        country_data = data[0]

        # Extract specific details from the REST Countries API response
        details["Name"] = country_data.get("name", "Not available")
        details["Capital"] = country_data.get("capital", "Not available")
        details["Population"] = country_data.get("population", "Not available")
        details["Region"] = country_data.get("region", "Not available")
        details["Subregion"] = country_data.get("subregion", "Not available")
        details["Flag"] = country_data.get("flags", {}).get("png", "Not available")
        details["Borders"] = ", ".join(country_data.get("borders", []))

        # Extract currency information
        currency_data = country_data.get("currencies", [])
        if currency_data and isinstance(currency_data, list):
            currency = currency_data[0]
            details["Currency"] = f"{currency.get('name', 'Not available')} ({currency.get('code', 'Not available')}, {currency.get('symbol', 'Not available')})"

        details["Languages"] = ", ".join(country_data.get("languages", {}).keys())
        details["Timezones"] = ", ".join(country_data.get("timezones", []))
    return details

# Main Streamlit app
def give_results():
    st.title("Treasure Hunter")
    #user Input
    destination = st.text_input("Enter your destination (country):")
    col1, col2, col3 = st.columns([1, 2, 2])
    # Get Information from REST Countries API
    if destination:
        country_info = get_country_information(destination)
        col1.header(f"Information about {destination}")
        col1.write(f"Capital: {country_info['Capital']}")
        col1.write(f"Population: {country_info['Population']}")
        col1.write(f"Region: {country_info['Region']}")
        col1.write(f"Subregion: {country_info['Subregion']}")
        col1.image(country_info['Flag'], caption=f"Flag of {country_info['Name']}", use_column_width=True)
        col1.write(f"Borders: {country_info['Borders']}")
        col1.write(f"Languages: {country_info['Languages']}")
        col1.write(f"Timezones: {country_info['Timezones']}")
    else:
        st.info("Enter a destination to get started.")

if __name__ == "__main__":
    give_results()