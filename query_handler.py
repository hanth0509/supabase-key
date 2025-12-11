from datetime import datetime, timedelta, date
from data_processor import get_transaction_stats, format_stats, find_highest_spending_category, format_currency
import random

def parse_date(date_str, date_format='%Y-%m-%d'):
    """Parse date string to date object"""
    if isinstance(date_str, date):
        return date_str
    try:
        return datetime.strptime(str(date_str), date_format).date()
    except (ValueError, TypeError):
        return None

def handle_question(question, transactions):
    if not question or not isinstance(question, str):
        return None, "Vui lòng nhập câu hỏi hợp lệ"
        
    question_lower = question.lower().strip()
    
    # Handle greetings first (chỉ khi cả câu là lời chào)
    greeting_phrases = [
        "xin chào",
        "xin chao",
        "hello",
        "hi",
        "chào",
        "chao",
        "chào bạn",
        "chao ban"
    ]
    if question_lower in greeting_phrases:
        greeting_responses = [
            "Chào bạn! Tôi có thể giúp gì bạn hôm nay?",
            "Xin chào! Bạn đang muốn xem chi tiêu hay thu nhập?",
            "Hello, mình có thể hỗ trợ bạn xem tổng tiền hoặc hóa đơn.",
            "Chào bạn, mình có thể giúp bạn phân tích chi tiêu theo tháng/năm.",
            "Xin chào! Hãy hỏi mình về tổng tiền, hóa đơn hoặc danh mục chi tiêu nhé."
        ]
        return None, random.choice(greeting_responses)
    
    # Detect finance / transaction-related question
    finance_keywords = [
        # General
        "tổng", "bao nhiêu", "tiền", "chi phí", "thu nhập", "thống kê",
        "đã chi", "đã thu", "số tiền", "hết bao nhiêu", "giao dịch",
        "income", "expense", "money", "spent", "earned", "tính", "tính tổng",
        "chi", "thu", "lương", "bill", "hóa đơn", "nhiều nhất", "cao nhất", "lớn nhất", "tốn kém nhất", "chi nhiều nhất", "ít nhất", "nhỏ nhất",
        # Time periods
        "hôm nay", "hôm qua", "tuần này", "tuần trước",
        "tháng này", "tháng trước", "năm nay", "năm ngoái",
        "3 tháng", "quý này", "quý trước",
        # Categories
        "nước", "điện", "tiền điện", "tiền nước", "hóa đơn điện", "hóa đơn nước",
        "ăn uống", "nhà hàng", "cà phê", "siêu thị", "chợ", "đi chợ",
        "xăng", "nhiên liệu", "gửi xe", "mua sắm", "quần áo", "giày dép",
        "giải trí", "xem phim", "du lịch", "khách sạn",
        "y tế", "khám bệnh", "bệnh viện", "thuốc men", "bảo hiểm",
        "học phí", "sách vở", "giáo dục",
        "tiền nhà", "tiền thuê", "tiền phòng", "tiền trọ", "điện nước",
        "internet", "mạng", "điện thoại", "truyền hình"
    ]
    has_finance_keyword = any(k in question_lower for k in finance_keywords)

    # Nếu câu hỏi KHÔNG liên quan tài chính → để main.py xử lý bằng LLM
    if not has_finance_keyword:
        return None, None

    # Từ đây trở xuống: CHỈ xử lý bằng dữ liệu giao dịch (Supabase)
    today = date.today()
    time_period = ""
    time_period_display = ""
    start_date = end_date = None

    # Time period detection
    if "hôm nay" in question_lower:
        start_date = today
        end_date = today
        time_period = f" ngày {today.strftime('%d/%m/%Y')}"
        time_period_display = f"ngày {today.strftime('%d/%m/%Y')}"
    elif "hôm qua" in question_lower:
        start_date = today - timedelta(days=1)
        end_date = start_date
        time_period = f" ngày {start_date.strftime('%d/%m/%Y')}"
        time_period_display = f"ngày {start_date.strftime('%d/%m/%Y')}"
    elif "tuần này" in question_lower:
        start_date = today - timedelta(days=today.weekday())
        end_date = today
        time_period = f" tuần này (từ {start_date.strftime('%d/%m')} đến {end_date.strftime('%d/%m/%Y')})"
        time_period_display = "tuần này"
    elif "tuần trước" in question_lower:
        end_date = today - timedelta(days=today.weekday() + 1)
        start_date = end_date - timedelta(days=6)
        time_period = f" tuần trước (từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')})"
        time_period_display = "tuần trước"
    elif "tháng này" in question_lower or "tháng nay" in question_lower:
        start_date = today.replace(day=1)
        end_date = today
        time_period = f" tháng {today.month}/{today.year}"
        time_period_display = f"tháng {today.month}/{today.year}"
    elif "tháng trước" in question_lower:
        first_day_current_month = today.replace(day=1)
        end_date = first_day_current_month - timedelta(days=1)
        start_date = end_date.replace(day=1)
        time_period = f" tháng {start_date.month}/{start_date.year}"
        time_period_display = f"tháng {start_date.month}/{start_date.year}"
    elif "năm nay" in question_lower:
        start_date = today.replace(month=1, day=1)
        end_date = today
        time_period = f" năm {today.year}"
        time_period_display = f"năm {today.year}"
    elif "năm ngoái" in question_lower:
        start_date = today.replace(year=today.year-1, month=1, day=1)
        end_date = today.replace(year=today.year-1, month=12, day=31)
        time_period = f" năm {today.year-1}"
        time_period_display = f"năm {today.year-1}"
    elif "3 tháng" in question_lower or "ba tháng" in question_lower or "quý này" in question_lower:
        end_date = today
        start_date = today - timedelta(days=90)
        time_period = f" 3 tháng gần đây (từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')})"
        time_period_display = "3 tháng gần đây"
    elif "quý trước" in question_lower:
        current_quarter = (today.month - 1) // 3 + 1
        if current_quarter == 1:
            start_date = today.replace(year=today.year-1, month=10, day=1)
            end_date = today.replace(year=today.year-1, month=12, day=31)
        else:
            start_month = ((current_quarter - 2) * 3) + 1
            start_date = today.replace(month=start_month, day=1)
            end_date = (start_date + timedelta(days=89)).replace(day=1) - timedelta(days=1)
        time_period = f" quý trước (từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')})"
        time_period_display = "quý trước"

    # Parse explicit month like "tháng 11" or "tháng 11/2025"
    if "tháng " in question_lower and start_date is None and end_date is None:
        import re
        match = re.search(r"tháng\s+(\d{1,2})(?:/(\d{4}))?", question_lower)
        if match:
            month = int(match.group(1))
            year = int(match.group(2)) if match.group(2) else today.year
            if 1 <= month <= 12:
                start_date = date(year, month, 1)
                # tính ngày cuối tháng
                if month == 12:
                    next_month = date(year + 1, 1, 1)
                else:
                    next_month = date(year, month + 1, 1)
                end_date = next_month - timedelta(days=1)
                time_period = f" tháng {month}/{year}"
                time_period_display = f"tháng {month}/{year}"

    # Câu hỏi "nhiều nhất" / "lớn nhất" phải xử lý TRƯỚC khi trả thống kê chung
    if any(x in question_lower for x in ["nhiều nhất", "cao nhất", "nhiều tiền nhất", "lớn nhất", "tốn kém nhất", "chi nhiều nhất"]):
        is_expense = any(x in question_lower for x in ["chi tiêu", "expense", "chi phí", "đã chi", "chi ra"])
        group = "expense" if is_expense else None

        category, amount = find_highest_spending_category(
            transactions,
            group_name=group,
            start_date=start_date,
            end_date=end_date
        )
        if not category or amount <= 0:
            return None, "Không đủ dữ liệu để trả lời."

        amount_fmt = format_currency(amount)
        period_text = f"{time_period_display} " if time_period_display else ""
        if is_expense:
            return amount, f"Bạn chi nhiều nhất cho {category} {period_text}là {amount_fmt}"
        else:
            return amount, f"Danh mục có số tiền lớn nhất {period_text}là {category} ({amount_fmt})"

    # Câu hỏi "ít nhất" / "nhỏ nhất" cho chi tiêu
    if any(x in question_lower for x in ["ít nhất", "nhỏ nhất"]):
        # Mặc định hiểu là chi tiêu nếu không nói rõ
        is_expense = any(x in question_lower for x in ["chi tiêu", "expense", "chi phí", "đã chi"]) or True
        if is_expense:
            stats = get_transaction_stats(
                transactions,
                group_name="expense",
                start_date=start_date,
                end_date=end_date
            )
            if not stats['by_category']:
                return None, "Không đủ dữ liệu để trả lời."

            # Tìm danh mục có chi tiêu nhỏ nhất > 0
            min_cat = None
            min_val = None
            for cat, val in stats['by_category'].items():
                if val <= 0:
                    continue
                if min_val is None or val < min_val:
                    min_val = val
                    min_cat = cat

            if not min_cat or min_val is None:
                return None, "Không đủ dữ liệu để trả lời."

            amount_fmt = format_currency(min_val)
            period_text = f"{time_period_display} " if time_period_display else ""
            return min_val, f"Danh mục bạn chi ít nhất {period_text}là {min_cat} ({amount_fmt})"

    # Thu nhập
    if any(x in question_lower for x in ["thu nhập", "lương", "income", "tiền lương"]):
        stats = get_transaction_stats(
            transactions,
            group_name="income",
            start_date=start_date,
            end_date=end_date
        )
        if stats['count'] == 0:
            return None, "Không đủ dữ liệu để trả lời."
        return stats['total'], format_stats(stats, time_period, "thu nhập")
    
    # Chi tiêu
    if any(x in question_lower for x in ["chi tiêu", "expense", "chi phí", "đã chi", "đã tiêu"]):
        stats = get_transaction_stats(
            transactions,
            group_name="expense",
            start_date=start_date,
            end_date=end_date
        )
        if stats['count'] == 0:
            return None, "Không đủ dữ liệu để trả lời."
        return stats['total'], format_stats(stats, time_period, "chi tiêu")
    
    # Map danh mục
    category_mapping = {
        # Tiện ích
        'nước': 'water',
        'tiền nước': 'water',
        'hóa đơn nước': 'water',
        'water bill': 'water',
        'điện': 'electricity',
        'tiền điện': 'electricity',
        'hóa đơn điện': 'electricity',
        'internet': 'internet',
        'mạng': 'internet',
        'điện thoại': 'phone',
        'di động': 'phone',
        'truyền hình': 'cable',
        'truyền hình cáp': 'cable',
        'tivi': 'cable',
        
        # Ăn uống
        'ăn uống': 'food',
        'thức ăn': 'food',
        'đồ ăn': 'food',
        'nhà hàng': 'restaurant',
        'quán ăn': 'restaurant',
        'cà phê': 'coffee',
        'nước uống': 'beverage',
        'đồ uống': 'beverage',
        
        # Mua sắm
        'mua sắm': 'shopping',
        'siêu thị': 'grocery',
        'đi chợ': 'grocery',
        'chợ': 'grocery',
        'quần áo': 'clothing',
        'thời trang': 'clothing',
        'giày dép': 'footwear',
        
        # Nhà ở
        'tiền nhà': 'rent',
        'thuê nhà': 'rent',
        'tiền thuê': 'rent',
        'tiền phòng': 'rent',
        'tiền trọ': 'rent',
        
        # Giao thông
        'xăng': 'gas',
        'dầu': 'gas',
        'nhiên liệu': 'gas',
        'đổ xăng': 'gas',
        'gửi xe': 'parking',
        'đậu xe': 'parking',
        
        # Giải trí
        'giải trí': 'entertainment',
        'xem phim': 'movies',
        'phim ảnh': 'movies',
        'game': 'gaming',
        'trò chơi': 'gaming',
        'thể thao': 'sports',
        'gym': 'fitness',
        'tập thể dục': 'fitness',
        
        # Y tế
        'y tế': 'healthcare',
        'khám bệnh': 'healthcare',
        'bệnh viện': 'healthcare',
        'thuốc men': 'medicine',
        
        # Giáo dục
        'giáo dục': 'education',
        'học phí': 'tuition',
        'sách vở': 'books',
        
        # Khác
        'quà tặng': 'gifts',
        'tiệc tùng': 'party',
        'sửa chữa': 'repairs',
        'bảo hiểm': 'insurance'
    }

    # So sánh hai danh mục trong cùng một khoảng thời gian
    # Ví dụ: "so sánh tiền điện và tiền nước tháng 11"
    if "so sánh" in question_lower or "so sanh" in question_lower:
        matched_categories = []  # danh sách (keyword, mapped_category)
        for keyword, category in category_mapping.items():
            if keyword in question_lower:
                if category not in [c for _, c in matched_categories]:
                    matched_categories.append((keyword, category))
            if len(matched_categories) >= 2:
                break

        if len(matched_categories) >= 2:
            (kw1, cat1), (kw2, cat2) = matched_categories[0], matched_categories[1]

            stats1 = get_transaction_stats(
                transactions,
                category_name=cat1,
                start_date=start_date,
                end_date=end_date
            )
            stats2 = get_transaction_stats(
                transactions,
                category_name=cat2,
                start_date=start_date,
                end_date=end_date
            )

            # Nếu cả hai đều không có giao dịch thì coi như không đủ dữ liệu
            if stats1['count'] == 0 and stats2['count'] == 0:
                return None, "Không đủ dữ liệu để trả lời."

            total1 = stats1['total'] if stats1['count'] > 0 else 0
            total2 = stats2['total'] if stats2['count'] > 0 else 0

            # Nếu cả hai đều 0 thì cũng xem như không có dữ liệu ý nghĩa
            if total1 == 0 and total2 == 0:
                return None, "Không đủ dữ liệu để trả lời."

            fmt1 = format_currency(total1)
            fmt2 = format_currency(total2)
            diff = abs(total1 - total2)
            diff_fmt = format_currency(diff) if diff != 0 else None

            period_text = f" {time_period_display}" if time_period_display else ""

            if total1 > total2:
                if diff_fmt:
                    return diff, f"Bạn chi cho {kw1}{period_text} nhiều hơn {kw2} là {diff_fmt} ({fmt1} so với {fmt2})."
                else:
                    return total1, f"Bạn chi cho {kw1}{period_text} nhiều hơn {kw2}."
            elif total2 > total1:
                if diff_fmt:
                    return diff, f"Bạn chi cho {kw2}{period_text} nhiều hơn {kw1} là {diff_fmt} ({fmt2} so với {fmt1})."
                else:
                    return total2, f"Bạn chi cho {kw2}{period_text} nhiều hơn {kw1}."
            else:
                # total1 == total2
                return total1, f"Bạn chi cho {kw1} và {kw2}{period_text} bằng nhau ({fmt1})."

    for keyword, category in category_mapping.items():
        if keyword in question_lower:
            stats = get_transaction_stats(
                transactions,
                category_name=category,
                start_date=start_date,
                end_date=end_date
            )
            if stats['count'] == 0:
                return None, "Không đủ dữ liệu để trả lời."
            return stats['total'], format_stats(stats, time_period, keyword)

    # Câu hỏi "nhiều nhất"
    if any(x in question_lower for x in ["nhiều nhất", "cao nhất", "nhiều tiền nhất"]):
        is_expense = any(x in question_lower for x in ["chi tiêu", "expense", "chi phí", "đã chi"])
        group = "expense" if is_expense else None
        
        category, amount = find_highest_spending_category(
            transactions,
            group_name=group,
            start_date=start_date,
            end_date=end_date
        )
        if not category or amount <= 0:
            return None, "Không đủ dữ liệu để trả lời."

        amount_fmt = format_currency(amount)
        period_text = f"{time_period_display} " if time_period_display else ""
        if is_expense:
            return amount, f"Bạn chi nhiều nhất cho {category} {period_text}là {amount_fmt}"
        else:
            return amount, f"Danh mục có số tiền lớn nhất {period_text}là {category} ({amount_fmt})"

    # Thống kê chung nếu vẫn là câu hỏi tài chính
    stats = get_transaction_stats(
        transactions,
        start_date=start_date,
        end_date=end_date
    )
    if stats['count'] == 0:
        return None, "Không đủ dữ liệu để trả lời."

    return stats['total'], format_stats(stats, time_period)