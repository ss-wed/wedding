import smtplib
import base64
import ssl
from email.mime.text import MIMEText
from email.utils import formatdate
from google.cloud import firestore
from flask import request, jsonify


class SMTPAccess():
    def __init__(self):
        pass

    def __del__(self):
        pass

    def sendSMTPMessage(self, data):
        # gmailアカウント
        MAIL_ADDRESS = 'wedding.siakyea@gmail.com'
        PASSWORD = "lcazigiuibvyuxig"
        SYSTEM_ADDRESS = 'sakura-nanovn-385@docomo.ne.jp'

        # MIMEメッセージ作成
        message = "当日はぜひ楽しい時間をお過ごしください\n" + \
                  "お会いできることを楽しみにしております\n\n" if data['attendance'] else "\n"
        main_text = data['name'] + " 様\n\n" + \
                    "この度は　ご回答いただきありがとうございました\n" + \
                    message + \
                    "■登録情報\n" + \
                    "お名前　：" + data['name'] + " \n" + \
                    "アドレス：" + data['mail_address'] + " \n" + \
                    "出欠　　：" + ("出席" if data['attendance'] else "欠席") + " \n\n" + \
                    "※登録情報に誤りがある場合には、お手数ですが下記までお問い合わせください。\n" + \
                    "※当メールはシステムより自動配信されております。当アドレスにご連絡いただいてもご返信できませんので予めご了承ください。\n\n" + \
                    "今後ともよろしくお願い申し上げます。\n\n" + \
                    "■□■───────────────────\n" + \
                    "池田将汰・菱川紗也子\n" + \
                    "連絡先：sakura-nanovn-385@docomo.ne.jp\n" + \
                    "LINEID(将汰)：lt0223sv\n" + \
                    "LINEID(紗也子)：saya3917\n" + \
                    "──────────────────────\n\n"
        msg = MIMEText(main_text)
        # msg = MIMEText(main_text, "plain", "utf-8")
        msg.replace_header("Content-Transfer-Encoding", "base64")
        msg["Subject"] = "出欠登録を受け付けました"
        msg["From"] = MAIL_ADDRESS
        msg["To"] = data['mail_address']
        msg["Cc"] = ""
        msg["Bcc"] = ""
        msg["Date"] = formatdate(None,True)
        print(msg)

        # MIMEメッセージ作成(確認用)
        conf_text = "出欠登録が1件ありました。\n\n" + \
                    "■登録情報\n" + \
                    "お名前　：" + data['name'] + " \n" + \
                    "アドレス：" + data['mail_address'] + " \n" + \
                    "出欠　　：" + ("出席" if data['attendance'] else "欠席") + " \n" + \
                    "" + data['message'] + " \n\n"
        conf_msg = MIMEText(conf_text)
        conf_msg.replace_header("Content-Transfer-Encoding", "base64")
        conf_msg["Subject"] = "出欠登録を受け付けました"
        conf_msg["From"] = MAIL_ADDRESS
        conf_msg["To"] = SYSTEM_ADDRESS
        conf_msg["Cc"] = ""
        conf_msg["Bcc"] = ""
        conf_msg["Date"] = formatdate(None,True)

        # メールサーバにログイン
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587, timeout=10) # ("通信方式", port番号)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(MAIL_ADDRESS, PASSWORD)

        # メール送信
        smtpobj.send_message(msg)
        smtpobj.send_message(conf_msg)
        smtpobj.quit()


def register(request):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)
    elif request.method != 'POST':
        return 'only POST'

    # 引数取得
    data = request.get_json()

    # メール送信機能は一旦コメントアウト
    mail = SMTPAccess()
    mail.sendSMTPMessage(data)

    # DB登録
    db = firestore.Client()
    batch = db.batch()
    collection = db.collection('participant')
    doc_ref = collection.document(data['name'])
    info = {
        'attendance': data['attendance'],
        'postcode': data['postcode'],
        'address': data['address'],
        'building': data['building'],
        'mail_address': data['mail_address'],
        'phone_number': data['phone_number'],
        'allergy': data['allergy'],
        'message': data['message'],
        'companion_list': data['companion_list'],
    }
    batch.set(doc_ref, info)
    batch.commit()

    res = jsonify({'result': True})
    res.headers.set('Access-Control-Allow-Origin', '*')

    return res