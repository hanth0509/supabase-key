from supabase_client import get_user_by_email, get_wallets_by_user_id, get_transactions_by_wallet_ids
from query_handler import handle_question
from ollama_client import ask_ollama
import os
import random

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("\n" + "="*60)
    print(" QUẢN LÝ TÀI CHÍNH CÁ NHÂN".center(60))
    print("="*60)

def print_help():
    """Print help information."""
    print("\n Tôi có thể giúp bạn với các câu hỏi sau:")
    print("\n THỐNG KÊ CHI TIÊU:")
    print("- Tổng chi tiêu tháng này")
    print("- Tôi đã chi bao nhiêu tiền điện tháng trước?")
    print("- Tổng thu nhập năm nay")
    print("- Tôi chi nhiều nhất cho khoản nào?")
    
    print("\n SỐ DƯ VÀ TỔNG KẾT:")
    print("- Số dư hiện tại")
    print("- Tổng số tiền đã chi")
    print("- Tổng thu nhập")
    
    print("\n TÌM KIẾM GIAO DỊCH:")
    print("- Tìm giao dịch mua sắm tháng này")
    print("- Tôi đã chi bao nhiêu cho ăn uống?")
    print("\nGõ 'đổi' để đổi người dùng, 'thoát' để kết thúc\n")

def format_currency(amount):
    """Format number as currency."""
    return "{:,.0f} VND".format(amount) if amount is not None else "0 VND"

def main():
    clear_screen()
    print_header()
    print(" Chào mừng bạn đến với hệ thống quản lý tài chính!")
    print("   Vui lòng đăng nhập bằng email của bạn.")
    
    while True:
        try:
            email = input("\n Nhập email (hoặc 'thoát' để kết thúc): ").strip()
            
            if email.lower() in ["exit", "quit", "thoát"]:
                print("\n Hẹn gặp lại bạn!")
                return
                
            if not email:
                continue
                
            print(f"\n Đang tìm kiếm thông tin của {email}...")
            user = get_user_by_email(email)
            
            if not user:
                print(" Không tìm thấy người dùng. Vui lòng thử lại.")
                continue

            print(f"\n Xin chào {user.get('full_name', 'bạn')}!")
            
            wallets = get_wallets_by_user_id(user["id"])
            if not wallets:
                print(" Bạn chưa có ví nào. Vui lòng tạo ví mới.")
                continue
                
            print(f"\n Tìm thấy {len(wallets)} ví:")
            for i, wallet in enumerate(wallets, 1):
                print(f"   {i}. {wallet.get('name', 'Không tên')} ({format_currency(wallet.get('balance', 0))})")
            
            wallet_ids = [w["id"] for w in wallets]
            print("\n Đang tải giao dịch...")
            transactions = get_transactions_by_wallet_ids(wallet_ids)
            
            if not transactions:
                print(" Không tìm thấy giao dịch nào.")
                continue
                
            print(f" Đã tải {len(transactions)} giao dịch gần đây.")
            print_help()
            
            while True:
                try:
                    question = input("\n Nhập câu hỏi của bạn: ").strip()
                    
                    if not question:
                        continue
                        
                    if question.lower() in ["exit", "quit", "thoát"]:
                        print("\n Hẹn gặp lại bạn!")
                        return
                        
                    if question.lower() in ["đổi", "đổi người dùng"]:
                        clear_screen()
                        print_header()
                        break
                        
                    if question.lower() in ["giúp", "help", "hướng dẫn"]:
                        print_help()
                        continue
                    
                    # Process the question
                    question_lower = question.lower().strip()
                    
                    # Handle greetings (chỉ khi cả câu là lời chào, không bắt substring)
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
                            "Xin chào! Bạn muốn xem chi tiêu hay thu nhập?",
                            "Hello, mình có thể hỗ trợ bạn xem tổng tiền hoặc hóa đơn.",
                            "Chào bạn, bạn đang quan tâm đến chi tiêu hay thống kê tổng quan?",
                            "Xin chào! Hãy hỏi mình về tổng tiền, hóa đơn hoặc danh mục chi tiêu nhé."
                        ]
                        print("\n " + random.choice(greeting_responses))
                        continue
                    
                    # Process with query_handler (dùng dữ liệu Supabase cho câu hỏi tài chính)
                    result, message = handle_question(question, transactions)

                    # Không đủ dữ liệu giao dịch
                    if message == "Không đủ dữ liệu để trả lời.":
                        print("\n Không đủ dữ liệu để trả lời.")
                        continue

                    # Không phải câu hỏi tài chính → gọi LLM như chatbot chung (không dùng dữ liệu giao dịch)
                    if result is None and message is None:
                        try:
                            answer = ask_ollama(question)
                            print(f"\n {answer}")
                        except Exception as e:
                            print(f"\n Lỗi khi gọi LLM: {e}")
                            print("Vui lòng thử lại sau.")
                        continue

                    # Câu hỏi tài chính có dữ liệu
                    if result is not None:
                        # message đã được format sẵn bằng format_stats/format_currency
                        print(f"\n {message}")
                    else:
                        print("\n Tôi không hiểu câu hỏi của bạn. Dưới đây là một số gợi ý:")
                        print_help()
                        
                except KeyboardInterrupt:
                    print("\n Hẹn gặp lại bạn!")
                    return
                except Exception as e:
                    print(f"\n Có lỗi xảy ra: {str(e)}")
                    print("Vui lòng thử lại với câu hỏi khác hoặc mô tả rõ hơn.")
                    
        except KeyboardInterrupt:
            print("\n Hẹn gặp lại bạn!")
            return
        except Exception as e:
            print(f"\n Có lỗi xảy ra: {str(e)}")
            print("Vui lòng thử lại.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n Có lỗi nghiêm trọng: {str(e)}")
        input("Nhấn Enter để thoát...")
