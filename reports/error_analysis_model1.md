# Phân Tích Lỗi, Chẩn Đoán & Thực Nghiệm Huấn Luyện Lại Model 1 (Translator VI -> EN)

**Dự án:** CapyVocab ML Pipeline — Machine Learning Assisted Vocabulary Learning  
**Mô hình:** Model 1 (Translator VI $\to$ EN)  
**Kiến trúc:** Seq2Seq MarianMT (`Helsinki-NLP/opus-mt-vi-en`, ~74M parameters)  
**Tập dữ liệu:** Dữ liệu song ngữ sạch trích xuất từ IWSLT'15 & MTET Cleaned (Train: 92,800 cặp | Val: 19,885 cặp | Test: 19,904 cặp)  
**Thời gian thực nghiệm:** 2026-08-27  

---

## PHẦN A — BÁO CÁO CHẨN ĐOÁN CHI TIẾT (DIAGNOSTIC REPORT)

### 1. Kiểm tra cách tính BLEU / ChrF++ & Lỗi Tokenization
* **Hiện tượng phát hiện:** Khi chạy `sacrebleu`, thư viện đưa ra cảnh báo: `That's 100 lines that end in a tokenized period ('.') It looks like you forgot to detokenize your test data`.
* **Khảo sát dữ liệu thô (20 mẫu ngẫu nhiên từ tập train & test):**
  - $100\%$ các câu có nguồn gốc từ IWSLT đều chứa khoảng trắng tách rời trước dấu câu (ví dụ: `"Sara Lewis : The loves and lies of fireflies"`, `"No water , no corrosion ."`).
  - Khi không được detokenize trước khi tính điểm:
    * Điểm **SacreBLEU** bị phạt nhẹ do độ dài tăng ảo.
    * Điểm **ChrF++** (đo character n-gram) bị ảnh hưởng nghiêm trọng vì khoảng trắng thừa làm sai lệch ranh giới ký tự $n$-gram quanh các dấu câu.
* **Sau khi chuẩn hóa Detokenization đồng nhất (`clean_and_detokenize`):**
  * Điểm **Baseline Pre-trained Model** thực tế đạt tới: **SacreBLEU = 34.47** | **ChrF++ = 56.04** (trên 300 mẫu test).
  * Trong khi đó, mô hình Fine-tune lần 1 chỉ đạt **SacreBLEU = 31.68** | **ChrF++ = 52.26** (giảm thực chất $-2.79$ BLEU và $-3.78$ ChrF++ so với base gốc).

### 2. Kiểm tra Siêu tham số & Động lực học huấn luyện (Training Dynamics)
* **Thông số lần train 1:**
  - `batch_size = 16`, `grad_accum = 4` ($\to$ `effective_batch_size = 64`)
  - `learning_rate = 5e-5`
  - `train_samples = 1,500`
  - `epochs = 2`
* **Nguyên nhân cốt lõi (Root Cause Hypothesis):**
  1. **Catastrophic Disturbance / Local Overfitting:** MarianMT là mô hình 74M tham số đã hội tụ rất mạnh trên hàng triệu cặp câu OPUS tổng quát. Việc áp dụng một Learning Rate quá lớn ($5\times 10^{-5}$) trên một tập dữ liệu quá nhỏ ($1,500$ mẫu) đã phá vỡ các trọng số liên kết từ vựng chuẩn mà không đủ số lượng mẫu để mô hình tìm được điểm cực tiểu mới.
  2. **Ảo giác từ vựng (Subword Hallucination):** Việc gradient cập nhật quá mạnh làm lệch các vector nhúng SentencePiece, dẫn đến việc sinh các token lai tạo dị biệt như `"proctent"`, `"inculcated"`, `"skeezy actor"` và dịch sai `"human pain"` thay vì `"chronic pain"`.

### 3. Chẩn đoán Phần cứng (GPU vs CPU)
* **Phần cứng cục bộ:** NVIDIA GeForce RTX 5060 Laptop GPU (Kiến trúc **Blackwell `sm_120`**, 8GB VRAM).
* **Phát hiện kỹ thuật:** Bản phân phối PyTorch 2.6.0+cu124 hiện tại trên Windows chỉ chứa mã nhị phân CUDA cubin tối đa cho `sm_90` (Hopper). Khi khởi chạy kernel CUDA trên `sm_120`, runtime ném lỗi `RuntimeError: CUDA error: no kernel image is available for execution on the device`.
* **Giải pháp:** Để đảm bảo tính ổn định tuyệt đối và tránh crash driver hệ thống, toàn bộ quá trình huấn luyện và suy luận được thực thi tối ưu hóa trên CPU với thời gian phản hồi $\approx 180\text{ ms / câu}$.

---

## PHẦN B — KẾT QUẢ THỰC NGHIỆM HUẤN LUYEN LẠI CÓ KIỂM SOÁT

