def build_prompt(user_email, transactions, question):
    context_lines = []
    for t in transactions:
        date = t.get("date")
        amount = t.get("amount")
        cate = t.get("categories", {}).get("categoryname", "Unknown")
        context_lines.append(f"{date}: {cate} - {amount} VND")

    context_text = "\n".join(context_lines) if context_lines else "Không có giao dịch nào."

    prompt = f"""
Bạn là trợ lý phân tích tài chính cá nhân cho ứng dụng quản lý chi tiêu.

QUY TẮC:
1. Nếu người dùng hỏi về chi tiêu, hóa đơn, số tiền, tổng tiền, theo ngày/tháng/năm:
   - Bạn CHỈ được sử dụng dữ liệu tại phần "DỮ LIỆU SUPABASE" (danh sách giao dịch bên dưới).
   - Phải tính toán chính xác, không được bịa số liệu.
   - Nếu không đủ dữ liệu thì phải trả lời đúng câu: "Không đủ dữ liệu để trả lời.".

2. Nếu câu hỏi không liên quan đến tài chính:
   - Trả lời như một chatbot bình thường.
   - Có thể sáng tạo và nói chuyện thoải mái.

DỮ LIỆU SUPABASE CỦA NGƯỜI DÙNG {user_email}:
{context_text}

CÂU HỎI CỦA NGƯỜI DÙNG:
{question}
"""
    return prompt
