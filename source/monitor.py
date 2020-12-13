from time import sleep
import json
import requests
import gzip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from config import *


def get_monthly_usage():
    wait = lambda: sleep(5)
    chrome_options = Options()
    chrome_options.headless = SELENIUM_HEADLESS
    chrome_options.add_argument("--window-size=1600,1000")
    driver = webdriver.Remote(
        SELENIUM_URL,
        desired_capabilities=DesiredCapabilities.CHROME,
        options=chrome_options,
    )
    driver.get(f"{ROUTER_HOST}")
    wait()
    driver.find_element_by_id("login_password").click()
    driver.find_element_by_id("login_password").clear()
    driver.find_element_by_id("login_password").send_keys(ROUTER_PASSWORD)
    driver.find_element_by_id("login_btn").click()
    wait()
    driver.get(f"{ROUTER_HOST}/html/content.html#statistic")
    wait()
    monthly_usage = driver.find_element_by_id("statistic_mounth_flow")
    monthly_usage = float(monthly_usage.text.split()[0].replace(",", "."))
    driver.save_screenshot("usage.png")
    driver.quit()
    return monthly_usage


class CustomEvent(dict):
    def __str__(self):
        return json.dumps(self)

    def __init__(self, *args, **kwargs):
        self["eventType"] = self.__class__.__name__
        return super().__init__(*args, **kwargs)


class MonthlyUsage(CustomEvent):
    pass


def send_events_to_tdp(events):
    """Sends the events to New Relic Telemetry Data Platform."""
    total = len(events)
    json_events = json.dumps(events)
    insert_key = NEW_RELIC_INSERT_KEY
    headers = {"X-Insert-Key": insert_key, "Content-Encoding": "gzip"}
    data = bytes(json_events, "utf-8")
    payload = gzip.compress(data)
    r = requests.post(NEW_RELIC_INSIGHTS_API_URL, data=payload, headers=headers)
    print(r.text)
    if r.status_code == 200:
        print(f"{total} events successfully sent to NR TDP")
    else:
        print("New Relic API Error:", r.status_code, r.text)


def main():
    monthly_usage = get_monthly_usage()
    print(f"Monthly usage: {monthly_usage} GB")
    send_events_to_tdp([MonthlyUsage(gigabytes_used=monthly_usage)])
    return 0


if __name__ == "__main__":
    exit(main())