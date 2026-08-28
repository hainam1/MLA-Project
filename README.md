# CapyVocab ML

CapyVocab ML là pipeline học từ vựng tiếng Anh theo CEFR A1–C1. Contract phục vụ hiện tại:

```text
Từ/cụm từ tiếng Việt (tối đa 3 token) + mức CEFR bắt buộc A1–C1
    -> từ điển Việt–Anh truy hồi nghĩa/POS/sense_id
    -> MarianMT + WordNet chỉ tạo thêm candidate
    -> multilingual E5 + bằng chứng song ngữ loại candidate sai nghĩa
    -> chuẩn hóa lemma + POS trước khi CEFR được xét
    -> CEFR lookup theo lemma+POS và kiểm tra level có thật sự tồn tại
    -> Model 3a + controlled templates sinh các câu ứng viên
    -> Model 2b kiểm chứng mức CEFR của câu
    -> từ tiếng Anh + câu hoàn chỉnh + target_match/needs_review
```

Pipeline không còn nhận câu tiếng Việt và không phục vụ Model 3b sentence rewriting. Artefact Model 3b vẫn được giữ để tái lập kết quả nghiên cứu cũ.

## Nguyên tắc độ chính xác

- `target_level` là lựa chọn bắt buộc của người dùng, không còn được suy ra từ bản dịch.
- `target_match: true` chỉ được trả khi wordlist xác thực đúng cả lemma, POS và level. Dự đoán Model 2a không còn được dùng như bằng chứng exact.
- Nếu tập candidate đúng nghĩa không có từ ở level yêu cầu, pipeline giữ từ đúng nghĩa nhất với `selection_status: no_exact_level_match`, `target_match: false` và `needs_review: true`; CEFR không được phép đổi nghĩa.
- `meaning_analysis` công khai candidate, POS, `sense_id`, nguồn và điểm semantic; input mơ hồ được đánh dấu `needs_clarification`.
- Câu phải chứa đúng từ được chọn, là câu hoàn chỉnh và được Model 2b phân loại lại. `level_match` cho biết câu có đạt target hay không.
- WordNet chỉ mở rộng đồng nghĩa từ sense ưu tiên. Nhãn CEFR luôn đến từ wordlist của dự án hoặc classifier.

## Cài đặt

Khuyến nghị Python 3.12:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m ensurepip --upgrade
python -m pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader -d data/external/nltk_data wordnet
```

Kiểm tra môi trường và GPU:

```powershell
python -m src._env_check
```

## Chạy pipeline

`--target-level` là bắt buộc khi chạy non-interactive:

```powershell
python -m src.pipeline.run_pipeline "tốt" --target-level B2 --device cuda
python -m src.pipeline.run_pipeline "quả táo" --target-level A1 --device cpu
```

Chế độ interactive sẽ hỏi lần lượt từ vựng và level:

```powershell
python -m src.pipeline.run_pipeline --interactive --device cuda
```

Ví dụ output rút gọn:

```json
{
  "status": "success",
  "input_vi": "tốt",
  "requested_level": "B2",
  "translation_en": "superb",
  "selected_vocabulary": {
    "predicted_level": "B2",
    "target_match": true,
    "selection_status": "matched"
  },
  "generated_example": {
    "sentence": "After reviewing the evidence, the committee concluded that the result was superb.",
    "level_match": true
  }
}
```

## REST API và giao diện web

```powershell
uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

- `GET /`: giao diện nhập từ vựng và chọn CEFR.
- `GET /health/live`: kiểm tra process, không load model.
- `GET /health/ready`: kiểm tra toàn bộ artefact phục vụ, bao gồm WordNet.
- `GET /v1/status`: contract và trạng thái model.
- `POST /v1/process`: xử lý từ vựng.

Request mới:

```json
{
  "vietnamese_vocabulary": "tốt",
  "target_level": "B2"
}
```

Hai trường cũ `vietnamese_text` và `rewrite_target_level` không còn được chấp nhận. API chỉ nên bind localhost vì chưa có authentication hoặc rate limiting.

## Kiểm thử

```powershell
python -m pytest -q
python -m black --check src tests
python -m flake8 src tests
python -m src.artifacts.build_manifest --verify
python -m src.release.build_release verify dist/capyvocab-ml-0.3.0
```

Đánh giá riêng tầng nghĩa bằng gold set (không dùng làm runtime mapping):

```powershell
python -m src.quality.evaluate_lexical_retrieval --device cpu --top-k 5
```

Test bao phủ input vocabulary-only, target bắt buộc, lexical gate, lemma+POS CEFR lookup, lexical constraint, API contract, artefact và release.

## Dữ liệu, model và giới hạn

- Model 1: MarianMT VI→EN, sinh ranked beams.
- Model 2a: word CEFR classifier; exact wordlist lookup được ưu tiên để tăng độ tin cậy.
- Model 2b: chỉ dùng nội bộ để xác minh CEFR của câu ví dụ.
- Model 3a: FLAN-T5-small; controlled templates là fallback khi câu sinh không hoàn chỉnh hoặc không đạt CEFR.
- Model 3b: giữ cho nghiên cứu cũ, không nằm trong serving contract.
- Model 4: chưa sẵn sàng; `quality_verification` vẫn là `false`.

Model binary và dữ liệu lớn không commit vào Git. Một số corpus có giấy phép CC BY-NC/CC BY-NC-SA nên `commercial_use_allowed: false`. Không load file pickle/joblib từ nguồn không tin cậy.

## Release

```powershell
python -m src.artifacts.build_manifest
python -m src.release.build_release build --version 0.3.0 --allow-noncommercial
python -m src.release.build_release verify dist/capyvocab-ml-0.3.0
```

Full model bundle bao gồm AVDict, multilingual E5 và WordNet runtime data. Source bundle bao gồm giao diện web, provenance và gold evaluation set.
