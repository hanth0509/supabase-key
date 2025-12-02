from supabase_client import get_user_by_email, get_wallets_by_user_id, get_transactions_by_wallet_ids
from query_handler import handle_question
from prompt_builder import build_prompt
from ollama_client import ask_ollama

def main():
    print("🚀 Supabase Chatbot")
    print("Gõ 'exit' để thoát\n")

    while True:
        # Nhập email người dùng
        email = input("Nhập email người dùng: ").strip()
        if email.lower() in ["exit", "quit"]:
            break

        # Xác thực người dùng
        user = get_user_by_email(email)
        if not user:
            print("❌ Không tìm thấy người dùng.")
            continue

        # Lấy danh sách ví của người dùng
        wallets = get_wallets_by_user_id(user["id"])
        if not wallets:
            print("❌ Người dùng chưa có ví nào.")
            continue
            
        wallet_ids = [w["id"] for w in wallets]
        
        # Lấy tất cả giao dịch của người dùng
        transactions = get_transactions_by_wallet_ids(wallet_ids)
        if not transactions:
            print("ℹ️ Không tìm thấy giao dịch nào.")
            continue

        # Vòng lặp chính cho câu hỏi
        while True:
            print("\n" + "="*50)
            question = input("\nNhập câu hỏi (hoặc 'đổi' để đổi người dùng): ").strip()
            
            if question.lower() in ["exit", "quit"]:
                return
                
            if question.lower() in ["đổi", "đổi người dùng"]:
                break

            # Kiểm tra nếu là câu chào hỏi hoặc không liên quan
            if any(x in question.lower() for x in ["xin chào", "hello", "hi", "chào"]):
                print("\n🤖 Chào bạn! Tôi có thể giúp gì bạn hôm nay?")
                continue
                
            # Xử lý câu hỏi bằng query_handler trước
            result, message = handle_question(question, transactions)
            
            if result is not None:
                # Nếu có kết quả từ query_handler
                print(f"\n🤖 {message}")
            else:
                # Nếu không xử lý được, trả lời ngắn gọn
                print("\n🤖 Tôi có thể giúp bạn với các câu hỏi về:")
                print("- Chi tiêu, thu nhập")
                print("- Số dư tài khoản")
                print("- Thống kê theo tháng/ngày")
                print("- Tìm kiếm giao dịch")

if __name__ == "__main__":
    main()
