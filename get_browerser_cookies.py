import browser_cookie3
import json

cj = list(browser_cookie3.firefox(domain_name="callofduty.com"))

cookie_dict = {"cookies": [{"fails": 0, "data": {}}]}

for cookie in cj:
    if cookie.name == "ACT_SSO_COOKIE_EXPIRY" or\
    cookie.name == "ACT_SSO_COOKIE" or\
    cookie.name == "atkn":
        cookie_dict["cookies"][0]['data'][cookie.name] = cookie.value


with open("app/new_auth_cookies.json", "w") as f:
    json.dump(cookie_dict, f)
