import os
from typing import List, Dict, Any, Optional
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Lấy thông tin người dùng bằng email
    
    Args:
        email: Email của người dùng
        
    Returns:
        Thông tin người dùng hoặc None nếu không tìm thấy
    """
    try:
        res = supabase.table("users").select("*").eq("username", email).execute()
        if res.data:
            print(f"[DEBUG] Tìm thấy user: {res.data[0]['id']}")
            return res.data[0]
        print(f"[DEBUG] Không tìm thấy user với email: {email}")
        return None
    except Exception as e:
        print(f"[ERROR] Lỗi khi lấy thông tin user: {str(e)}")
        return None

def get_wallets_by_user_id(user_id: str) -> List[Dict[str, Any]]:
    """
    Lấy danh sách ví của người dùng
    
    Args:
        user_id: ID của người dùng
        
    Returns:
        Danh sách các ví của người dùng
    """
    try:
        res = supabase.table("wallets").select("*").eq("user_id", user_id).execute()
        wallets = res.data if res.data else []
        print(f"[DEBUG] Số lượng ví tìm thấy: {len(wallets)}")
        for wallet in wallets:
            print(f"  - Ví {wallet['id']}: {wallet.get('name', 'Không có tên')}")
        return wallets
    except Exception as e:
        print(f"[ERROR] Lỗi khi lấy danh sách ví: {str(e)}")
        return []

def get_transactions_by_wallet_ids(wallet_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Lấy danh sách giao dịch theo danh sách ID ví
    
    Args:
        wallet_ids: Danh sách ID ví cần lấy giao dịch
        
    Returns:
        Danh sách các giao dịch
    """
    if not wallet_ids:
        print("[DEBUG] Không có wallet_ids")
        return []
    
    print(f"[DEBUG] Đang lấy giao dịch cho các wallet: {wallet_ids}")
    
    try:
        # Lấy dữ liệu giao dịch với thông tin category và group
        res = supabase.table('transactions')\
            .select('''
                *,
                categories!inner(
                    *,
                    groups!inner(
                        group_name
                    )
                )
            ''')\
            .in_('wallet_id', wallet_ids)\
            .order('date', desc=True)\
            .execute()
        
        # Xử lý dữ liệu trả về
        transactions = []
        if res.data:
            for t in res.data:
                if 'categories' in t and t['categories']:
                    # Chuyển đổi cấu trúc dữ liệu
                    category = t['categories']
                    t['categories'] = {
                        'categoryname': category.get('categoryname'),
                        'group_name': category.get('groups', {}).get('group_name', '')
                    }
                    transactions.append(t)
        
        print(f"[DEBUG] Số lượng giao dịch lấy được: {len(transactions)}")
        
        # In thông tin mẫu cho debug
        if transactions:
            print("\n[DEBUG] Mẫu dữ liệu giao dịch (3 giao dịch gần nhất):")
            for i, t in enumerate(transactions[:3]):
                print(f"Giao dịch {i+1}:")
                print(f"  ID: {t.get('id')}")
                print(f"  Số tiền: {float(t.get('amount', 0)):,.0f} VND")
                print(f"  Ngày: {t.get('date')}")
                print(f"  Ghi chú: {t.get('note', 'Không có')}")
                print(f"  Danh mục: {t.get('categories', {}).get('categoryname', 'Chưa phân loại')}")
                print(f"  Nhóm: {t.get('categories', {}).get('group_name', 'Chưa phân loại')}")
                print("-" * 40)
        else:
            print("[DEBUG] Không tìm thấy giao dịch nào")
        
        return transactions
        
    except Exception as e:
        print(f"[ERROR] Lỗi khi lấy dữ liệu giao dịch: {str(e)}")
        print("[DEBUG] Kiểm tra lại cấu trúc bảng và quan hệ giữa các bảng")
        return []
