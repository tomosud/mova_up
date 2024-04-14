import requests
import os

import mova_up_command as muc
import time
import json

# ファイルのパスとプリサインドURLのリスト
file_path = "C:/Users/tomoh/Desktop/two_person_ken/cam01_test04.mp4"


def get_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # ステータスコードが200以外の場合はエラーを発生させる
        return response.json()  # JSONデータをPythonの辞書に変換
    except requests.exceptions.HTTPError as e:
        print(f"HTTPエラー: {e}")
    except requests.exceptions.RequestException as e:
        print(f"リクエスト中にエラーが発生しました: {e}")


def split_file(file_path, part_size=30*1024*1024):  # 
    """
    指定されたサイズでファイルを分割するジェネレータ
    :param file_path: 分割するファイルのパス
    :param part_size: 各分割ファイルのサイズ（バイト）
    """
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(part_size)
            if not data:
                break
            yield data


'''
"parts": [
    {"ETag": "bad60c657404bfe462641d6d6a60dd6a", "PartNumber": 3},
    {"ETag": "296c01e7d5786c50cd24d9ea43c8cd14", "PartNumber": 1},
    {"ETag": "0b45981996a16aec241e0eedece22ca1", "PartNumber": 2}
],

'''    
def meke_payload(csrf_token,etag_list,upload_id,file_path,sesstion_ID):

    file_size = os.path.getsize(file_path)

    dictn = {}

    # ペイロードの作成
    payload = {
        "csrfmiddlewaretoken": csrf_token,
        "done": 1,
        "parts": etag_list,
    
        "upload_id": upload_id,
        "file_size": file_size
    }

    # JSON形式でデータをエンコード
    json_data = json.dumps(payload)

    # ヘッダーの設定
    headers = {
        "Content-Type": "application/json",
        "X-CSRFToken": payload["csrfmiddlewaretoken"],  # CSRF Tokenをヘッダーに含める
        'Referer': 'https://app.move.ai/sessions/' + str(sesstion_ID)+ '/'
    }

    cookies={"csrftoken": payload["csrfmiddlewaretoken"]}

    dictn['json_data'] = json_data

    dictn['headers'] = headers

    dictn['cookies'] = cookies

    return dictn

    # POSTリクエストを送信
    #response = requests.post(url, headers=headers, data=json_data, cookies={"csrftoken": payload["csrfmiddlewaretoken"]})


def upload_parts(file_path=file_path,sesstion_ID=53533, urls=''):
    """
    ファイルを分割し、各部分をプリサインドURLにアップロードする
    :param file_path: アップロードするファイルのパス
    :param urls: 各パートのアップロード先URLのリスト
    """

    r = muc.do()

    session = r[0]
    csrf_token = r[1]

    url = 'https://app.move.ai/upload_video/' + str(sesstion_ID) + '/' + file_path.split('/')[-1] + '/?create_multipart=1'

    print ('url---',url)

    response = session.get(url)
    dictn = response.json()

    print(dictn)
    #{'status': 0, 'upload_id': 'GGWr1dXPvsOMo00KbMda7**NZzIVJAdoYyBKDQyJPfQ1snslEw--'}

    upload_id = dictn['upload_id']

    etag_list = []

    for i, data in enumerate(split_file(file_path)):

        part = i + 1 # パート番号

        nurl = 'https://app.move.ai/upload_video/' + str(sesstion_ID) + '/' + file_path.split('/')[-1] + '/?generate_multipart_presigned_url=1&upload_id=' + upload_id + '&part_no=' + str(part)
        #https://app.move.ai/upload_video/53533/cam01_test01.mp4/?generate_multipart_presigned_url=1&upload_id=ot1xKulzl43g--&part_no=1
        print ('\nnurl---',nurl)

        #処理を止める
        time.sleep(1)

        response = session.get(nurl)
        dictn = response.json()

        print(dictn)
        #{'status': 1, 'signed_url': 'https://s3.eu***-west4630'}

        response = session.put(dictn['signed_url'], data=data)
        #print(f"Status Code: {response.status_code}, URL: {urls[i]}")

        print (response.text)

        
        etag = response.headers['ETag']
        print ('etag---',etag)
        etag_list.append({"ETag": etag, "PartNumber": part})

        '''
        print(f"Uploading part {i+1} to {urls[i]}")
        response = requests.put(urls[i], data=data)
        print(f"Status Code: {response.status_code}, URL: {urls[i]}")

        print (response.text)

        
        etag = response.headers['ETag']
        print ('etag---',etag)


        if response.status_code != 200:
            print("Failed to upload part {i+1}")
            return False
         '''       
    #処理を止める
    time.sleep(1)
    furl = 'https://app.move.ai/upload_video/' + str(sesstion_ID) + '/' + file_path.split('/')[-1] + '/'

    dictn = meke_payload(csrf_token,etag_list,upload_id,file_path,sesstion_ID)
        

    #完了用のPOSTリクエストを送信
    r = session.post(furl, headers=dictn['headers'], data=dictn['json_data'], cookies=dictn['cookies'])  

    print (r.text)      
    return r



