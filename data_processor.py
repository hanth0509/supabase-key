def calculate_total(transactions, group_name=None, category_name=None, start_date=None, end_date=None):
    """
    Tính tổng số tiền từ danh sách giao dịch dựa trên các điều kiện lọc
    """
    total = 0.0
    matched_count = 0
    
    if not transactions:
        print("[DEBUG] Không có giao dịch nào để xử lý")
        return total
    
    # Chuẩn hóa tên nhóm và danh mục để so sánh không phân biệt hoa thường
    target_group = group_name.lower() if group_name else None
    target_category = category_name.lower() if category_name else None
    
    for t in transactions:
        try:
            # Lấy thông tin giao dịch
            amount = float(t.get('amount', 0))
            t_date = t.get('date')
            
            # Lấy thông tin category và group
            category = t.get('category', {}) or {}
            
            # Lấy tên category từ nhiều trường có thể có
            cname = (
                category.get('name') or 
                category.get('categoryname') or 
                t.get('category_name') or 
                ''
            ).strip().lower()
            
            # Lấy tên nhóm từ nhiều trường có thể có
            grp = (
                t.get('group') or 
                category.get('group') or 
                t.get('group_name') or 
                ''
            ).lower()
            
            # Debug thông tin chi tiết
            print(f"[DEBUG] Category data: {category}")
            print(f"[DEBUG] Transaction data: {t}")
            print(f"[DEBUG] Extracted category: {cname}, group: {grp}")
            
            # Debug log
            debug_info = (
                f"\n[DEBUG] Xử lý giao dịch {t.get('id')}:\n"
                f"- Số tiền: {amount:,.0f}\n"
                f"- Ngày: {t_date}\n"
                f"- Danh mục: {cname}\n"
                f"- Nhóm: {grp}"
            )
            
            # Lọc theo group_name nếu có
            if target_group and grp != target_group:
                print(f"{debug_info}\n  => BỎ QUA (nhóm không khớp: '{grp}' != '{target_group}')")
                continue
            
            # Lọc theo category_name nếu có
            if target_category:
                if not cname:
                    print(f"{debug_info}\n  => BỎ QUA (không có thông tin danh mục)")
                    continue
                if target_category not in cname:
                    print(f"{debug_info}\n  => BỎ QUA (danh mục '{cname}' không khớp với '{target_category}')")
                    continue
            
            # Lọc theo ngày nếu có
            if start_date and t_date and t_date < start_date:
                print(f"{debug_info}\n  => BỎ QUA (ngày {t_date} trước {start_date})")
                continue
                
            if end_date and t_date and t_date > end_date:
                print(f"{debug_info}\n  => BỎ QUA (ngày {t_date} sau {end_date})")
                continue

            # Nếu đến đây, giao dịch thỏa mãn tất cả điều kiện
            total += amount
            matched_count += 1
            print(f"{debug_info}\n  => THÊM VÀO TỔNG: {amount:,.0f} (tổng hiện tại: {total:,.0f})")

        except Exception as e:
            print(f"[ERROR] Lỗi khi xử lý giao dịch: {e}")
            continue

    print(f"\n[DEBUG] Kết thúc tính tổng:\n- Số giao dịch phù hợp: {matched_count}\n- Tổng cộng: {total:,.0f} VND")
    return total

def get_transaction_stats(transactions, group_name=None, category_name=None, start_date=None, end_date=None):
    """
    Get detailed statistics for transactions matching the given filters
    Returns: {
        'total': float,
        'count': int,
        'by_category': {category: amount},
        'by_month': {month: amount},
        'average': float
    }
    """
    stats = {
        'total': 0.0,
        'count': 0,
        'by_category': {},
        'by_month': {},
        'average': 0.0
    }
    
    if not transactions:
        return stats
    
    target_group = group_name.lower() if group_name else None
    target_category = category_name.lower() if category_name else None
    
    for t in transactions:
        try:
            # Get transaction details
            amount = float(t.get('amount', 0))
            t_date = t.get('date')
            
            # Handle different possible category field names
            category = (
                t.get('category', {}).get('name') or 
                t.get('category_name') or 
                t.get('categories', {}).get('name') or 
                t.get('categories', {}).get('categoryname') or 
                ''
            ).lower().strip()
            
            # Handle different possible group field names
            group = (
                t.get('group') or 
                t.get('group_name') or 
                t.get('categories', {}).get('group_name') or 
                ''
            ).lower().strip()
            
            # Debug info
            print(f"[DEBUG] Processing transaction - Amount: {amount}, Date: {t_date}, Category: {category}, Group: {group}")
            
            # Apply filters
            if target_group and group != target_group:
                continue
            if target_category and target_category not in category:
                continue
            if start_date and t_date and isinstance(t_date, str):
                try:
                    from datetime import datetime
                    t_date = datetime.strptime(t_date, '%Y-%m-%d').date()
                except:
                    pass
            if start_date and t_date and hasattr(t_date, 'date'):
                if t_date.date() < start_date:
                    continue
            if end_date and t_date and hasattr(t_date, 'date'):
                if t_date.date() > end_date:
                    continue
            
            # Update statistics
            stats['total'] += amount
            stats['count'] += 1
            
            # Update category stats
            if category:
                stats['by_category'][category] = stats['by_category'].get(category, 0) + amount
            
            # Update monthly stats
            if t_date:
                try:
                    if hasattr(t_date, 'strftime'):
                        month_key = t_date.strftime('%Y-%m')
                    else:
                        month_key = t_date[:7]  # Assuming format YYYY-MM-DD
                    stats['by_month'][month_key] = stats['by_month'].get(month_key, 0) + amount
                except Exception as e:
                    print(f"[WARNING] Could not process date {t_date}: {e}")
                    
        except Exception as e:
            print(f"[ERROR] Error processing transaction: {e}")
            continue
    
    # Calculate average
    if stats['count'] > 0:
        stats['average'] = stats['total'] / stats['count']
    
    # Sort categories by amount (descending)
    stats['by_category'] = dict(sorted(
        stats['by_category'].items(), 
        key=lambda x: x[1], 
        reverse=True
    ))
    
    return stats

