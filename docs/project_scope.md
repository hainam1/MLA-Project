# Project scope and research questions

## Definition

Given an English learner essay, estimate its human-rated Vocabulary and Grammar scores from
interpretable features, and use disagreement between two model families to prioritize teacher
review.

## Fixed decisions

- Domain: educational support and natural-language processing.
- Task: two supervised regression targets, Vocabulary and Grammar.
- Models: Ridge Regression and Random Forest Regression, each fitted separately per target.
- Features: length, vocabulary, detected grammar issues, and syntax.
- Evaluation: MAE, RMSE, and R-squared per model and target.
- Review signal: the maximum absolute Ridge/Random Forest prediction difference across the two
  targets, producing one deterministic queue score per essay.
- Human role: teachers retain scoring authority; disagreement is neither confidence nor an error
  probability.

## Research questions

1. **Primary RQ (Phase 1):** At the fixed primary teacher-review budget of 20%, does ranking essays
   by essay-level model disagreement capture more large selected-RF-prediction errors than uniform
   random selection of the same number of essays?
   *(Với cùng số bài giáo viên có thể xem, xếp hạng theo mức bất đồng giữa mô hình có tìm được nhiều
   dự đoán sai lớn hơn chọn ngẫu nhiên không?)*
2. How accurately do Ridge and Random Forest predict human Vocabulary and Grammar scores under the
   same leakage-safe split?
3. Which interpretable feature groups contribute useful predictive information for each target?
4. Where do predictions have the largest reference-score errors, and what linguistic or dataset
   patterns characterize those cases?

## Excluded

Automatic correction, essay generation, personalized feedback, plagiarism detection, high-stakes
grading, and claims about complete language proficiency are outside scope.