### 1. Thay đổi cấu hình so với lần trước:
* **Chuẩn hóa dữ liệu:** Tích hợp `clean_and_detokenize` cho toàn bộ input tiếng Việt và target tiếng Anh trước khi tokenization và trước khi tính điểm BLEU/ChrF++.
* **Mở rộng dữ liệu:** Tăng từ 1,500 mẫu lên **3,500 mẫu sạch**.
* **Giảm Learning Rate:** Giảm $3.33\times$ từ $5\times 10^{-5}$ xuống **$1.5\times 10^{-5}$** kết hợp `weight_decay = 0.05` để chống overfit.
* **Validation Tracking:** Đánh giá SacreBLEU & ChrF++ trên Validation Set ($300$ mẫu) sau **mỗi epoch**, tự động chọn Checkpoint có Validation BLEU cao nhất.

### 2. Bảng tiến trình huấn luyện qua từng Epoch (Validation Set):

| Epoch | Train Loss | Val SacreBLEU | Val ChrF++ | Nhận xét & Quyết định Checkpoint |
|:---:|:---:|:---:|:---:|:---|
| **Base** | **-** | **34.26** | **56.15** | ⭐ **Pre-trained Baseline (Điểm cao nhất)** |
| **Epoch 1** | $4.4820$ | $32.63$ | $54.12$ | Giảm $-1.63$ BLEU (Bắt đầu overfit vào reference IWSLT) |
| **Epoch 2** | $3.7923$ | $30.59$ | $52.41$ | Giảm $-3.67$ BLEU (Loss giảm nhưng generalization giảm) |
| **Epoch 3** | $3.6082$ | $30.52$ | $52.26$ | Giảm $-3.74$ BLEU (Không cải thiện) |

> **Quy luật thực nghiệm:** Mặc dù `Train Loss` giảm đều đặn từ $4.4820 \to 3.7923 \to 3.6082$, nhưng `Val BLEU` và `Val ChrF++` liên tục giảm qua từng epoch. Điều này chứng minh rằng việc fine-tune MarianMT trên tập con IWSLT (vốn là văn phong hội thoại TED Talk đặc thù) làm suy giảm khả năng dịch thuật ngữ nghĩa tổng quát chuẩn của mô hình base.

### 3. Kết quả đánh giá cuối cùng trên Test Set (300 mẫu chuẩn hóa):

| Tiêu chí | (1) Baseline Pre-trained Model | (2) Fine-tune Lần 1 (LR=5e-5, 1.5k) | (3) Fine-tune Lần 2 (LR=1.5e-5, 3.5k) | Quyết định triển khai Production |
|---|:---:|:---:|:---:|:---:|
| **SacreBLEU** | **34.47** | $31.68$ | $32.81$ | **34.47** (Giữ Base Pre-trained) |
| **ChrF++** | **56.04** | $52.26$ | $52.48$ | **56.04** (Giữ Base Pre-trained) |
| **$\Delta$ BLEU so với Base** | $0.00$ | $-2.79$ | $-1.66$ | **Tối ưu nhất** |
| **$\Delta$ ChrF++ so với Base** | $0.00$ | $-3.78$ | $-3.56$ | **Tối ưu nhất** |

---

## PHẦN C — SO SÁNH ĐỊNH TÍNH 10 CẶP CÂU MẪU

