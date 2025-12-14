import requests
import google.generativeai as genai
import time
import os


HF_API_TOKEN = "Bearer ISI_TOKEN_HUGGINGFACE_DISINI"
GEMINI_API_KEY = "ISI_API_KEY_GEMINI_DISINI"


try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Konfigurasi Gemini Error: {e}")


HF_API_URL = "https://router.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"

def analyze_sentiment(text):
    headers = {"Authorization": HF_API_TOKEN}
    try:
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": text})
        
        if response.status_code == 503:
            print("Model HF sedang loading, mencoba request ulang...")
            time.sleep(2)
            response = requests.post(HF_API_URL, headers=headers, json={"inputs": text})

        if response.status_code != 200:
            print(f"HF Error Code {response.status_code}: {response.text}")
            return {"label": "Neutral (Error)", "score": "0.00"}

        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], list): scores = data[0]
            else: scores = data
        else:
            return {"label": "Neutral", "score": "0.50"}

        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        top_result = sorted_scores[0]
        
        label_map = {"negative": "Negative", "neutral": "Neutral", "positive": "Positive"}
        final_label = label_map.get(top_result['label'].lower(), "Neutral")
        
        return {"label": final_label, "score": f"{top_result['score']:.2f}"}

    except Exception as e:
        print(f"Exception HF: {e}")
        return {"label": "Neutral (Fallback)", "score": "0.00"}

def extract_key_points(text):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Buatkan ringkasan poin-poin (pro dan kontra) dari review produk berikut dalam Bahasa Indonesia (Markdown):\n\n'{text}'"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Exception Gemini: {e}")
        if "429" in str(e):
            return "⚠️ (API Limit Reached) Kuota AI Google habis. Coba lagi nanti."
        return "Gagal mengambil ringkasan dari AI."