# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("GOOGLE_API_KEY")

# def ask_gemini(prompt: str):
#     """Gọi Gemini để sinh câu lệnh SQL"""
#     url = "https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText"
#     payload = {
#         "prompt": {"text": prompt},
#         "temperature": 0.2,
#         "max_output_tokens": 300
#     }
#     try:
#         response = requests.post(f"{url}?key={API_KEY}", json=payload)
#         response.raise_for_status()
#         data = response.json()
#         return data["candidates"][0]["output"]
#     except Exception as e:
#         print("Lỗi Gemini API:", e)
#         return None

# llm_client.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def ask_gemini(prompt: str):
    url = "https://generativelanguage.googleapis.com/v1beta2/models/embedding-gecko-001:generateText"  # Thay bằng model text nếu có
    payload = {
        "prompt": {"text": prompt},
        "temperature": 0.2,
        "max_output_tokens": 300
    }
    try:
        response = requests.post(f"{url}?key={API_KEY}", json=payload)
        response.raise_for_status()
        data = response.json()
        # Nếu text model trả về khác, bạn chỉnh key trả về cho đúng
        return data.get("candidates", [{}])[0].get("output", "❌ Không có phản hồi từ Gemini")
    except Exception as e:
        print("Lỗi Gemini API:", e)
        return "❌ Lỗi khi gọi Gemini API."
