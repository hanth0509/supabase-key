import subprocess

def ask_ollama(prompt, model="deepseek-r1:7b"):
    try:
        process = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,               # text mode
            encoding="utf-8"          # ← quan trọng
        )
        stdout, stderr = process.communicate(prompt + "\n")
        if stderr:
            print("Lỗi Ollama:", stderr)
        return stdout.strip()
    except Exception as e:
        print("Lỗi Ollama:", e)
        return "❌ Lỗi khi gọi Ollama."