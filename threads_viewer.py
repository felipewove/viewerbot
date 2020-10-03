import linecache
import random
import sys
import time
from threading import Thread

import requests
from fake_useragent import UserAgent
from streamlink import Streamlink


proxies_file = "proxies/good_proxy.txt"
all_proxies = list()

# Session creating for request
ua = UserAgent()
session = Streamlink()
session.set_option(
    "http-headers",
    {
        'User-Agent': ua.random,
        "Client-ID": "ewvlchtxgqq88ru9gmfp1gmyt6h2b93",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
)


def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def get_proxies():
    # Reading the list of proxies
    try:
        return [line.rstrip("\n") for line in open(proxies_file)]
    except IOError as e:
        print("An error has occurred while trying to read the list of proxies: %s" % e.strerror)
        sys.exit(1)


def open_url(proxy_data):
    try:
        global all_proxies
        headers = {
            'User-Agent': ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        current_index = all_proxies.index(proxy_data)

        if not proxy_data['url']:
            try:
                streams = session.streams("https://www.twitch.tv/felipewove")
                if streams:
                    try:
                        proxy_data['url'] = streams['480p'].url
                    except:
                        proxy_data['url'] = streams['worst'].url
                else:
                    return
            except:
                print("************* Streamlink Error! *************", sys.exc_info()[0], sys.exc_info()[1])

        try:
            if time.time() - proxy_data['time'] >= random.randint(1, 5):
                current_proxy = {"http": "http://"+proxy_data['proxy'], "https": "https://"+proxy_data['proxy']}
                with requests.Session() as request:
                    response = request.head(proxy_data['url'], proxies=current_proxy, headers=headers)
                print(f"Sent HEAD request with {current_proxy['http']} | {response.status_code} | {response.request} | {response.headers}")
                proxy_data['time'] = time.time()
                all_proxies[current_index] = proxy_data
        except:
            print("************* Connection Error! *************", sys.exc_info()[0], sys.exc_info()[1], proxy_data)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()


if __name__ == "__main__":
    max_nb_of_threads = 1000
    
    for proxy in get_proxies():
        all_proxies.append({
            'proxy': proxy,
            'time': time.time(),
            'url': "",
        })

    # open_url(all_proxies[0])
    while True:
        try:
            for thread_id in range(0, len(all_proxies)-1):
                threaded = Thread(
                    target=open_url,
                    args=(all_proxies[thread_id],)
                )
                threaded.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
                threaded.start()
        except:
            print_exception()
        random.shuffle(all_proxies)
        time.sleep(5)
