def calculate_total(transactions, group_name=None, category_name=None, start_date=None, end_date=None):
    """
    Tính tổng số tiền từ danh sách giao dịch dựa trên các điều kiện lọc
    
    Args:
        transactions: Danh sách các giao dịch
        group_name: Tên nhóm cần lọc ('Income', 'Expense', 'Debt-Loan')
        category_name: Tên danh mục cần lọc
        start_date: Ngày bắt đầu (tùy chọn)
        end_date: Ngày kết thúc (tùy chọn)
    """
    total = 0.0  # Sử dụng float để xử lý số thập phân
    matched_count = 0
    
    if not transactions:
        print("[DEBUG] Không có giao dịch nào để xử lý")
        return total
    
    # Chuẩn hóa tên nhóm và danh mục để so sánh không phân biệt hoa thường
    # Lưu nguyên gốc group_name và category_name cho mục đích hiển thị
    target_group = group_name.strip().lower() if group_name else None
    target_category = category_name.strip().lower() if category_name else None
    
    for t in transactions:
        try:
            # Lấy thông tin category và group
            cat = t.get("categories", {}) or {}
            # Lưu nguyên gốc group_name để hiển thị
            grp_display = (cat.get("group_name") or "").strip()
            # Chuyển về chữ thường để so sánh
            grp = grp_display.lower()
            cname = (cat.get("categoryname") or "").strip().lower()
            
            # Debug log
            debug_info = (
                f"\n[DEBUG] Xử lý giao dịch {t.get('id')}:"
                f"\n- Số tiền: {t.get('amount')}"
                f"\n- Ngày: {t.get('date')}"
                f"\n- Danh mục: {cname or 'N/A'}"
                f"\n- Nhóm: {grp or 'N/A'}"
            )
            
            # Lọc theo group_name nếu có
            if target_group:
                # Kiểm tra không phân biệt hoa thường
                if not grp or target_group != grp:
                    print(f"{debug_info}\n  => BỎ QUA (nhóm '{grp_display}' không khớp với '{group_name}')")
                    continue
            
            # Lọc theo category_name nếu có
            if target_category and target_category not in cname:
                print(f"{debug_info}\n  => BỎ QUA (không khớp danh mục: {category_name})")
                continue
            
            # Lọc theo ngày nếu có
            t_date = t.get("date")
            if start_date and t_date and t_date < start_date:
                print(f"{debug_info}\n  => BỎ QUA (trước ngày {start_date})")
                continue
            if end_date and t_date and t_date > end_date:
                print(f"{debug_info}\n  => BỎ QUA (sau ngày {end_date})")
                continue
            
            # Tính tổng nếu thỏa tất cả điều kiện
            try:
                amount = float(t.get("amount", 0))
                total += amount
                matched_count += 1
                print(f"{debug_info}\n  => THÊM VÀO TỔNG: {amount:,.0f} (tổng hiện tại: {total:,.0f})")
            except (ValueError, TypeError) as e:
                print(f"{debug_info}\n  => LỖI: Không thể chuyển đổi số tiền: {t.get('amount')}")
                continue
                
        except Exception as e:
            print(f"[ERROR] Lỗi khi xử lý giao dịch {t.get('id')}: {str(e)}")
            continue
    
    print(f"\n[DEBUG] Kết thúc tính tổng:")
    print(f"- Số giao dịch phù hợp: {matched_count}")
    print(f"- Tổng cộng: {total:,.0f} VND")
    
    return total

def find_highest_spending_category(transactions, group_name=None, start_date=None, end_date=None):
    """
    Tìm danh mục có số tiền chi tiêu cao nhất
    
    Args:
        transactions: Danh sách các giao dịch
        group_name: Tên nhóm cần lọc ('income', 'expense', 'debt-loan')
        start_date: Ngày bắt đầu (tùy chọn)
        end_date: Ngày kết thúc (tùy chọn)
        
    Returns:
        Tuple (tên danh mục, số tiền) hoặc (None, 0) nếu không tìm thấy
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
