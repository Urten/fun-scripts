from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

proxies_response = requests.get(
    "https://proxylist.geonode.com/api/proxy-list?filterLastChecked=4&limit=500&page=1&sort_by=lastChecked&sort_type=desc")
proxies_json = proxies_response.json()

def proxy_test(proxy):
    try:
        # remove country info
        proxy_no_country = proxy.split("#")[0]
        protocol = proxy_no_country.split("://")[0].lower()

        # use same proxy for both http and https requests
        proxies = {"http": proxy_no_country, "https": proxy_no_country}

        # avoid env proxy/no_proxy interfering
        session = requests.Session()
        session.trust_env = False

        # test using the proxy
        resp = session.get("http://httpbin.org/ip", proxies=proxies, timeout=8)
        resp.raise_for_status()

        country = proxy.split("#")[1] if "#" in proxy else None
        print("OK proxy:", proxy_no_country, "->", resp.json())
        return (proxy_no_country, country)
    except Exception as e:
        pass
    return None

def get_working_proxies_list(workers=100):
    proxy_list = []
    for item in proxies_json.get("data", []):
        ip = item.get("ip")
        port = item.get("port")
        protocol = item.get("protocols")[0]
        country = item.get("country")
        if ip and port:
            proxy_list.append(f"{protocol}://{ip}:{port}#{country}")

    working_proxies = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(proxy_test, proxy_list)
        for result in results:
            if result:
                working_proxies.append(result)
    return working_proxies

@app.get("/working_proxies")
def get_working_proxies():
    return JSONResponse(content={"working_proxies": get_working_proxies_list(workers=200)})


if __name__ == "__main__":
    print(get_working_proxies_list(workers=200))