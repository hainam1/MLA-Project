"""
Input Type Detector Module (CapyVocab ML Pipeline).

Mục đích:
- Phân loại và điều hướng đầu vào của người dùng vào 2 nhánh xử lý chính:
  1. `word_mode`: Đầu vào là từ đơn, cụm từ vựng (vocab/phrase).
     -> Luồng: Translator (Model 1) -> CEFR Word Classifier (Model 2a) -> Example Generator (Model 3a) -> Second Pair of Eyes (Model 4).
  2. `sentence_mode`: Đầu vào là một câu hoàn chỉnh (full sentence).
     -> Luồng: Translator (Model 1) -> CEFR Sentence Classifier (Model 2b) -> Sentence Rewriter (Model 3b) -> Second Pair of Eyes (Model 4).

(Mã nguồn chi tiết sẽ được triển khai ở Phase 1).
"""

def detect_input_type(text: str) -> str:
    """
    Detect whether the input text is a 'word' or a 'sentence'.
    
    Args:
        text (str): Input text from user.
        
    Returns:
        str: 'word' | 'sentence'
    """
    raise NotImplementedError("Will be implemented in Phase 1.")
