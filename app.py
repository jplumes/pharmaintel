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

def fetch_clinical_trials_eu(keyword, url, max_results=100):
    try:
        response = requests.get(f"{url}?query={keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        trials = []
        for row in soup.select('table.results tbody tr')[:max_results]:
            cols = row.find_all('td')
            trials.append({
                'EudraCT Number': cols[0].text.strip(),
                'Title': cols[1].text.strip(),
                'Status': cols[2].text.strip(),
                'Start Date': cols[3].text.strip(),
                'End Date': cols[4].text.strip(),
                'Link': url + cols[0].text.strip()
            })
        if not trials:
            log_and_display_error("No trials found", url, response.text)
        return trials
    except requests.exceptions.RequestException as e:
        log_and_display_error(str(e), url, response.text if 'response' in locals() else None)
        return []

def fetch_clinical_trials_anz(keyword, url, max_results=100):
    try:
        response = requests.get(f"{url}?searchTxt={keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        trials = []
        for row in soup.select('div#trialResults div.trial')[:max_results]:
            title = row.select_one('div.title a').text.strip()
            status = row.select_one('div.status').text.strip()
            start_date = row.select_one('div.startDate').text.strip()
            end_date = row.select_one('div.endDate').text.strip()
            link = row.select_one('div.title a')['href']
            trials.append({
                'Title': title,
                'Status': status,
                'Start Date': start_date,
                'End Date': end_date,
                'Link': link
            })
        if not trials:
            log_and_display_error("No trials found", url, response.text)
        return trials
    except requests.exceptions.RequestException as e:
        log_and_display_error(str(e), url, response.text if 'response' in locals() else None)
        return []

def fetch_clinical_trials_canada(keyword, url, max_results=100):
    try:
        response = requests.get(f"{url}?search={keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        trials = []
        for row in soup.select('table tbody tr')[:max_results]:
            cols = row.find_all('td')
            trials.append({
                'Protocol Number': cols[0].text.strip(),
                'Title': cols[1].text.strip(),
                'Status': cols[2].text.strip(),
                'Date': cols[3].text.strip(),
                'Link': row.find('a')['href']
            })
        if not trials:
            log_and_display_error("No trials found", url, response.text)
        return trials
    except requests.exceptions.RequestException as e:
        log_and_display_error(str(e), url, response.text if 'response' in locals() else None)
        return []

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
    if '"' in searchSure, let's continue from where we left off:

```python
if search_keyword:
    if '"' in search_keyword:
        keywords = [kw.strip() for kw in search_keyword.split('"') if kw.strip()]
    else:
        keywords = [kw.strip() for kw in search_keyword.split(',') if kw.strip()]

# Input for selecting authorities
selected_authorities = {
    "clinical_trials": st.multiselect("Select Clinical Trials Authorities", list(authorities["clinical_trials"].keys()), default=list(authorities["clinical_trials"].keys())),
    "drug_approvals": st.multiselect("Select Drug Approvals Authorities", list(authorities["drug_approvals"].keys()), default=list(authorities["drug_approvals"].keys())),
    "medical_device_approvals": st.multiselect("Select Medical Device Approvals Authorities", list(authorities["medical_device_approvals"].keys()), default=list(authorities["medical_device_approvals"].keys()))
}

# Fetch and display clinical trials
st.subheader("Clinical Trials Data")
clinical_trials_data = []
for keyword in keywords:
    for authority in selected_authorities["clinical_trials"]:
        if authority == "usa":
            clinical_trials_data.extend(fetch_clinical_trials_usa(keyword, authorities["clinical_trials"]["usa"]))
        elif authority == "eu":
            clinical_trials_data.extend(fetch_clinical_trials_eu(keyword, authorities["clinical_trials"]["eu"]))
        elif authority == "anz":
            clinical_trials_data.extend(fetch_clinical_trials_anz(keyword, authorities["clinical_trials"]["anz"]))
        elif authority == "canada":
            clinical_trials_data.extend(fetch_clinical_trials_canada(keyword, authorities["clinical_trials"]["canada"]))

clinical_trials_df = pd.DataFrame(clinical_trials_data)
display_results(clinical_trials_df, "Clinical Trials")

# Fetch and display drug approvals
st.subheader("Drug Approvals Data")
drug_approvals_data = []
for keyword in keywords:
    for authority in selected_authorities["drug_approvals"]:
        # Implement similar fetch functions for drug approvals
        pass

drug_approvals_df = pd.DataFrame(drug_approvals_data)
display_results(drug_approvals_df, "Drug Approvals")

# Fetch and display medical device approvals
st.subheader("Medical Device Approvals Data")
medical_device_approvals_data = []
for keyword in keywords:
    for authority in selected_authorities["medical_device_approvals"]:
        # Implement similar fetch functions for medical device approvals
        pass

medical_device_approvals_df = pd.DataFrame(medical_device_approvals_data)
display_results(medical_device_approvals_df, "Medical Device Approvals")
This code handles:

Fetching clinical trials data for different regions.
Displaying results in an expandable, grouped format using Streamlit.
Logging and displaying errors as they occur.
You will need to implement similar fetch functions for drug approvals and medical device approvals, following the pattern of the clinical trials functions.
