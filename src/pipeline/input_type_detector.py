"""
Input Type Detector Module for CapyVocab ML Pipeline.

Mục đích & Logic Phân Loại:
--------------------------
Module này đóng vai trò là bộ định tuyến (router) ở tầng đầu vào của CapyVocab ML,
nhận chuỗi văn bản từ người học và xác định chế độ xử lý phù hợp:
  - "invalid_input" : Chuỗi rỗng, chỉ chứa khoảng trắng, hoặc không hợp lệ.
  - "word_mode"     : Đầu vào là từ đơn hoặc cụm từ/thành ngữ ngắn (1-3 từ, không có dấu câu).
  - "sentence_mode" : Đầu vào là một câu hoàn chỉnh, mệnh đề dài hoặc câu có dấu kết thúc.

Lý do chọn ngưỡng 3 token:
--------------------------
1. Trong học ngoại ngữ (EN-VI), các đơn vị từ vựng đa từ (multi-word lexical units)
   như cụm danh từ (compound nouns: "ice cream", "machine learning"),
   cụm động từ (phrasal verbs: "look after", "look forward to"),
   và thành ngữ ngắn hầu như luôn có độ dài từ 1 đến 3 từ.
2. Các chuỗi từ 4 token trở lên hầu như luôn mang cấu trúc vị ngữ/mệnh đề đầy đủ
   (ví dụ: "she wants to study", "tôi thích đọc sách"), ngay cả khi người dùng quên gõ dấu chấm.
3. Dấu câu kết thúc (. ? ! ...) là tín hiệu ngữ pháp rõ ràng nhất của một câu hoàn chỉnh,
   kể cả khi câu rất ngắn (ví dụ: "I am.", "Why me?", "Stop it!").
"""

import sys
import re
from typing import List, Tuple

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

TERMINAL_PUNCTUATION_PATTERN = re.compile(r'[\.\?\!\…\n]')

def detect_input_type(text: str) -> str:
    """
    Detect whether the input text should be processed in 'word_mode', 'sentence_mode',
    or rejected as 'invalid_input'.

    Rule:
      1. Kiểm tra tính hợp lệ của kiểu dữ liệu chuỗi.
      2. Chuẩn hóa chuỗi (strip khoảng trắng thừa). Nếu rỗng -> 'invalid_input'.
      3. Kiểm tra xem có chứa dấu câu kết thúc (. ? ! … hoặc ký tự xuống dòng) hay không.
      4. Đếm số token (tách bằng khoảng trắng).
      5. Nếu số token <= 3 VÀ không chứa dấu câu kết thúc -> 'word_mode'.
      6. Ngược lại -> 'sentence_mode'.

    Args:
        text (str): Raw input string from the user.

    Returns:
        str: "invalid_input" | "word_mode" | "sentence_mode"
    """
    if not isinstance(text, str):
        return "invalid_input"
        
    cleaned_text = text.strip()
    if not cleaned_text:
        return "invalid_input"

    # Kiểm tra sự xuất hiện của dấu câu kết thúc
    has_terminal_punct = bool(TERMINAL_PUNCTUATION_PATTERN.search(cleaned_text))

    # Tách token theo khoảng trắng
    tokens = cleaned_text.split()
    token_count = len(tokens)

    # Điều kiện phân loại
    if token_count <= 3 and not has_terminal_punct:
        return "word_mode"
    else:
        return "sentence_mode"


if __name__ == "__main__":
    test_cases: List[Tuple[str, str, str]] = [
        # Nhóm Word Mode
        ("persevere", "word_mode", "Từ đơn tiếng Anh không dấu câu"),
        ("kiên trì", "word_mode", "Từ ghép tiếng Việt (2 từ) không dấu câu"),
        ("look after", "word_mode", "Phrasal verb 2 từ không dấu câu"),
        ("look forward to", "word_mode", "Phrasal verb 3 từ không dấu câu"),
        ("machine learning", "word_mode", "Cụm danh từ chuyên ngành 2 từ"),
        
        # Nhóm Sentence Mode
        ("I am.", "sentence_mode", "Câu cực ngắn (2 từ) nhưng CÓ dấu chấm kết thúc"),
        ("Why not?", "sentence_mode", "Câu hỏi ngắn (2 từ) có dấu chấm hỏi"),
        ("Stop it!", "sentence_mode", "Câu cảm thán (2 từ) có dấu chấm than"),
        ("she wants to learn english because it is fun", "sentence_mode", "Câu dài (9 từ) KHÔNG có dấu chấm cuối"),
        ("cats like drinking milk", "sentence_mode", "Câu 4 từ không dấu câu kết thúc"),
        ("Tôi đang học từ vựng mỗi ngày.", "sentence_mode", "Câu tiếng Việt hoàn chỉnh có dấu chấm"),
        
        # Nhóm Invalid Input Edge Cases
        ("", "invalid_input", "Edge case: Chuỗi rỗng hoàn toàn"),
        ("   ", "invalid_input", "Edge case: Chuỗi chỉ chứa khoảng trắng space"),
        ("\t\n", "invalid_input", "Edge case: Chuỗi chỉ chứa ký tự tab và xuống dòng"),
    ]

    print("=" * 82)
    print("KIEM THU MODULE INPUT TYPE DETECTOR (CAPYVOCAB ML PIPELINE)")
    print("=" * 82)
    print(f"{'Input Text':<47} | {'Detected Mode':<15} | {'Expected':<15} | {'Status':<6}")
    print("-" * 82)

    all_passed = True
    for raw_input, expected, description in test_cases:
        detected = detect_input_type(raw_input)
        is_pass = (detected == expected)
        status = "PASS" if is_pass else "FAIL"
        if not is_pass:
            all_passed = False
        display_text = f"\"{raw_input}\"" if raw_input else "\"\" (empty/whitespace)"
        print(f"{display_text:<47} | {detected:<15} | {expected:<15} | {status:<6}")

    print("=" * 82)
    if all_passed:
        print(f">>> TAT CA {len(test_cases)}/{len(test_cases)} TEST CASES DEU DAT CHUAN (PASSED)! <<<")
    else:
        print(">>> CO TEST CASE THAT BAI! VUI LONG KIEM TRA LAI LOGIC! <<<")
    print("=" * 82)
