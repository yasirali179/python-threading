
# Threaded URL Requests and Data Analysis - Python-threading

This Python script and documentation provide a threaded approach for making HTTP requests to a list of URLs, analyzing response data, finding attribute occurrences, and calculating rarity based on a collection size.

## Usage

### Installation

1. Make sure you have Python 3.x installed.

2. Install the required Python packages using pip:

```bash
pip install requests psutil
```

3. Clone or download this repository to your local machine.


### Running the Script

You can use the provided Python script `threaded_url_requests.py` for multi-threaded URL requests and data analysis. The script includes a class `ThreadRequests` and three main functions for different tasks:

1. `get_data(urls_list: list)`: Fetches data from a list of URLs.
2. `get_occurrence_data(urls_list: list)`: Fetches data and finds attribute occurrences.
3. `get_rarity_data(urls_list: list, collection_size)`: Fetches data, finds attribute occurrences, and calculates rarity.

Here's how to run these functions:

```python
# Example usage
import threaded_url_requests

# List of URLs to fetch data from
urls_list = [...]
collection_size = 20  # Set your collection size

# Fetch data from URLs
attribute_list = threaded_url_requests.get_data(urls_list)

# Find attribute occurrences
occurrence_data = threaded_url_requests.get_occurrence_data(urls_list)

# Calculate rarity
rarity_data = threaded_url_requests.get_rarity_data(urls_list, collection_size)
```

## Documentation

Detailed documentation for the provided Python script `threaded_url_requests.py`:

- Class `ThreadRequests`: A class for handling multi-threaded URL requests and data analysis.
- Methods: `run`, `check_status`, `worker_get`, `find_occurrence`, `get_occurrence`, `calculate_rarity`, and more.
- Properties: `responses`.
- Function `get_data(urls_list)`: Fetches data from a list of URLs using multi-threaded requests.
- Function `get_occurrence_data(urls_list)`: Fetches data and finds attribute occurrences from a list of URLs using multi-threaded requests.
- Function `get_rarity_data(urls_list`, collection_size): Fetches data, finds attribute occurrences, and calculates rarity from a list of URLs using multi-threaded requests.

## License
This project is licensed under the MIT License

## Author
Yasir Ali

LinkedIn:\\yasirali179