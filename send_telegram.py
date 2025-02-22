import requests
from config import TOKEN, CHAT_ID

def send_telegram(text: str):
    url = "https://api.telegram.org/bot"
    url += TOKEN
    method = url + "/sendMessage"

    r = requests.post(method, data={
         "chat_id": CHAT_ID,
         "text": text
          })

    if r.status_code != 200:
        raise Exception("post_text error")

if __name__ == '__main__':
  send_telegram('test_message')