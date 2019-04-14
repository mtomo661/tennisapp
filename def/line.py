import requests

def post(name, text, line_token):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    text = name + ":" + text
    payload = {'message': text}
    headers = {'Authorization': 'Bearer ' + line_token}  # 発行したトークン
    requests.post(line_notify_api, data=payload, headers=headers)
