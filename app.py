import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from loguru import logger

# Configure logging
logger.add("error_log.log", rotation="500 MB")

# Initial keywords and authorities
initial_keywords = ["botulinum toxin", "botox", "dermal fillers"]

initial_authorities = {
    "clinical_trials": {
        "usa": "https://clinicaltrials.gov/api/query/study_fields",
        "eu": "https://www.clinicaltrialsregister.eu/ctr-search/search",
        "anz": "https://www.anzctr.org.au/TrialSearch.aspx",
        "canada": "https://health-products.canada.ca/ctdb-bdec/searchsite"
    },
    "drug_approvals": {
        "usa": "https://api.fda.gov/drug/ndc.json",
        "eu": "https://www.ema.europa.eu/en/medicines",
        "australia": "https://www.tga.gov.au/search-node",
        "canada": "https://health-products.canada.ca/dpd-bdpp/index-eng.jsp"
    },
    "medical_device_approvals": {
        "usa": "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm",
        "eu": "https://ec.europa.eu/tools/eudamed",
        "australia": "https://www.tga.gov.au/search/node",
        "canada": "https://health-products.canada.ca/mdall-limh"
    }
}

def log_and_display_error(error_message, url, response_text=None):
    logger.error(f"Error: {error_message} | URL: {url}")
    if response_text:
        logger.error(f"Response Text: {response_text}")
    st.error(f"Error: {error_message} | URL: {url}")
    if response_text:
        st.error(f"Response Text: {response_text}")

def fetch_clinical_trials_usa(keyword, url, max_results=100):
    params = {
        "expr": keyword,
        "fields": "NCTId,Title,Condition,Status,Phase,StartDate,CompletionDate",
        "min_rnk": 1,
        "max_rnk": max_results,
        "fmt": "json"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            trials = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
            if not trials:
                log_and_display_error("No trials found", url, response.text)
            return trials
        else:
            log_and_display_error("Response content is not in JSON format", url, response.text)
            return []
    except requests.exceptions.RequestException as e:
        log_and_display_error(str(e), url)
        return []

# Other fetch functions here...

def display_results(data, category):
    if not data.empty:
        grouped = data.groupby(['Title'])
        for name, group in grouped:
            with st.expander(name):
                st.table(group.drop(columns=['Title']))
    else:
        st.warning(f"No results found for {category}")

# Load initial data
keywords = initial_keywords
authorities = initial_authorities

# Streamlit app
st.title("Competitive Intelligence Dashboard")

# Input for new keywords
search_keyword = st.text_input("Enter search keyword")

if search_keyword:
    if '"' in search_keyword:
        search_keyword = search_keyword.strip('"')  # Exact phrase search
    else:
        search_keyword = search_keyword.replace(' ', '+')  # Boolean search

    # Display data based on the selected keyword
    all_data = []
    for category, sources in authorities.items():
        st.header(f"{category.replace('_', ' ').title()}")
        category_data = []
        for country, url in sources.items():
            st.subheader(f"{country.upper()}")
            fetch_function = globals()[f"fetch_{category}_{country}"]
            data = fetch_function(search_keyword, url)
            if data:
                df = pd.DataFrame(data)
                df['Country'] = country.upper()
                category_data.append(df)
            else:
                st.warning(f"No results found for {search_keyword} in {category} for {country.upper()}")
        if category_data:
            combined_df = pd.concat(category_data)
            display_results(combined_df, category)
            all_data.append(combined_df)

    if not all_data:
        st.warning(f"No results found for {search_keyword}. Please check the keyword or try again later.")
