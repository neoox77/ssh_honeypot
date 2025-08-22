# Import library dependencies.
import pandas as pd
import re
import requests

# Parser for the creds file. Returns IP Address, Username, Password.
def parse_creds_audits_log(creds_audits_log_file):
    data = []

    with open(creds_audits_log_file, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            if len(parts) >= 3:
                ip_address, username, password = parts[:3]
                data.append([ip_address, username, password])

    df = pd.DataFrame(data, columns=["ip_address", "username", "password"])
    return df

# Parser for commands entered during SSH session.
def parse_cmd_audits_log(cmd_audits_log_file):
    data = []
    pattern = re.compile(r"Command b'([^']*)'executed by (\d+\.\d+\.\d+\.\d+)")
    
    with open(cmd_audits_log_file, 'r') as file:
        for line in file:
            match = pattern.search(line.strip())
            if match:
                command, ip = match.groups()
                data.append({'IP Address': ip, 'Command': command})
    
    df = pd.DataFrame(data)
    return df

# Calculator to generate top 10 values from a dataframe.
def top_10_calculator(dataframe, column):
    if column not in dataframe.columns:
        print(f"[!] Warning: Column '{column}' not found in dataframe.")
        return pd.DataFrame(columns=[column, "count"])
    
    top_10_df = dataframe[column].value_counts().reset_index().head(10)
    top_10_df.columns = [column, "count"]
    return top_10_df

# Takes an IP address and fetches country code from CleanTalk API.
def get_country_code(ip):
    url = f"https://api.cleantalk.org/?method_name=ip_info&ip={ip}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            ip_data = data.get('data', {}).get(ip, {})
            return {'IP Address': ip, 'Country_Code': ip_data.get('country_code', 'Unknown')}
        elif response.status_code == 429:
            print("[!] CleanTalk API rate limit exceeded. Wait 60 seconds.")
        else:
            print(f"[!] Error: Unable to retrieve data for IP {ip}. Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"[!] Request failed: {e}")
    return {'IP Address': ip, 'Country_Code': 'Unknown'}

# Converts IP addresses in a dataframe to country codes.
def ip_to_country_code(dataframe):
    data = [get_country_code(ip) for ip in dataframe['ip_address']]
    return pd.DataFrame(data)
