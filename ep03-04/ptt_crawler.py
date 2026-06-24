import requests
from bs4 import BeautifulSoup


# 定義一個 Function，一個傳入參數：看板名稱
def ptt_crawler(board):

    # 目標頁面，將網址內的看板名稱改為變數（使用 f-strings）
    url = f"https://www.ptt.cc/bbs/{board}/index.html"

    # 設定標頭(頭部)資訊
    headers = {
        "cookie": "over18=1"  # 在 cookie 中存放資訊：已滿18歲
        # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
    }

    # 發送 GET 請求，指定 url 與 headers，將回應結果存在變數
    response = requests.get(url, headers=headers)

    # 將回應的內容文字放在 BeautifulSoup 進行解析，存在 soup 變數中
    soup = BeautifulSoup(response.text, "html.parser")

    # 存在一個變數
    all_article = soup.find_all("div", {"class": "r-ent"})

    # 宣告一個空的文章列表(List)，用來存放文章資料（Dictionary）
    article_list = []
    for article in all_article:
        if article.find("div", {"class": "title"}).find("a") is not None:
            title = (
                article.find("div", {"class": "title"}).getText().strip("\n")
            )
            # 連結也要改
            link = f"https://www.ptt.cc/bbs/{board}" + article.find(
                "div", {"class": "title"}
            ).find("a").get("href")
            author = article.find("div", {"class": "author"}).getText()
            date = article.find("div", {"class": "date"}).getText()
            rec_num = article.find("div", {"class": "nrec"}).getText()

            # 宣告字典，欄位名稱(key)自訂，欄位值(value)等於變數
            article_dict = {
                "看板": board,  # 將固定值改為變數
                "標題": title,
                "連結": link,
                "作者": author,
                "日期": date,
                "推文數": rec_num,
            }
            # 將字典新增到列表當中
            article_list.append(article_dict)

    # 回傳字典列表(List of Dictionary)
    return article_list


result = ptt_crawler("Stock")
print(result)
