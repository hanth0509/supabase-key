def build_prompt(user_email, transactions, question):
    context_lines = []
    for t in transactions:
        date = t.get("date")
        amount = t.get("amount")
        cate = t.get("categories", {}).get("categoryname", "Unknown")
        context_lines.append(f"{date}: {cate} - {amount} VND")

    context_text = "\n".join(context_lines) if context_lines else "Không có giao dịch nào."

    prompt = f"""
Bạn là trợ lý tài chính cá nhân.

Dữ liệu giao dịch của người dùng {user_email}:
{context_text}

Câu hỏi: {question}

Hướng dẫn trả lời:
- Nếu câu hỏi liên quan dữ liệu giao dịch, trả lời **ngắn gọn, trực tiếp, chỉ đưa kết quả cuối cùng**.
- Nếu câu hỏi không liên quan dữ liệu, trả lời ngắn gọn, thân thiện.
- Không giải thích quá trình hay viết dài dòng.
"""
    return prompt
