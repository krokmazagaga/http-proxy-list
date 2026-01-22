import requests

SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
]

TIMEOUT = 5

def is_alive(proxy):
    try:
        r = requests.get(
            "http://httpbin.org/ip",
            proxies={
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            },
            timeout=TIMEOUT
        )
        return r.status_code == 200
    except:
        return False


def main():
    proxies = set()

    for url in SOURCES:
        try:
            res = requests.get(url, timeout=10)
            for line in res.text.splitlines():
                if ":" in line:
                    proxies.add(line.strip())
        except:
            pass

    alive = []
    for proxy in proxies:
        if is_alive(proxy):
            alive.append(proxy)

    with open("http.txt", "w") as f:
        f.write("\n".join(alive))

    print(f"Alive proxies: {len(alive)}")


if __name__ == "__main__":
    main()
