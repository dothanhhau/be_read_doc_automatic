from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json
import base64
load_dotenv()

genai.configure(api_key=str(os.getenv('GOOGLE_API_KEY')))
model = genai.GenerativeModel(str(os.getenv('MODLE_GEMINI')))

app = Flask(__name__)

@app.route('/')
def home():
  return 'Xin chào server này dành cho môn cô Liên: Thực hành thiết kế hệ thống'

@app.route('/api/texttospeech', methods=['POST'])
def tts():
  url = str(os.getenv('URL_TTS'))

  data = {
    "text": request.form.get('text'),
    "lang": request.form.get('lang'),
    "gender": request.form.get('gender')
  }

  if data['lang'] == "MALE":
    name = str(os.getenv('VOICE_NAME_MALE'))
  else:
    name = str(os.getenv('VOICE_NAME_FEMALE'))

  payload = {
    "input": {"text": data['text']},
    "voice": {
      "languageCode": data['lang'],
      "ssmlGender": data['gender'],
      "name": name
    },
    "audioConfig": {
      "audioEncoding": "MP3"
    }
  }

  headers = {
    "Content-Type": "application/json",
  }

  params = {
    "key": str(os.getenv('GOOGLE_API_KEY'))
  }

  try:
    response = requests.post(url, headers=headers, params=params, data=json.dumps(payload))

    if response.status_code == 200:
      audio_content = response.json()['audioContent']
      audio_data = base64.b64decode(audio_content)
      return jsonify(status=200, data=str(audio_data))
    else:
      return jsonify(status=response.status_code, data=response.text)
  except Exception as e:
    return jsonify(status=500, data=e)
    

@app.route('/api/summary', methods=['POST'])
def summary():
  data = {
    "text": request.form.get('text'),
    "prompt": "Tóm tắt đoạn văn dưới đây cho tôi. Tuỳ thuộc vào ngôn ngữ của đoạn text bên dưới. Nếu tiếng việt thì trả về tiếng việt, tiếng anh thì trả về tiếng anh, ..."
  }
  try:
    response = model.generate_content(str(data['prompt'] + '\n' + data['text']))
    return jsonify(status=200, data=response.text)
  except Exception as e:
    return jsonify(status=500, data=e)
    

@app.route('/api/translate', methods=['POST'])
def trans():
  url = str(os.getenv('URL_TRANSLATE'))
  payload = {
    'q': request.form.get('text'),
    'target': request.form.get('lang'),
    'key': str(os.getenv('GOOGLE_API_KEY'))
  }
  
  try:
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
      result = response.json()
      return jsonify(status=200, data=result['data']['translations'][0]['translatedText'])
    else:
      return jsonify(status=response.status_code, data=response.text)
  except Exception as e:
    return jsonify(status=500, data=e)


if __name__ == '__main__':
    app.run(debug=True)
