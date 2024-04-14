import os
import configparser

def manage_tool_settings():
    # ファイルのパスを指定
    config_file = 'tool_setting.ini'
    
    # ConfigParserのインスタンスを作成
    config = configparser.ConfigParser()
    
    # tool_setting.iniファイルの存在を確認
    if not os.path.exists(config_file):
        # ファイルが存在しない場合、デフォルト設定を作成
        config['DEFAULT'] = {
            'moveai_user': 'temp@temp.com',
            'moveai_pass': 'password',
            'PYPPETEER_CHROMIUM_REVISION': '1263111'
        }
        # ファイルに書き込む
        with open(config_file, 'w') as configfile:
            config.write(configfile)
            os.startfile(os.path.dirname(os.path.abspath(config_file)))
            return None
        raise Exception("Config file 'tool_setting.ini' was not found. A new one has been created with default values.")
        # 設定の場所をエクスプローラーで開く
        

    else:
        # ファイルが存在する場合、設定を読み込む
        config.read(config_file)

        print(dict(config['DEFAULT']))

        dictn = dict(config['DEFAULT'])

        # 環境変数として設定を格納

        for key in dictn:
            os.environ[key.upper()] = dictn[key]
            print(key.upper(), os.environ[key.upper()])
            # Python変数にも格納
            globals()[key] = dictn[key]

        # 読み込んだ情報を表示（デバッグ用）
        return dictn
        
# 関数を実行して結果を表示
#manage_tool_settings()
