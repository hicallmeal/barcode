#login, works. finish when activating and cancelling sim next.

import requests

username = ""
password = ""

session = requests.Session()

login_url = "https://www.belong.com.au/new/login"
token_url = "https://belong.au.auth0.com/oauth/token"
auths_url = "https://belong.au.auth0.com/mfa/authenticators"
chall_url = "https://belong.au.auth0.com/mfa/challenge"

client_id = "" # seems hard coded, though likely updates

token = {
    'username': username,
    'password': password,
    'audience': 'https://api.belong.com.au',
    'grant_type': 'password',
    'client_id': client_id,
    'scope': "openid profile email offline_access read:authenticators",
}

non_mfa_req = session.post(token_url, json=token).json()
access_token = non_mfa_req["access_token"]


token["scope"] = "openid profile email offline_access read:authenticators manage:services manage:profile manage:orders"
mfa_req = session.post(token_url, json=token).json()

mfa_token = mfa_req["mfa_token"]

account_info = session.get(auths_url, headers={"Authorization": "Bearer "+access_token}).json()
for account in account_info: # precautionary, proba
    if account["active"]:
        account_id = account["id"]
        break

challenge = {
    "authenticator_id": account_id,
    "challenge_type": "oob",
    "client_id": client_id,
    "mfa_token": mfa_token
}

oob_code = session.post(chall_url, json=challenge).json()["oob_code"]
code = input("code: ")

mfa_json = {
    "binding_code": code,
    "client_id": client_id,
    "grant_type": "http://auth0.com/oauth/grant-type/mfa-oob",
    "mfa_token": mfa_token,
    "oob_code": oob_code
}

mfa_response = session.post(token_url, json=mfa_json) #cause I'm dumb
if not mfa_response.ok:
    code = input("Wrong code, what is it: ")
    mfa_response = session.post(token_url, json=mfa_json).json()


token["scope"] = "enroll offline_access read:authenticators"
token["x_access_token"] = mfa_response.json()["access_token"]
token["audience"] = "https://belong.au.auth0.com/mfa/"

final_auth = session.post(token_url, json=token).json()


