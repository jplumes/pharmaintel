import json
import requests
from bs4 import BeautifulSoup
import streamlit as st

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
        response.raise_for_status()  # Raise an error for bad status codes
        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            trials = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
            return trials
        else:
            st.error("Response content is not in JSON format")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
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
                'Link': url + cols[0].text.strip()  # Construct the link
            })
        return trials
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
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
        return trials
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
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
        return trials
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_drug_approvals_usa(keyword, url, max_results=100):
    params = {
        "search": keyword,
        "limit": max_results
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            approvals = data.get('results', [])
            return approvals
        else:
            st.error("Response content is not in JSON format")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_drug_approvals_eu(keyword, url, max_results=100):
    try:
        response = requests.get(f"https://www.ema.europa.eu/en/medicines?search_api_fulltext={keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        approvals = []
        for row in soup.select('div.view-content div.views-row')[:max_results]:
            title = row.select_one('h2').text.strip()
            status = row.select_one('div.field--name-field-status').text.strip()
            date = row.select_one('div.field--name-field-date-of-referral').text.strip()
            link = row.select_one('a')['href']
            approvals.append({
                'Title': title,
                'Status': status,
                'Date': date,
                'Link': "https://www.ema.europa.eu" + link  # Construct the full link
            })
        return approvals
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_drug_approvals_australia(keyword, url, max_results=100):
    try:
        response = requests.get(f"https://www.tga.gov.au/search-node/{keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        approvals = []
        for row in soup.select('ol.search-results li')[:max_results]:
            title = row.select_one('h3').text.strip()
            date = row.select_one('div.search-result-date').text.strip()
            link = row.select_one('a')['href']
            approvals.append({
                'Title': title,
                'Date': date,
                'Link': link
            })
        return approvals
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_drug_approvals_canada(keyword, url, max_results=100):
    try:
        response = requests.get(f"{url}?search={keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        approvals = []
        for row in soup.select('table tbody tr')[:max_results]:
            cols = row.find_all('td')
            link = row.find('a')['href']
            approvals.append({
                'Drug Identification Number (DIN)': cols[0].text.strip(),
                'Brand Name': cols[1].text.strip(),
                'Company': cols[2].text.strip(),
                'Active Ingredient(s)': cols[3].text.strip(),
                'Strength': cols[4].text.strip(),
                'Link': link
            })
        return approvals
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_medical_device_approvals_usa(keyword, url, max_results=100):
    try:
        response = requests.get(f"{url}?keyword={keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        approvals = []
        for row in soup.select('table tbody tr')[:max_results]:
            cols = row.find_all('td')
            link = row.find('a')['href']
            approvals.append({
                '510(k) Number': cols[0].text.strip(),
                'Device Name': cols[1].text.strip(),
                'Decision Date': cols[2].text.strip(),
                'Applicant': cols[3].text.strip(),
                'Link': link
            })
        return approvals
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_medical_device_approvals_eu(keyword, url, max_results=100):
    # Placeholder for EUDAMED scraping
    return []

def fetch_medical_device_approvals_australia(keyword, url, max_results=100):
    try:
        response = requests.get(f"{url}/{keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        approvals = []
        for row in soup.select('ol.search-results li')[:max_results]:
            title = row.select_one('h3').text.strip()
            date = row.select_one('div.search-result-date').text.strip()
            link = row.select_one('a')['href']
            approvals.append({
                'Title': title,
                'Date': date,
                'Link': link
            })
        return approvals
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_medical_device_approvals_canada(keyword, url, max_results=100):
    try:
        response = requests.get(f"{url}?search={keyword}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        approvals = []
        for row in soup.select('table tbody tr')[:max_results]:
            cols = row.find_all('td')
            link = row.find('a')['href']
            approvals.append({
                'Licence Number': cols[0].text.strip(),
                'Device Name': cols[1].text.strip(),
                'Licence Holder': cols[2].text.strip(),
                'Link': link
            })
        return approvals
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

# Load initial data
keywords = initial_keywords
authorities = initial_authorities

# Streamlit app
st.title("Competitive Intelligence Dashboard")

# Sidebar menu
menu = ["Dashboard", "Add Database"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    # Input for new keywords
    new_keyword = st.text_input("Enter new search keyword")
    if st.button("Add Keyword"):
        keywords.append(new_keyword)
        st.success(f"Keyword '{new_keyword}' added.")

    # Select keyword to search
    search_keyword = st.selectbox("Select search keyword", keywords)

    # Display data based on the selected keyword
    if search_keyword:
        for category, sources in authorities.items():
            st.header(f"{category.replace('_', ' ').title()}")
            for country, url in sources.items():
                st.subheader(f"{country.upper()}")
                fetch_function = globals()[f"fetch_{category}_{country}"]
                data = fetch_function(search_keyword, url)
                for item in data:
                    st.write(item)
                    if 'Link' in item:
                        st.markdown(f"[Link to Source]({item['Link']})")

elif choice == "Add Database":
    # Input for new data sources
    new_category = st.text_input("Enter new category (e.g., clinical_trials, drug_approvals, medical_device_approvals)")
    new_country = st.text_input("Enter country code (e.g., usa, eu, anz, canada)")
    new_url = st.text_input("Enter URL for the new data source")
    if st.button("Add Data Source"):
        if new_category in authorities and new_country:
            authorities[new_category][new_country] = new_url
            st.success(f"Data source for '{new_country}' in '{new_category}' category added.")
        else:
            st.error("Invalid category or country code.")
