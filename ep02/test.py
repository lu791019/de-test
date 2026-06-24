import requests

res = requests.get("https://www.ptt.cc/bbs/Tech_Job/index.html")
print(res.text)