from datetime import datetime

# Mapping keyword → bảng/cột
CATEGORY_MAPPING = {
    "water bill": "Water bill",
    "electricity bill": "Electricity bill",
    "internet bill": "Internet bill",
    "shopping": "Shopping",
    "salary": "Salary"
}

def generate_sql_from_question(question: str):
    """
    Sinh SQL từ câu hỏi dựa trên mapping keywords → cột categoryname.
    """
    question_lower = question.lower()

    # Tìm category phù hợp
    category = None
    for key, value in CATEGORY_MAPPING.items():
        if key in question_lower:
            category = value
            break

    if category is None:
        return None  # Không tìm thấy category

    # Kiểm tra tháng/năm trong câu hỏi (ví dụ: 'tháng này')
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1).strftime("%Y-%m-%d")
    end_date = datetime(now.year, now.month, 28).strftime("%Y-%m-%d")  # tạm lấy 28, hoặc tính end of month

    sql = f"""
SELECT SUM(t.amount) as total
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE c.categoryname = '{category}'
  AND t.date >= '{start_date}'
  AND t.date <= '{end_date}';
"""
    return sql