def upload_parts_old(file_path, urls):
    """
    ファイルを分割し、各部分をプリサインドURLにアップロードする
    :param file_path: アップロードするファイルのパス
    :param urls: 各パートのアップロード先URLのリスト
    """
    for i, data in enumerate(split_file(file_path)):
        print(f"Uploading part {i+1} to {urls[i]}")
        response = requests.put(urls[i], data=data)
        print(f"Status Code: {response.status_code}, URL: {urls[i]}")

        print (response.text)

        
        etag = response.headers['ETag']
        print ('etag---',etag)


        if response.status_code != 200:
            print("Failed to upload part {i+1}")
            return False
    return True



urls = [
    "https://s3.eu-westmp4?uploadId=SOUK_1rlFIfQXhUH1CFWVBYXSA1pPj0xv6_mUOy.yC7YBSeFAuCeXHn6m.7NFXaoEQ5tlKoVBj9l4TXVpN274wHQgj3cmPq4Iuj54k6nPQ85Q2anQqp3Vtr8QMAK9lRtL70hGfhSM79t1xKulzl43g--&partNumber=1&AWSAccessKeyId=ASIAZJHW76V2YATNYS6R&Signature=tNq9XGSqaRXTPwxtYVFJoXllhsE%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEDoaCWV1LXdlc3QtMSJIMEYCIQDsWiiO9%2Faohv%2FOx%2FCp%2F5ZtWryE8QS4KCEkg0BqKsgjUwIhAM%2FmRR72mLLn67orWZCNTSzdMarwpp1EMF1R0mvijK1aKrwFCHIQARoMNjM4MzIwNjM3MzAxIgxFUnnAn0iLCTg5k38qmQXwGHpkevj4WbQdfEE6N4UALK1L%2FV9vGqa6rebVaGCI2FVxNxiVAtSLATtiv39DwwZKsG5mtZkWRM0AH7NQn1tQ820GTtToyQtCmuIHaTrdU58D%2FdI6eY0%2BpNoo34ZP9NsXhep9Q6tQpjOaRGntQ3%2FhcOKV0lHu1mV10VW%2FdVmqLE4DTFGninzCAMs86hYa1UHD9DHsAMWkMWNff1DxRebLzzLNM2ZU%2B9Jf3FnBSB2hx4GMqtJoqzZY1cmSZYQ3dGGuO5Z5ZtAAsyfHF9cHdYvOOk5LJhC215XXATfW%2FF2CPkXDmcKTEPHGEtQk77YxIIA5kxEkKChrYwC07eXZNVUmQ%2FUTdOcQ88jEgK6HTBsrilXCK539uQgToF6p5ySgfCZfz9rpecxHZd6VgNdPT0Jgfswdbw8fWxC1FsnnwLx%2FcE1969tbu1XT6RKyALe%2BaSU%2FGYPghRN3q9T%2Ft7A5CIl%2Fek6sw4TxvUsWX%2FZHE8oKG5qg%2BWG8k7FHYUxG3oTl0vCg4tJKzSumsP7doy%2BaIzfh7JMnwXWU5WXACez2yr2P8G560nRBw7lSZQ%2BFrB1BDhTZHdKaHT1i%2Bb6egfV0YEEzto1Ngl4nvYDHgotwtBuWIfD6phuHhXAFxUgVqxWwTnphjfthHSXWMbHdNzzSn%2B4IndJJv4%2FyzbocO1g3nOV6%2BWRqxvsgQuN4PnL%2FY408ZjmalPc8xB8Ew5c7p636sTCraaDjQzntunNQcHHRl29YHuFu1u76aeIH4yW7UBp4MSX3yEaJGxc%2BY%2BGoOXq%2FqRwywX%2FPJNmpW%2BAfHSZpQxK%2Fv1zKmArMaHuloZtZypxRVkr6xcuTEQT0y9DMTv1KrPyT1WSySCxsNvDI1RZKYV%2F2p%2Fe0XiXuO7CZDzDvmumwBjqwAaDTZXgOXkbV4lRRp4H0RsVT3EqAA28EEzBDslGJa1wXwe9vwgj3vm4w1XVvgwcMtTwUk%2F%2BkA43bTndSD5shJJ42cK2xw9TPw75RH7eQzlJNC4UtNSwR3u%2BXLdFYCbq%2BcjreTJvT1VGw3JMfrpZX2K5%2B6Al%2Bw0FJdElK8JlHwgN4hLhmdMjY4SVxz3z8SvBg30ZTdzPV8G%2B2ckwJ8MEEnPEyYUduOBzg2NhyAcx4EYSF&Expires=1713272836",
    "https://s3.eu-we.mocap.prod/vipty/53533/videos/cam01_test01.mp4?uploadId=SOUK_1rlFIfQXhUH1CFWVBYXSA1pPj0xv6_mUOy.yC7YBSeFAuCeXHn6m.7NFXaoEQ5tlKoVBj9l4TXVpN274wHQgj3cmPq4Iuj54k6nPQ85Q2anQqp3Vtr8QMAK9lRtL70hGfhSM79t1xKulzl43g--&partNumber=2&AWSAccessKeyId=ASIAZJHW76V2XVAWALOC&Signature=zQjjbA5cRtNg81yQYU3lHby%2FbIU%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEDsaCWV1LXdlc3QtMSJGMEQCIA8HBq%2ByN70C4SRj1ZDADXg%2B43U68xNxSbUAZrHUXCMlAiAsKyU4WnwSqSkEMmhXGz7gUdUgtalzE4a%2BFf2loOLiESq8BQh0EAEaDDYzODMyMDYzNzMwMSIMsZuKRr%2BplbSLJ1dXKpkFoORffqjUfVRoXMGNrxlFCOVqqvtzCgl9qVrf8eWMxiNr9AVpVRewq6sqcEC2eHBT0rBRAOsPcxn7PvVhrdE405DepSx0ZelNoQAwE3KtRNRhpF17vw9bqhCTeixMYCqvy7YX15SXVzT%2FFAI9MH2ys1oVzIEXlLm7G2Qvv2ptDrpL353hLOPGAvobeFRmCyTU9i2jrk%2BzrRRp4m2tOoInui0XXCGBreHh5SKB3tOIbtKp7Z%2Fwq6WIb%2F17QKGedh%2BdqayBG0u4L5EHrfE14k0kUF3%2FJiexH3ZpLB9j6yjasGB2btDJ23k2%2BCmuobzs34xmaCU%2B1Ecd5brAp1AfbZ8jByOmAFPr%2F7oQSeQYRJ9ECBE6ejcyFB8AdGmnFpvEcK3P99zXbqCNkxvn%2BVL9eDVbtmjtNen6gTfrTKpAjNdzuxL7VVHMpZlU83yuMdsE2iRJZwnzHgUMN4oUg39V0cupTEyq57QQ%2BMHJKRzcdcBd6CbJ4AHF3BQmfdksBB%2FGa8lqDkGJvHdY97npG2FsSYuRIIfWe%2F%2FCG8X1gWc1HcwtDPRG%2B25hjINI2lULROq%2FgY0tSCGYJ7SJG%2FIC9Zq1o3mO5VBEDgd6qlgge7P6oPDC81bzffsP9yH8T9rgAjdEN5a14Vbkkn6sPo3QvoVWWDzPBV5MMXQJxE7I53U2Zv%2F%2F%2FBWhUHfQKUsHHRDuSfQ3ak%2FOtr84KyHPjZYx7sQ6dw7%2BzyGThpX0mSCAu9JpKvNC8f3WT3w0W%2FbtqsR9j36%2F2mpYjm1TvcdQIh50UqXh67H%2FGUDX3aQvXbYCRoXApSJLMzbfywgxdmgAXSuP8BGmTelG%2B5xecnvMpnV%2BZ6QUqKYhgyHhmB3kB0bDfKT4ww2s2QNwMo1xeph4Qzowos7psAY6sgFDnafTAQKF90mbc4XY84HW8VrjmOlC0shq%2BQto3j%2FGupCSGj5a03FhrNWLOzDTvzuA%2BH5VPrdoZigUuEbFRSwX3fE4pYtuGfLIwGAjAmGp%2FN0c1yEgsU2Y4hjoa86qvvYY%2BffMqJll%2FFmOGiBlITFjNcLNRIGBCDlP2IA4HkgmANDoeLxiyz8vgwo3f%2BXSbI2WZXoQ6jHsncm9%2FlIYsiIsOsitgbLhgRHDF8fNQgV5lf91&Expires=1713272852",
    # 他のパートのURLを追加...
]


'''
# ファイルの分割とアップロードを実行
if upload_parts(file_path, urls):
    print("All parts uploaded successfully")
else:
    print("An error occurred during the upload")

'''

