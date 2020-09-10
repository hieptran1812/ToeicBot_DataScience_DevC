from flask import Flask, request
import http.client
import mimetypes, json, requests

app = Flask(__name__)
@app.route('/') # this is the home page route
def hello_world(): # this is the home page function that generates the page code
    return "Các tính năng: \n * Tra từ \n * Đưa ra tài liệu tương ứng với mức điểm \n * Check grammar \n * dịch câu sang tiếng Việt "
    
@app.route('/webhook', methods=['POST'])
def webhook():
  # Lấy từ tiếng Anh mà người dùng nhập
  req_dialog = request.get_json(silent=True, force=True) # Đọc json 
  query_result = req_dialog.get('queryResult') # Lấy query result 
  action = query_result.get('action') # Lấy action
  #webhookstatus = req_dialog.get('webhookStatus') # Lấy trạng thái webhook
  #message_webhookstatus = webhookstatus.get('message') # Lấy thông tin message trong trạng thái webhook

  if action == "dich.cau.en2vi": # Khi yêu cầu là dịch câu từ tiếng Anh sang tiếng Việt
    parameters = query_result.get('parameters')
    text = parameters.get('any')

    conn = requests.post("https://google-translate1.p.rapidapi.com/language/translate/v2",
    data = {'source': 'en' ,'q' : text, 'target': 'vi'},
    headers = {
      'x-rapidapi-host': "google-translate1.p.rapidapi.com",
      'x-rapidapi-key': "4cb005e529msha0ca4328251c2bbp129110jsnc8a4e91b8b61",
      'accept-encoding': "application/gzip",
      'content-type': "application/x-www-form-urlencoded"
    })
    json_obj = conn.json()
    message = "Mình dịch câu đấy như này: " + str(json_obj["data"]["translations"][0]["translatedText"])
    message = message.replace("&quot;", "'") # thay thế dấu ""

  if action == "tai.lieu.luyen.thi": # Khi yêu cầu là cần tìm tài liệu ôn thi ứng với mức điểm
    parameters = query_result.get('parameters')
    muc_tieu = int(parameters.get('any'))
    message = "Với mục tiêu " + str(muc_tieu) + " thì tớ gửi bạn bộ tài liệu trong link này nha, hãy cứ từ từ tham khảo nhé ^^; "
    if muc_tieu == 0:
          message = "Chà sao mục tiêu lại là 0 được nhỉ :> Hãy đặt mục tiêu cao hơn nha bạn <3"
    elif muc_tieu > 0 and muc_tieu <= 350:
          message += "https://bit.ly/3jAj9Ws"
    elif muc_tieu > 350 and muc_tieu <= 550:
          message += "https://bit.ly/3gOEJVh" 
    elif muc_tieu > 550 and muc_tieu <= 750:
          message += "https://bit.ly/3hSmLTm" 
    elif muc_tieu > 750 and muc_tieu <= 990:
          message += "https://bit.ly/3bm0Ilj"
    else:
          message = "Trong TOEIC điểm chỉ có từ 0 đến 990 thôi nha bạn ^^ Đặt mục tiêu khác nha"

  if action == "kiemtracau": # Khi yêu cầu là kiểm tra câu
    parameters = query_result.get('parameters')
    text = parameters.get('any')

    conn = requests.post("https://grammarbot.p.rapidapi.com/check",
    data = {'text': text, 'language': 'en-US'},
    headers={
    'x-rapidapi-host': "grammarbot.p.rapidapi.com",
    'x-rapidapi-key': "344a355e6emsh1a277aff5097a05p1d18d3jsn008d668fc0d1",
    'content-type': "application/x-www-form-urlencoded"
    })

    json_obj = conn.json()
    if(len(json_obj["matches"]) == 0): # Độ dài matches bằng 0
          message = "Câu của bạn viết ok :D Không bị lỗi gì nha ^^"
    else:
          message = "Có " + str(len(json_obj["matches"])) + "vấn đề trong câu của bạn :< Mình sẽ liệt kê ra để bạn lưu ý nha; "
          for i,match in enumerate(json_obj["matches"]):
                message += "Vấn đề " + str(i+1) + "; "
                problem = "Mô tả lỗi chi tiết: " + str(match["message"]) + "; " # Lấy giá trị message để mô tả lỗi chi tiết
                short_message = "Mô tả lỗi ngắn gọn: " + str(match["shortMessage"]) # Lấy giá trị shortMessage để mô tả ngắn gọn lỗi
                replacement_message = "Bạn có thể sửa thành: "
                for j,replacement in enumerate(match["replacements"]): # Lấy giá trị replacements để sửa từ hoặc câu cho đúng
                      if j == len(match["replacements"])-1: # Nếu lỗi đó là lỗi cuối thì phải có dấu ;
                            replacement_message += str(replacement["value"]) + "; "
                      else:
                            replacement_message += str(replacement["value"]) + ", " 
                issue_type = "Loại lỗi: " + str(match["rule"]["issueType"]) + "; " # Lấy giá trị issueType tìm loại lỗi
                description = "Lưu ý: " + str(match["rule"]["description"]) # Lấy giá trị description mô tả lưu ý
                message += problem + short_message + replacement_message + issue_type + description # Tổng hợp các vấn đề 

  if action == "tratu": # Khi yêu cầu là tra từ
    parameters = query_result.get('parameters')
    word_id = parameters.get('any') # Lấy từ cần tra

    conn = http.client.HTTPSConnection("od-api.oxforddictionaries.com")
    payload = ''
    headers = {
      'app_id': 'b2e4a5f3',
      'app_key': '940ac4ef689187a30eaf9c2cbf0cdd97'
    }
    api = "/api/v2/entries/en-us/" + word_id
    conn.request("GET", api, payload, headers)
    res = conn.getresponse()
    data = res.read()
    json_obj = json.loads(data) # file json ket qua
    results = json_obj["results"] # lay key result 

    # Lay dinh nghia
    message = "Đây là kết quả cho bạn nha ^^; "

    # Lay dinh nghia
    for i, lexicalEntry in enumerate(results[0]["lexicalEntries"]):
          definitions = str(lexicalEntry["entries"][0]["senses"][0]["definitions"][0])
          message += "Định nghĩa " + str(i+1) + ": " + definitions + "; "

    # Lay file phat am
    #audio_file = str(results[0]["lexicalEntries"][0]["entries"][0]["pronunciations"][1]["audioFile"]) # Lấy audiofile
    #message += "Phát âm: " + audio_file + "; "

    # Lay vi du voi tung dinh nghia
    examples = results[0]["lexicalEntries"][0]["entries"][0]["senses"][0]["examples"][0]["text"] # Lấy ví dụ với từng câu
    message += "Ví dụ: " + examples + "; "

    synonyms = results[0]["lexicalEntries"][0]["entries"][0]["senses"][0]["synonyms"] # Lấy các từ đồng nghĩa

    synonyms_list = []
    for i, synonym in enumerate(synonyms):
          synonyms_list.append(synonyms[i]["text"])

    message += "Từ đồng nghĩa: " + str(synonyms_list)
    print(message)
    
    #if "Webhook call failed" in str(message_webhookstatus): # Trường hợp lỗi từ từ điển
          #message = "Chà từ đó bị lỗi trong bộ nhớ của tớ rồi :< Tớ sẽ bảo đội kĩ thuật check sớm nhất nha :3"

  return {
    "fulfillmentText": message,
    "displayText": '25',
    "source": "webhookdata_repl.it"
  }

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)