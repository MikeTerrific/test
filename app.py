import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from scipy.stats import norm

@st.cache_data
def get_ratings():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://masseyratings.com/wnba/ratings"
    driver.get(url)

    rows = driver.find_elements(By.XPATH, '//table[@id="tbl"]/tbody/tr')
    ratings = {}
    for row in rows:
        try:
            team_cell = row.find_element(By.CLASS_NAME, 'fteam')
            team_name = team_cell.find_element(By.TAG_NAME, 'a').text.strip()
            rating_cell = row.find_elements(By.CLASS_NAME, 'frank')[0]
            rating_value = float(rating_cell.find_element(By.CLASS_NAME, 'detail').text.strip())
            ratings[team_name] = rating_value
        except:
            continue
    driver.quit()
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
