import requests
from concurrent.futures import ThreadPoolExecutor

proxies_response = requests.get(
    "https://proxylist.geonode.com/api/proxy-list?filterLastChecked=4&limit=500&page=1&sort_by=lastChecked&sort_type=desc")
proxies_json = proxies_response.json()


working_proxies = []


def proxy_test(proxy):
    try:

        protocol = proxy.split("://")[0]
        proxies = {protocol: proxy}
        response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5)

        if response.status_code == 200:
            print(f"Proxy {proxy} is working.")
            working_proxies.append(proxy)
        else:
            print(f"Proxy {proxy} returned status code {response.status_code}.")
    except Exception as e:
        print(f"Proxy {proxy} failed: {e}")

# Extract proxy addresses from the JSON response
proxy_list = []
for item in proxies_json.get("data", []):
    ip = item.get("ip")
    port = item.get("port")
    protocol = item.get("protocols")[0]
    if ip and port:
        proxy_list.append(f"{protocol}://{ip}:{port}")

# Test proxies in parallel
with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(proxy_test, proxy_list)


print(f"Working proxies: {working_proxies}")