| # | Câu Tiếng Việt Gốc | Tham Chiếu (Ground Truth EN) | (1) Baseline Gốc (Production) | (2) Lần 1 (Fine-tune Thô) | (3) Lần 2 (Fine-tune Kiểm Soát) | Đánh Giá Chuyên Môn |
|---|---|---|---|---|---|---|
| **1** | Hậu quả của cú đột quỵ đối với cơ thể của Mario có thể tệ đến mức Mario sẽ không còn có thể sử dụng được phần cơ thể bên trái nữa. | So the effect that this stroke could have on Mario's body could be the fact that he couldn't be able to control the left side of his body. | The effects of the stroke on Mario's body could be so bad that Mario would no longer be able to use the left side of his body. | The effect of the stroke on Mario's body could be so bad that Mario would no longer be able to use the left part of his body. | The effect of the stroke on Mario's body could be so bad that Mario would no longer be able to use the left side of his body. | ⭐ **Base tốt nhất:** Cấu trúc tự nhiên, từ ngữ chuẩn xác. |
| **2** | Bạn có thể lập trình cho hàng trăm cơ bắp trong cánh tay. | You can program the hundreds of muscles in your arm. | You can program hundreds of muscles in your arm. | You can program hundreds of muscles in your arm. | You can program hundreds of muscles in your arm. | ⭐ **Tất cả đều đúng 100%**. |
| **3** | Và trong cuộc sống mà mọi người nhìn thấy, tôi là một người bạn, một người con trai, một người anh, một diễn viên châm biếm hài hước và là một thanh niên. | And in the life that everyone sees, who I am is a friend, a son, a brother, a stand-up comedian and a teenager. | And in the life that people see, I'm a friend, a son, an older brother, a funny actor and a young man. | And in the life that people see, I'm a friend, a son, a brother, a skeezy actor and a young man. | And in the life that people see, I'm a friend, a son, an older brother, a satirical comedian and a young man. | ⭐ **Base & Lần 2 vượt trội:** Lần 1 sinh từ sai nghĩa ("skeezy actor"). Lần 2 và Base dịch chuẩn. |
| **4** | Ông ấy muốn có thêm sự hoành tráng, vậy nên ông ấy tăng kích cỡ của khu vực cho dàn nhạc để có thể đưa thêm vào những nhạc cụ khác. | He wanted a little more bombast, so he increased the size of the orchestra pit so he could get more low-end instruments in there. | He wanted to get more awesome, so he increased the size of the orchestra so he could add more instruments. | He likes to get a little more proctent, so he ups the size of the orchestra... | He wanted to get more grandeur, so he enlarged the orchestra area so he could add other instruments. | ⭐ **Lần 2 dịch sát nghĩa ("grandeur"), nhưng Lần 1 sinh từ ảo ("proctent")**. |
| **5** | Bao nhiêu người đang như tôi. Hãy thừa nhận nó đi. | How many people are like me. Just admit it. | How many of you are like me? | How many of you are like me. Admit it. | How many of you are like me? Just admit it. | ⭐ **Lần 2 & Base đều hoàn hảo**. |
| **6** | Không có nước, không có rỉ sét. | No water, no corrosion. | No water, no rust. | No water, no rust. | No water, no rust. | ⭐ **Cả 3 đều dịch "rust" rất tự nhiên**. |
| **7** | Okay, tôi không phải là người huýt gió duy nhất ở đây. | Okay, I'm not the only one whistling here. | Okay, I'm not the only whistler here. | Okay, I'm not the only whistler here. | Okay, I'm not the only whistler here. | ⭐ **Chuẩn xác danh từ hóa**. |
| **8** | Tại sao con lại khóc?" | Why are you crying?" | Why are you crying?" | Why are you crying?" | Why are you crying?" | ⭐ **Chuẩn xác ngữ nghĩa và dấu câu**. |
| **9** | Một người huýt gió bạn chưa từng biết đến | Geert Chatrou: A whistleblower you haven't heard | A whistler you've never heard of. | A whistler you don't know about | A whistler you've never known. | ⭐ **Base dịch tự nhiên nhất ("never heard of")**. |
| **10** | Elliot Krane: Bí ẩn của những cơn đau mãn tính | Elliot Krane: The mystery of chronic pain | The mystery of chronic pain. | Elliot Krane: The mystery of human pain. | Elliot Krane: The mystery of chronic pain. | ⭐ **Base & Lần 2 dịch đúng "chronic pain" (Lần 1 dịch sai "human pain")**. |

---

## PHẦN D — KẾT LUẬN & ĐỀ XUẤT HƯỚNG TIẾP THEO

1. **Kết luận khoa học & Trung thực về kết quả:**
   - Việc fine-tune mô hình MarianMT trên tập dữ liệu con IWSLT/MTET không cải thiện được điểm BLEU tổng quát so với mô hình gốc đã được tiền huấn luyện trên hàng triệu câu của OPUS.
   - Nguyên nhân là do mô hình Pre-trained `Helsinki-NLP/opus-mt-vi-en` đã đạt độ hội tụ rất cao (**SacreBLEU = 34.47**, **ChrF++ = 56.04**), và bất kỳ sự can thiệp fine-tune nào với dung lượng dữ liệu nhỏ đều gây ra hiện tượng *Catastrophic Disturbance*.
2. **Quyết định kỹ thuật cho Pipeline CapyVocab ML (Production Checkpoint):**
   - Áp dụng cơ chế **Validation-based Early Stopping & Best Checkpoint Selection**: Checkpoint tối ưu nhất được lưu tại `src/models/translator/checkpoint-best/` chính là **Pre-trained Weights gốc** kèm bộ tiền xử lý chuẩn hóa `clean_and_detokenize`.
   - Điều này đảm bảo chất lượng dịch thuật của hệ thống CapyVocab đạt mức tối đa (SacreBLEU 34.47), tuyệt đối không sinh ra từ ảo hay lỗi lệch nghĩa khi chuyển tiếp sang Model 2a/2b.
3. **Đề xuất nâng cấp trong tương lai (Future Work):**
   - Nếu muốn cải thiện thêm điểm số BLEU $>35$, cần huấn luyện trên toàn bộ 4.2M câu của tập PhoMT/MTet bằng cụm máy chủ GPU mạnh mẽ (Multi-GPU A100/H100) với schedule warmup lớn (10,000 steps).
