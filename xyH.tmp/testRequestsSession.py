###############################################################################
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

################################ retry_strategy ###############################
# Configure retry strategy
retry_strategy = Retry(
	total=3, # Total number of retries
	status_forcelist=[429, 500, 502, 503, 504], # Which status codes to retrace
	allowed_methods=["HEAD", "GET", "OPTIONS", "POST"], # Which HTTP methods are allowed to retrace
	backoff_factor=1 # Backoff factor, used to calculate the latency between each retrieval
)

################################ adapter ######################################
# Create an adapter configured with a connection pool to implement connection reuse and apply the retry strategy
# By default, requests already has similar behavior, but mount provides more fine-grained control
adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)

################################ custom_headers ###############################
# The User-Agent header is commonly set to mimic a web browser
custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Authorization': 'Bearer <your_token_here>'
}

################################ session ######################################
# Create a Session object
session = requests.Session()

###############################################################################
# Assign the headers to the session object
session.headers.update(custom_headers)

###############################################################################
# Mount to HTTP and HTTPS (Global Configuration)
session.mount('http://', adapter)
session.mount('https://', adapter)

###############################################################################
# Send requests continuously, reusing the underlying connection
print("First request...")
response1 = session.get('https://clashgithub.com/category/freenode', timeout=5)
print(f"Status: {response1.status_code}")

print("\nSecond request...")
response2 = session.get('https://clashgithub.com/category/freenode', timeout=5)
print(f"Status: {response2.status_code}")

###############################################################################
# Close the session (Optional, but recommended)
session.close()
