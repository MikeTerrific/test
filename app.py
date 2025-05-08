import streamlit as st
import requests
from bs4 import BeautifulSoup
from scipy.stats import norm

@st.cache_data
def get_ratings():
    url = "https://masseyratings.com/wnba/ratings"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return {}

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", class_="mytable")
        if not table:
            st.error("Could not find table with class='mytable'. Structure may have changed.")
            return {}

        ratings = {}
        rows = table.find("tbody").find_all("tr")
        if not rows:
            st.error("No rows found in table body.")
            return {}

        for i, row in enumerate(rows):
            try:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue

                team_td = cols[0]
                team_link = team_td.find("a")
                team_name = team_link.text.strip() if team_link else team_td.text.strip()

                rating_td = cols[2]
                rating_div = rating_td.find("div", class_="detail")
                if not rating_div:
                    continue

                rating = float(rating_div.text.strip())
                ratings[team_name] = rating
            except Exception as e:
                st.warning(f"Row {i} skipped due to parsing error: {e}")
                continue

        if not ratings:
            st.error("Parsed table but found no valid team ratings.")
        return ratings

    except Exception as e:
        st.error(f"HTML parsing failed: {e}")
        return {}

# UI
st.title("WNBA Win Probability Calculator")
ratings = get_ratings()

if ratings:
    team_list = sorted(ratings.keys())
    team_a = st.selectbox("Select Team A", team_list)
    team_b = st.selectbox("Select Team B", team_list)

    if team_a and team_b and team_a != team_b:
        sigma = 1.0  # standard deviation used in normal CDF
        prob = norm.cdf((ratings[team_a] - ratings[team_b]) / sigma)
        st.metric(label=f"Win Probability: {team_a}", value=f"{prob:.2%}")
        st.metric(label=f"Win Probability: {team_b}", value=f"{(1-prob):.2%}")
else:
    st.error("Failed to load Massey Ratings. Check above for detailed errors.")
