from datetime import datetime
from data_processor import calculate_total, find_highest_spending_category

def handle_question(question, transactions):
    """
    Xử lý câu hỏi và trả về kết quả tương ứng
    
    Args:
        question: Câu hỏi từ người dùng
        transactions: Danh sách giao dịch
        
    Returns:
        Tuple (tổng tiền, thông báo) hoặc (None, thông báo lỗi)
    """
    if not question or not isinstance(question, str):
        return None, "Vui lòng nhập câu hỏi hợp lệ"
        
    question_lower = question.lower().strip()
    
    # Xử lý câu hỏi về tổng giao dịch
    if "tổng" in question_lower:
        # Xác định khoảng thời gian nếu có
        time_period = None
        if "tháng này" in question_lower:
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            time_period = f" trong tháng {today.month}/{today.year}"
        elif "năm nay" in question_lower:
            today = datetime.now()
            start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            time_period = f" trong năm {today.year}"
        else:
            start_date = end_date = None
            time_period = ""
        
        # Xử lý theo nhóm (có thể có hoặc không có từ khóa 'nhóm')
        if any(x in question_lower for x in ["thu nhập", "income"]):
            total = calculate_total(transactions, group_name="income", start_date=start_date, end_date=end_date)
            return total, f"Tổng thu nhập{time_period}"
        
        if any(x in question_lower for x in ["chi tiêu", "expense"]):
            total = calculate_total(transactions, group_name="expense", start_date=start_date, end_date=end_date)
            return total, f"Tổng chi tiêu{time_period}"
            
        if any(x in question_lower for x in ["nợ", "vay", "debt", "loan"]):
            total = calculate_total(transactions, group_name="debt-loan", start_date=start_date, end_date=end_date)
            return total, f"Tổng nợ/vay{time_period}"
        
        # Xử lý theo danh mục cụ thể
        category_mapping = {
            'ăn uống': 'Food & Beverage',
            'food': 'Food & Beverage',
            'đồ ăn': 'Food & Beverage',
            'tiền điện': 'Electricity bill',
            'điện': 'Electricity bill',
            'electricity': 'Electricity bill',
            'tiền nước': 'Water bill',
            'nước': 'Water bill',
            'water': 'Water bill',
            'mua sắm': 'Shopping',
            'shopping': 'Shopping',
            'lương': 'Salary',
            'salary': 'Salary',
            'tiền thuê': 'Rentals',
            'rent': 'Rentals',
            'internet': 'Internet bill',
            'mạng': 'Internet bill',
            'sức khỏe': 'Health',
            'health': 'Health',
            'giải trí': 'Entertainment',
            'entertainment': 'Entertainment',
            'giáo dục': 'Education',
            'education': 'Education'
        }
        
        for keyword, category in category_mapping.items():
            if keyword in question_lower:
                total = calculate_total(
                    transactions, 
                    category_name=category,
                    start_date=start_date,
                    end_date=end_date
                )
                return total, f"Tổng {category.lower()}{time_period}"
        
        # Nếu không khớp với danh mục cụ thể, trả về tổng tất cả
        if not any(x in question_lower for x in ["của", "thuộc", "trong"]):
            total = calculate_total(transactions, start_date=start_date, end_date=end_date)
            return total, f"Tổng giao dịch{time_period}"
    
    # Xử lý câu hỏi về số dư hiện tại
    elif any(x in question_lower for x in ["số dư", "tiền hiện có", "current balance"]):
        total_income = calculate_total(transactions, group_name="income")
        total_expense = calculate_total(transactions, group_name="expense")
        balance = total_income - total_expense
        return balance, "Số dư hiện tại"
        
    # Xử lý câu hỏi về danh mục chi tiêu nhiều nhất
    elif any(x in question_lower for x in ["nhiều nhất", "nhiều tiền nhất", "tốn kém nhất"]) and any(x in question_lower for x in ["tháng", "tháng này", "tháng trước", "tháng qua"]):
        from datetime import datetime, timedelta
        
        # Xác định khoảng thời gian
        today = datetime.now()
        
        # Xử lý tháng được chỉ định (nếu có)
        month_match = None
        # Tìm số tháng trong câu hỏi (xử lý cả trường hợp có nhiều dấu cách)
        import re
        month_pattern = r"tháng\s*(\d{1,2})"
        match = re.search(month_pattern, question_lower)
        if match:
            try:
                month = int(match.group(1))
                if 1 <= month <= 12:
                    month_match = month
            except (ValueError, IndexError):
                pass
        
        if month_match is not None:
            # Xử lý tháng được chỉ định
            target_month = month_match
            target_year = today.year
            if today.month < target_month:  # Nếu tháng chỉ định đã qua trong năm trước
                target_year -= 1
                
            start_date = datetime(target_year, target_month, 1).strftime('%Y-%m-%d')
            if target_month == 12:
                end_date = datetime(target_year + 1, 1, 1).strftime('%Y-%m-%d')
            else:
                end_date = datetime(target_year, target_month + 1, 1).strftime('%Y-%m-%d')
            time_period = f"tháng {target_month}/{target_year}"
            
        elif any(x in question_lower for x in ["tháng này", "tháng nay"]):
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1).strftime('%Y-%m-%d')
            else:
                end_date = today.replace(month=today.month + 1, day=1).strftime('%Y-%m-%d')
            time_period = f"tháng {today.month}"
            
        elif any(x in question_lower for x in ["tháng trước"]):
            if today.month == 1:
                prev_month = 12
                year = today.year - 1
            else:
                prev_month = today.month - 1
                year = today.year
            start_date = today.replace(year=year, month=prev_month, day=1).strftime('%Y-%m-%d')
            end_date = today.replace(day=1).strftime('%Y-%m-%d')
            time_period = f"tháng {prev_month}"
            
        else:  # Mặc định là tháng hiện tại
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1).strftime('%Y-%m-%d')
            else:
                end_date = today.replace(month=today.month + 1, day=1).strftime('%Y-%m-%d')
            time_period = f"tháng {today.month}"
        
        print(f"[DEBUG] Tìm kiếm giao dịch từ {start_date} đến {end_date}")
            
        # Xác định xem có phải là chi tiêu hay không
        # Nếu câu hỏi có từ 'chi' hoặc 'chi tiêu' hoặc 'chi phí' thì mặc định là hỏi về chi tiêu
        is_expense = any(x in question_lower for x in ["chi", "chi tiêu", "chi phí", "expense", "tốn", "tiêu"]) \
                    and not any(x in question_lower for x in ["thu nhập", "lương", "income", "thu"])
        group = "expense" if is_expense else None
        
        # In thông tin debug
        print(f"[DEBUG] Tìm kiếm theo nhóm: {group}")
            
        # Tìm danh mục chi tiêu nhiều nhất
        category, amount = find_highest_spending_category(
            transactions, 
            group_name=group,
            start_date=start_date,
            end_date=end_date
        )
        
        if category and amount > 0:
            amount_fmt = "{:,} VND".format(int(amount))
            period_text = f"trong {time_period}" if time_period else ""
            
            if is_expense:
                return amount, f"Bạn chi nhiều nhất cho {category} {period_text}: {amount_fmt}"
            else:
                return amount, f"Danh mục có số tiền lớn nhất {period_text}: {category} ({amount_fmt})"
        else:
            period_text = f"trong {time_period} " if time_period else ""
            return 0, f"Không tìm thấy giao dịch {period_text}nào"
    
    # Nếu không khớp với bất kỳ mẫu nào, trả về None để sử dụng LLM
    return None, "Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể thử một trong các câu hỏi sau:\n" \
    "- Tổng thu nhập của tôi là bao nhiêu?\n" \
    "- Tôi đã chi bao nhiêu tiền điện tháng này?\n" \
    "- Tổng chi phí ăn uống của tôi?\n" \
    "- Số dư hiện tại của tôi là bao nhiêu?"
