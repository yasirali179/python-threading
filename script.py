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
    urls: queue.Queue = queue.Queue()
    infos: queue.Queue = queue.Queue()
    output = {}

    def __init__(
        self,
        urls: List[str],
        http_method: str,
        nb_threads: int = 2,
    ) -> None:
        """Put all urls to the queue url """
        self.nb_threads = nb_threads
        self.http_method = http_method
        self.workers = {"GET": self.worker_get}
        for url in urls:
            self.urls.put(url)

    @property
    def responses(self) -> List[Dict]:
        return [data['attributes'] for data in list(self.infos.queue)]

    def run(self) -> None:
        """ Run all workers"""
        for i in range(0, self.nb_threads):
            threading.Thread(target=self.workers[self.http_method], daemon=True).start()
        threading.Thread(target=self.check_status(), daemon=True).start()
        self.urls.join()

    def check_status(self):
        while not self.urls.empty():
            time.sleep(2)
            print("remaining tasks: " + str(self.urls.unfinished_tasks))

    def worker_get(self) -> None:
        """Pull a url from the queue and make a get request to endpoint"""
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
        """Put found object with occurrence into output dict"""
        if key in self.output:
            if value in self.output[key]:
                self.output[key][value] = self.output[key][value] + 1
            else:
                self.output[key][value] = 1
        else:
            self.output[key] = {value: 1}

    def __update_occurrence(self, attributes):
        for attribute in attributes:
            self.__put_in(attribute['trait_type'], attribute['value'])

    def find_occurrence(self) -> None:
        """Find the occurrence of attribute"""
        for data in list(self.infos.queue):
            attributes = data['attributes']
            for attribute in attributes:
                self.__put_in(attribute['trait_type'], attribute['value'])

    def get_occurrence(self) -> dict:
        """get the occurrence response"""
        self.find_occurrence()
        return self.output

    def calculate_rarity(self, collection_size):
        output = {}
        for data in list(self.infos.queue):
            output[data['json_id']] = collection_size/len(data['attributes'])

        return dict(sorted(output.items()))


def get_data(urls_list: list):
    client = ThreadRequests(urls_list, "GET", nb_threads=200)  # Here we can update number of threads
    client.run()
    return client.responses


def get_occurrence_data(urls_list: list):
    client = ThreadRequests(urls_list, "GET", nb_threads=200)  # Here we can update number of threads
    client.run()
    return client.output


def get_rarity_data(urls_list: list, collection_size):
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

