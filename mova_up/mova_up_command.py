#test 

print ("Hello World")

import asyncio
import requests

print ('\n\n---------------------------------')
print ('もし、pyppeteerがエラーを出す場合は、以下のファイルを修正してください。')
print ('\\venv\Lib\site-packages\pyppeteer\__init__.py')
print ('以下のコードを置き換えて')
print ("__chromium_revision__ = '1181205'")
print ('↓')
print ("__chromium_revision__ = '1263111'")
print ('---------------------------------\n\n')


from pyppeteer import launch
import urllib

import os
import mova_up_config

config = mova_up_config.manage_tool_settings()

muser = ''
mpass = ''


def do():
    global muser
    global mpass

    if config is not None:
        muser = config['moveai_user']
        mpass = config['moveai_pass']
    else:
        return 
    
    #
    return asyncio.get_event_loop().run_until_complete(main()) 
    
file = 'C:/Users/tomoh/Desktop/two_person_ken/cam02_two_person_ken.mp4'

#https://qiita.com/bishop_func/items/bb9071e38ce0d812c115

async def main():

    #global settion

    #browser = await launch()
    browser = await launch(headless=False)
    page = await browser.newPage()

    url = 'https://app.move.ai/'
    await page.goto(url)

    # 既存ユーザーのログインボタンをクリック
    await page.click('a#home-beta-signup[href*="auth.move.ai"]')

    # ログインフォームが表示されるまで待つ
    await page.waitForSelector('#signInFormUsername')

    # ユーザー名（Email）とパスワードを入力
    await page.type('#signInFormUsername', muser)  # 実際のメールアドレスに置き換えてください
    await page.type('#signInFormPassword', mpass)  # 実際のパスワードに置き換えてください

    # ログインボタンをクリックして、ページの遷移を待つ
    # ナビゲーションとクリックイベントを同時に待つためにasyncio.gatherを使用
    await asyncio.gather(
        page.waitForNavigation(waitUntil='networkidle0'),  # ネットワークアクティビティがなくなるまで待つ
        page.click('input[name="signInSubmitButton"]')  # サブミットボタンをクリック
    )

    #requestsへ渡す

    
     # クッキーを取得
    cookies = await page.cookies()
    #await browser.close()
    
    #requestsへ渡す

    # セッションを作成 globalでセッションを保持
    session = requests.Session()

    csrf_token = ''

    # Pyppeteerから取得したクッキーをセッションに追加
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

        #print ('cookie name ',cookie['name'],cookie['value'])

        if cookie['name'] == 'csrftoken':
            csrf_token = cookie['value']


    # ログイン後のページをリクエスト
    response = session.get(url)
    #print(response.text)

    print ('csrf_token is ',csrf_token)
    print ('return session and csrf_token')

    
    return [session,csrf_token]

    '''

    await page.goto(url)


 
    # ファイルアップロードボタンをクリック upload_batch_videos_button
    # ボタンが表示されるのを待つ
    await page.waitForSelector('#upload_batch_videos_button', {'visible': True})

    #file dialog
    #const input = await page.$('input[type="file"]')
    #await input.uploadFile(file)


    print ('-----dir page ',dir(page))

    # ボタンをクリック
    await page.click('#upload_batch_videos_button')



    # ボタンが非表示になるまで無期限に待つ
    await page.waitForSelector('#upload_batch_videos_button', options={'hidden': True, 'timeout': 0})
    print("アップロードが開始されました。")

    # ボタンが再表示されるのを無期限に待つ
    await page.waitForSelector('#upload_batch_videos_button', options={'visible': True, 'timeout': 0})
    print("アップロードが完了しました。")

    # 終了前にユーザーの入力を待つ
    print("操作を続けるには何かキーを押してください...")
    input()

    await browser.close()
    '''