def format_currency(amount):
    """Format number as currency"""
    if amount is None:
        return "0 VND"
    return "{:,.0f} VND".format(amount)

def format_stats(stats, time_period="", category_name=None):
    """Format statistics into a human-readable string"""
    if stats['count'] == 0:
        return "Không tìm thấy giao dịch phù hợp."
    
    lines = []
    total = format_currency(stats['total'])
    avg = format_currency(stats['average'])
    
    if category_name:
        lines.append(f"📊 Thống kê cho {category_name}{time_period}:")
        lines.append(f"• Tổng cộng: {total}")
    else:
        lines.append(f"📊 Thống kê giao dịch{time_period}:")
        lines.append(f"• Tổng số tiền: {total}")
        lines.append(f"• Số giao dịch: {stats['count']}")
        if stats['count'] > 0:
            lines.append(f"• Trung bình: {avg}/giao dịch")
    
    # Add category breakdown if available
    if len(stats['by_category']) > 1:
        lines.append("\n📋 Chi tiết theo danh mục:")
        for cat, amount in stats['by_category'].items():
            percent = (amount / stats['total']) * 100 if stats['total'] > 0 else 0
            lines.append(f"  • {cat.title()}: {format_currency(amount)} ({percent:.1f}%)")
    
    # Add monthly trend if available
    if len(stats['by_month']) > 1:
        lines.append("\n📈 Xu hướng theo tháng:")
        for month in sorted(stats['by_month'].keys()):
            amount = stats['by_month'][month]
            lines.append(f"  • {month}: {format_currency(amount)}")
    
    return "\n".join(lines)

def find_highest_spending_category(transactions, group_name=None, start_date=None, end_date=None):
    """Find the category with the highest spending.

    Args:
        transactions: Danh sách các giao dịch.
        group_name: Tên nhóm cần lọc ('income', 'expense', 'debt-loan'), có thể None.
        start_date: Ngày bắt đầu (datetime.date), tùy chọn.
        end_date: Ngày kết thúc (datetime.date), tùy chọn.

    Returns:
        Tuple (tên danh mục, số tiền) hoặc (None, 0) nếu không tìm thấy.
    """
    if not transactions:
        print("[DEBUG] Không có giao dịch nào để xử lý")
        return None, 0

    category_totals = {}

    for t in transactions:
        try:
            # Lấy thông tin category và group
            cat = t.get("categories", {}) or {}
            group = (cat.get("group_name") or "").strip().lower()
            category = (cat.get("categoryname") or "Khác").strip()

            # Lọc theo group_name nếu có
            if group_name and group_name.lower() != group:
                continue

            # Lọc theo ngày nếu có
            t_date = t.get("date")
            if t_date and isinstance(t_date, str):
                try:
                    from datetime import datetime
                    t_date = datetime.strptime(t_date, "%Y-%m-%d").date()
                except Exception:
                    t_date = None
            elif t_date and hasattr(t_date, "date"):
                # Trường hợp datetime
                t_date = t_date.date()

            if start_date and t_date and t_date < start_date:
                continue
            if end_date and t_date and t_date > end_date:
                continue

            # Tính tổng theo danh mục
            try:
                amount = float(t.get("amount", 0))
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount
            except (ValueError, TypeError):
                continue

        except Exception as e:
            print(f"[ERROR] Lỗi khi xử lý giao dịch {t.get('id')}: {str(e)}")
            continue

    # Tìm danh mục có số tiền lớn nhất
    if not category_totals:
        return None, 0

    max_category = max(category_totals.items(), key=lambda x: x[1])
    return max_category[0], max_category[1]
