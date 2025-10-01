import streamlit as st
import requests
import json
from datetime import datetime

# API Base URL
API_URL = 'https://black-pessah.onrender.com'

def validate_license():
    st.header("Validate License")
    with st.form(key='validate_form'):
        license_key = st.text_input("License Key", placeholder="Enter license key")
        machine_id = st.text_input("Machine ID", placeholder="Enter machine ID")
        platform = st.text_input("Platform", placeholder="Enter platform")
        arch = st.text_input("Architecture", placeholder="Enter architecture")
        timestamp = datetime.now().isoformat()
        version = "1.0.0"
        submit_button = st.form_submit_button("Validate License")

        if submit_button:
            if not license_key:
                st.error("License Key is required")
                return
            payload = {
                "license_key": license_key,
                "fingerprint": {
                    "machine_id": machine_id,
                    "platform": platform,
                    "arch": arch
                },
                "timestamp": timestamp,
                "version": version
            }
            with st.spinner("Validating..."):
                try:
                    response = requests.post(f"{API_URL}/validate", 
                                          headers={"Content-Type": "application/json"},
                                          data=json.dumps(payload))
                    response.raise_for_status()
                    data = response.json()
                    if data.get("valid"):
                        st.success(f"Status: Valid\nMessage: {data.get('message')}")
                        if data.get("expires_at"):
                            st.write(f"Expires: {datetime.fromisoformat(data['expires_at']).strftime('%Y-%m-%d %H:%M:%S')}")
                        if data.get("remaining_validations") is not None:
                            st.write(f"Remaining Validations: {data['remaining_validations']}")
                    else:
                        st.error(f"Status: Invalid\nMessage: {data.get('message')}")
                except requests.RequestException as e:
                    st.error(f"Failed to validate license: {str(e)}")

def create_license():
    st.header("Create License (Admin)")
    with st.form(key='create_form'):
        admin_token = st.text_input("Admin Token", placeholder="Enter admin token", type="password")
        license_key = st.text_input("License Key (optional)", placeholder="Leave blank to auto-generate")
        expires_in_days = st.number_input("Expires In Days", min_value=1, value=365)
        max_instances = st.number_input("Max Instances", min_value=1, value=1)
        submit_button = st.form_submit_button("Create License")

        if submit_button:
            if not admin_token:
                st.error("Admin Token is required")
                return
            payload = {
                "licenseKey": license_key,
                "expiresInDays": expires_in_days,
                "maxInstances": max_instances
            }
            with st.spinner("Creating..."):
                try:
                    response = requests.post(f"{API_URL}/create",
                                          headers={
                                              "Content-Type": "application/json",
                                              "Authorization": f"Bearer {admin_token}"
                                          },
                                          data=json.dumps(payload))
                    response.raise_for_status()
                    data = response.json()
                    st.success(f"License Key: {data.get('license_key')}\n"
                              f"Expires: {datetime.fromisoformat(data['expires_at']).strftime('%Y-%m-%d %H:%M:%S')}\n"
                              f"Max Instances: {data.get('max_instances')}\n"
                              f"Message: {data.get('message')}")
                except requests.RequestException as e:
                    st.error(f"Failed to create license: {str(e)}")

def stats():
    st.header("License Statistics (Admin)")
    admin_token = st.text_input("Admin Token", placeholder="Enter admin token", type="password")
    if st.button("Fetch Statistics"):
        if not admin_token:
            st.error("Admin Token is required")
            return
        with st.spinner("Loading..."):
            try:
                response = requests.get(f"{API_URL}/stats",
                                      headers={"Authorization": f"Bearer {admin_token}"})
                response.raise_for_status()
                data = response.json()
                st.success(f"Total Licenses: {data.get('total_licenses')}\n"
                          f"Active Licenses: {data.get('active_licenses')}\n"
                          f"Expired Licenses: {data.get('expired_licenses')}\n"
                          f"Recent Validations (7 days): {data.get('recent_validations')}\n"
                          f"Universal License Active: {'Yes' if data.get('universal_license_active') else 'No'}")
            except requests.RequestException as e:
                st.error(f"Failed to fetch stats: {str(e)}")

def main():
    st.title("GhostShell License Manager")
    page = st.sidebar.selectbox("Navigate", ["Validate License", "Create License", "Statistics"])
    
    if page == "Validate License":
        validate_license()
    elif page == "Create License":
        create_license()
    elif page == "Statistics":
        stats()

if __name__ == "__main__":
    main()
