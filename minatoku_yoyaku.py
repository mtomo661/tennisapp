#実行ファイルのディレクトリをカレントディレクトリに変更
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#関数ディレクトリ設定
import sys
sys.path.append("./def")
#おまじない用
from time import sleep
#日付計算用
import datetime
import target_day
#通知用
import slack
import line

#selenium用
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

##########ユーザー設定箇所##########
headless_flag = 1 #1はヘッドレスブラウザで起動
#対象urlとログイン情報
url = "https://web101.rsv.ws-scs.jp/minato/user/view/user/homeIndex.html"
USER = 60027959
PASS = 11471147
#検索対象日
delta = 30 #何日先までを対象にするか
youbi = (5,6,7)#(0：月曜～6：日曜、7：祝日)
#通知先
slack_post_url = "https://hooks.slack.com/services/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"
line_token = 'N5DDSDTfz2p7LaHNbJVRJSeAOqQPOfS5mvIKzECY5kp'
#保存先
output = "output/toei_aki.csv"

##################################

#ドライバーを設定
driver_path = "chromedriver"
options = Options()
if headless_flag == 1:
    options.add_argument('--headless') #ヘッドレスブラウザにする場合
options.add_argument('--disable-gpu')
browser = webdriver.Chrome(chrome_options=options)
browser.implicitly_wait(5) #ドライバーの初期化待ち

print("------start------")
try:
    #ブラウザを起動して、urlへアクセス
    browser.get(url)
    print(browser.title + "へアクセスしました。")

    #ログイン画面をクリック
    browser.find_element_by_id("login").click()
    browser.implicitly_wait(5)

    #ログイン情報を入力してログイン
    id_user = browser.find_element_by_id("userid")
    id_user.clear()
    id_user.send_keys(USER)
    id_pass = browser.find_element_by_id("passwd")
    id_pass.clear()
    id_pass.send_keys(PASS)
    sleep(3) #待たないとログインできない
    browser.find_element_by_id("doLogin").click()
    browser.implicitly_wait(5)

    #予約「種目から探す」をクリック
    browser.find_element_by_id("goPurposeSearch").click()
    browser.implicitly_wait(5)

    #テニス(ハード、人工芝)にチェックを入れる
    id_checkedes = browser.find_elements_by_id("checked")
    for id_checked in id_checkedes:
        att_name = id_checked.get_attribute("name")
        if att_name == "layoutChildBody:childForm:purposeSearchItems:15:selectItemsItems:0:selectItems:3:checked":#ハード
            id_checked.click()

    #検索ボタンをクリック
    browser.find_element_by_id("doNextPage").click()
    browser.implicitly_wait(5)
    #print(browser.title + "へアクセスしました。")

    #検索日を設定
    t_days = target_day.day(delta, youbi)

    #空き状況検索
    list_aki = []#最終空き状況リスト
    list_yoyaku = []#予約済リスト
    print("検索中...")
    for t_day in t_days:
        day = "{},{},{}".format(t_day.year, t_day.month, t_day.day)
        browser.execute_script("javascript:selectCalendarDate(" + day + ");return false;")#対象日をクリック
        browser.implicitly_wait(5)

        #次のページがある限り検索を繰り返す
        id_isHeader = browser.find_element_by_id("isHeader")
        id_goNextPagers = id_isHeader.find_elements_by_id("goNextPager")
        while len(id_goNextPagers) >= 1:
            tag_tables = browser.find_elements_by_xpath("//*[@id='isNotEmptyPager']/table")#コートごとのテーブルタグリストを取得
            for tag_table in tag_tables:#施設ごとに空きを確認
                id_bnamem = tag_table.find_element_by_id("bnamem")#コート名がある要素を取得
                id_tzoneStimeLabels = tag_table.find_elements_by_id("tzonename")#時間が書いてある要素リストを取得
                id_emptyStateIcons = tag_table.find_elements_by_id("emptyStateIcon")#空き状況が書いてある要素リストを取得
                for i, id_emptyStateIcon in enumerate(id_emptyStateIcons):
                    alt = id_emptyStateIcon.get_attribute("alt")#"alt"に空き情報の記載がある
                    print("{} {} {} {}".format(id_bnamem.text, t_day, id_tzoneStimeLabels[i].text, alt))
                    if alt == "空き":
                        list_aki0 = []
                        list_aki0.append(id_bnamem.text)#コート名
                        list_aki0.append("{} {}".format(t_day, id_tzoneStimeLabels[i].text))#日付
                        list_aki.append(list_aki0)#最終空きリストへ追加
                    elif alt == "受付期間外":
                        break
            if alt == "受付期間外":
                id_goNextPagers = []
            else:
                for id_goNextPager in id_goNextPagers:
                    id_goNextPager.click()
                    browser.implicitly_wait(5)
                    id_isHeader = browser.find_element_by_id("isHeader")
                    id_goNextPagers = id_isHeader.find_elements_by_id("goNextPager")
                    break
        if alt == "受付期間外":
            pass
        #最後の1ページを処理
        tag_tables = browser.find_elements_by_xpath("//*[@id='isNotEmptyPager']/table")#コートごとのテーブルタグリストを取得
        for tag_table in tag_tables:#施設ごとに空きを確認
            id_bnamem = tag_table.find_element_by_id("bnamem")#コート名がある要素を取得
            id_tzonename = tag_table.find_elements_by_id("tzonename")#時間が書いてある要素リストを取得
            id_emptyStateIcons = tag_table.find_elements_by_id("emptyStateIcon")#空き状況が書いてある要素リストを取得
            for i, id_emptyStateIcon in enumerate(id_emptyStateIcons):
                alt = id_emptyStateIcon.get_attribute("alt")#"alt"に空き情報の記載がある
                print("{} {} {} {}".format(id_bnamem.text, t_day, id_tzonename[i].text, alt))
                if alt == "空き":
                    list_aki0 = []
                    list_aki0.append(id_bnamem.text)#コート名
                    list_aki0.append("{} {}".format(t_day, id_tzonename[i].text))#日付
                    list_aki.append(list_aki0)#最終空きリストへ追加
                elif alt == "受付期間外":
                    break

    #検索結果を通知
    if len(list_aki) >= 1:
        data = ""
        for aki in list_aki:
            data = data + " ".join(aki) + "\n"
    else:
        data = "空きはありません。"
    print(data)
    slack.post("港区空き", data, slack_post_url)
    #line.post("港区空き", data, line_token)


except:
    import traceback
    traceback.print_exc()
    data = "エラーだお(;^ω^)"
    slack.post("港区空き", data, slack_post_url)
    #line.post("港区空き", data, line_token)

finally:
    #sleep(10)
    browser.close()#アクティブウィンドウを閉じる
    browser.quit()#ブラウザを閉じる(メモリはきれいにクリアされない...)
    print("--------finish--------")
