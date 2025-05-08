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

        all_tables = soup.find_all("table")
        target_table = None
        for tbl in all_tables:
            tbl_classes = tbl.get("class", [])
            if any("mytable" in cls for cls in tbl_classes):
                headers = [th.text.strip().lower() for th in tbl.find_all("th")]
                if "team" in headers and "rat" in headers:
                    target_table = tbl
                    break

        if not target_table:
            st.error("Could not find a valid ratings table. Structure may have changed.")
            return {}

        ratings = {}
        rows = target_table.select("tbody > tr")
        if not rows:
            st.error("No rows found in table body. Table may be empty or improperly parsed.")
            return {}

        for i, row in enumerate(rows):
            try:
                cols = row.find_all("td")
                if len(cols) < 3:
                    st.warning(f"Row {i} skipped: not enough columns.")
                    continue

                team_cell = cols[0]
                team_link = team_cell.find("a")
                team_name = team_link.text.strip() if team_link else team_cell.text.strip()

                rating_cell = cols[2]
                rating_div = rating_cell.find("div", class_="detail")
                if not rating_div:
                    st.warning(f"Row {i} ({team_name}) skipped: no rating div.")
                    continue

                rating = float(rating_div.text.strip())
                ratings[team_name] = rating
            except Exception as e:
                st.warning(f"Error parsing row {i}: {e}")
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
