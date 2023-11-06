# Updated On Nov 07, 2023.
"""
Threaded URL Requests and Data Analysis Documentation

This script defines a class 'ThreadRequests' for handling multi-threaded URL requests and data analysis.
The script also provides three functions 'get_data', 'get_occurrence_data', and 'get_rarity_data' for
fetching data, finding attribute occurrences, and calculating rarity, respectively, using the 'ThreadRequests' class.

Author: Yasir Ali
LinkedIn: https://www.linkedin.com/in/yasirali179/

"""

import queue
import time

import psutil
import threading
import requests
from typing import Dict, List
from urllib.parse import urlencode
from dataclasses import dataclass

THREAD_COUNT = psutil.cpu_count() / psutil.cpu_count(logical=True)


def logging(message, stars_count=1):
    print(f'[{"*" * 1}] {message}', flush=True)


@dataclass
class ThreadRequests(object):
    """
        A class for performing threaded URL requests and data analysis.

        Attributes:
        - urls (queue.Queue): A queue to store URLs to be requested.
        - infos (queue.Queue): A queue to store response data.
        - output (dict): A dictionary to store data attributes and their occurrences.
        - nb_threads (int): Number of worker threads to perform URL requests.
        - http_method (str): HTTP method to be used for requests.

        Methods:
        - run(): Initiates and runs the worker threads.
        - check_status(): Continuously checks and logs the remaining tasks in the URL queue.
        - worker_get(): Pulls a URL from the queue and makes a GET request to the endpoint.
        - find_occurrence(): Finds the occurrence of attributes in response data.
        - get_occurrence(): Gets the occurrence response data.
        - calculate_rarity(collection_size): Calculates rarity based on collection size.

        """
    urls: queue.Queue = queue.Queue()
    infos: queue.Queue = queue.Queue()
    output = {}

    def __init__(
        self,
        urls: List[str],
        http_method: str,
        nb_threads: int = 2,
    ) -> None:
        """
        Initializes the ThreadRequests object.

        Args:
        - urls (List[str]): List of URLs to be requested.
        - http_method (str): HTTP method to be used for requests.
        - nb_threads (int): Number of worker threads to perform URL requests.

        """
        self.nb_threads = nb_threads
        self.http_method = http_method
        self.workers = {"GET": self.worker_get}
        for url in urls:
            self.urls.put(url)

    @property
    def responses(self) -> List[Dict]:
        """
        Returns a list of response data attributes.

        Returns:
        - List[Dict]: A list of data attributes from response data.

        """
        return [data['attributes'] for data in list(self.infos.queue)]

    def run(self) -> None:
        """
        Runs all worker threads and a status checker thread.

        """
        for i in range(0, self.nb_threads):
            threading.Thread(target=self.workers[self.http_method], daemon=True).start()
        threading.Thread(target=self.check_status(), daemon=True).start()
        self.urls.join()

    def check_status(self):
        """
        Continuously checks and logs the remaining tasks in the URL queue.

        """
        while not self.urls.empty():
            time.sleep(2)
            print("remaining tasks: " + str(self.urls.unfinished_tasks))

    def worker_get(self) -> None:
        """
        Pulls a URL from the queue and makes a GET request to the endpoint.
        Handles exceptions and logs errors.

        """
        while not self.urls.empty():
            url_obj = self.urls.get()
            try:

                resp = requests.get(url_obj['url'], timeout=60)
                if resp.status_code != 200:
                    raise Exception(resp.text)
                if 'attributes' not in resp.json():
                    raise Exception('attributes not found')
                json_resp = resp.json()
                attributes = json_resp['attributes']
                data = {'json_id':  url_obj['id'], 'attributes': attributes}
                self.__update_occurrence(attributes)
                self.infos.put(data)
                self.urls.task_done()
            except Exception as e:
                logging("Unable to get Data from URL:" + str(url_obj))
                logging("Error:" + str(e.args))
                self.urls.task_done()

    def __put_in(self, key, value):
        """
        Puts found object with occurrence into the output dictionary.

        Args:
        - key: Key to store in the dictionary.
        - value: Value to store in the dictionary.

        """
        if key in self.output:
            if value in self.output[key]:
                self.output[key][value] = self.output[key][value] + 1
            else:
                self.output[key][value] = 1
        else:
            self.output[key] = {value: 1}

    def __update_occurrence(self, attributes):
        """
        Updates the occurrence of attributes in the output dictionary.

        Args:
        - attributes: List of attributes to update occurrences.

        """
        for attribute in attributes:
            self.__put_in(attribute['trait_type'], attribute['value'])

    def find_occurrence(self) -> None:
        """
        Finds the occurrence of attribute values in the response data.

        """
        for data in list(self.infos.queue):
            attributes = data['attributes']
            for attribute in attributes:
                self.__put_in(attribute['trait_type'], attribute['value'])

    def get_occurrence(self) -> dict:
        """
        Gets the occurrence response data.

        Returns:
        - dict: A dictionary containing attribute occurrences.

        """
        self.find_occurrence()
        return self.output

    def calculate_rarity(self, collection_size):
        """
        Calculates rarity based on collection size.

        Args:
        - collection_size: Size of the collection.

        Returns:
        - dict: A dictionary containing rarity values.

        """
        output = {}
        for data in list(self.infos.queue):
            output[data['json_id']] = collection_size/len(data['attributes'])

        return dict(sorted(output.items()))


def get_data(urls_list: list):
    """
    Fetches data from a list of URLs using multi-threaded requests.

    Args:
    - urls_list (list): List of URLs to fetch data from.

    Returns:
    - List[Dict]: A list of response data attributes.

    """
    client = ThreadRequests(urls_list, "GET", nb_threads=200)  # Here we can update number of threads
    client.run()
    return client.responses


def get_occurrence_data(urls_list: list):
    """
    Fetches data and finds attribute occurrences from a list of URLs using multi-threaded requests.

    Args:
    - urls_list (list): List of URLs to fetch data from.

    Returns:
    - dict: A dictionary containing attribute occurrences.

    """
    client = ThreadRequests(urls_list, "GET", nb_threads=200)  # Here we can update number of threads
    client.run()
    return client.output


def get_rarity_data(urls_list: list, collection_size):
    """
    Fetches data, finds attribute occurrences, and calculates rarity from a list of URLs using multi-threaded requests.

    Args:
    - urls_list (list): List of URLs to fetch data from.
    - collection_size: Size of the collection.

    Returns:
    - dict: A dictionary containing rarity values.

    """
    client = ThreadRequests(urls_list, "GET", nb_threads=200)  # Here we can update number of threads
    client.run()
    return client.calculate_rarity(collection_size)


if __name__ == "__main__":
    URL = ""
    query_params = {'pinataGatewayToken': ''}
    max_number = 500
    collection_size = 20

    urls = [{'url': f"{URL}{id_}.json?{urlencode(query_params)}", 'id': id_} for id_ in range(1, max_number + 1)]

    # attribute_list = get_data(urls)
    # print("Attribute List is:")
    # print(attribute_list)

    occurrence_data = get_occurrence_data(urls)
    print(occurrence_data)

    # rarity_data = get_rarity_data(urls, collection_size)
    # print(rarity_data)

