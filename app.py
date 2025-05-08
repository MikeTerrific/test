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

    ratings = {}
    rows = table.select("tbody > tr")

    for row in rows:
        try:
            # Team name is in the first <td> with a nested <a>
            team_cell = row.find_all("td")[0]
            team_link = team_cell.find("a")
            team_name = team_link.text.strip() if team_link else team_cell.text.strip()

            # Rating is in the third <td> (index 2) and inside a <div class='detail'>
            rating_cell = row.find_all("td")[2]
            rating_div = rating_cell.find("div", class_="detail")
            rating = float(rating_div.text.strip())

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
