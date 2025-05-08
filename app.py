import streamlit as st
import requests
from bs4 import BeautifulSoup
from scipy.stats import norm

@st.cache_data
def get_ratings():
    url = "https://masseyratings.com/wnba/ratings"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"id": "tbl"})
    if not table:
        return {}

    tbody = table.find("tbody")
    rows = tbody.find_all("tr")
    ratings = {}

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            try:
                team_name = cols[0].find("a").text.strip()
                rating_detail = cols[2].find("div", class_="detail")
                if rating_detail:
                    rating = float(rating_detail.text.strip())
                    ratings[team_name] = rating
            except:
                continue

    return ratings

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
    st.error("Failed to load Massey Ratings.")

