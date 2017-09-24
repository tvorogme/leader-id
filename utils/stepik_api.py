import json

import requests


def get_token() -> str:
    client_id = 'UV9HpDB6lTdJXa35ayxxCX9Iw47rptSMHHRB4Qx9'
    client_secret = '0c1kWfRCRJp5GWswqLbNZU8OzP9id9MlWS5PH2Ycg16FfHscK7Oqiquf7uikggp8MY1vfinhyCZQt9QwXsjSOqK9lhmYkXCe9jNRTqDsUoSmgPMblgKgq1NEMPvyHsXN'

    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    resp = requests.post('https://stepik.org/oauth2/token/',
                         data={'grant_type': 'client_credentials'},
                         auth=auth)

    return json.loads(resp.text)['access_token']
