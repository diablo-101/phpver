import requests
from bs4 import BeautifulSoup
import re
import sys

def read_urls_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def get_php_version_from_headers(url):
    try:
        response = requests.get(url, allow_redirects=True)
        if 'X-Powered-By' in response.headers:
            return response.headers['X-Powered-By']
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
    return None

def get_php_version_from_body(url):
    try:
        response = requests.get(url, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        for meta in soup.find_all('meta'):
            if 'name' in meta.attrs and meta.attrs['name'].lower() == 'generator':
                content = meta.attrs.get('content', '')
                if 'php' in content.lower():
                    return content
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
    return None

def get_php_version_from_known_endpoints(url):
    known_endpoints = [
        'phpinfo.php',
        'info.php',
        'test.php'
    ]
    
    for endpoint in known_endpoints:
        full_url = f"{url}/{endpoint}"
        try:
            response = requests.get(full_url, allow_redirects=True)
            if response.status_code == 200:
                version = re.search(r'PHP Version (\d+\.\d+\.\d+)', response.text)
                if version:
                    return version.group(0)
        except requests.RequestException as e:
            print(f"Error accessing {full_url}: {e}")
    return None

def get_php_version_from_source_code(url):
    try:
        response = requests.get(url, allow_redirects=True)
        # Ensure the response is successful
        response.raise_for_status()
        
        # Extracting PHP version from response text using regex
        version_match = re.search(r'PHP Version (\d+\.\d+\.\d+)', response.text)
        if version_match:
            return version_match.group(0)
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")
    return None

def get_php_version_from_server_banner(url):
    try:
        response = requests.get(url, allow_redirects=True)
        server_banner = response.headers.get('Server')
        if server_banner and 'PHP' in server_banner:
            return server_banner
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
    return None

def get_php_version_from_error_message(url):
    try:
        response = requests.get(url, allow_redirects=True)
        # Analyze the response content for error messages
        # For simplicity, let's assume a common PHP error message format
        if 'PHP Fatal error' in response.text:
            # Extract version from the error message
            version_match = re.search(r'PHP Version (\d+\.\d+\.\d+)', response.text)
            if version_match:
                return version_match.group(0)
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
    return None

def get_php_version_from_file_metadata(url):
    # This method depends on access to specific files, like version control system metadata,
    # which may not be available publicly. Hence, it's included for completeness but may not be applicable in all cases.
    return None

def get_php_version(url):
    version = get_php_version_from_headers(url)
    if version:
        return version

    version = get_php_version_from_body(url)
    if version:
        return version

    version = get_php_version_from_known_endpoints(url)
    if version:
        return version

    version = get_php_version_from_source_code(url)
    if version:
        return version

    version = get_php_version_from_server_banner(url)
    if version:
        return version

    version = get_php_version_from_error_message(url)
    if version:
        return version

    version = get_php_version_from_file_metadata(url)
    if version:
        return version

    return "PHP version not found"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    urls = read_urls_from_file(file_path)

    for url in urls:
        print(f"Checking {url}...")
        php_version = get_php_version(url)
        print(f"PHP Version: {php_version}")
