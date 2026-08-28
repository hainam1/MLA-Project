# Task Formulation & System Architecture: CapyVocab ML

## 1. Motivation & Real-World Context (CapyVocabApp)

In contemporary language learning platforms such as **CapyVocabApp**, learners encounter two primary interaction modalities when attempting to acquire and practice English vocabulary:
1. **Querying specific vocabulary words or short phrases** (e.g., searching for the English equivalent of a Vietnamese concept, finding its CEFR proficiency level, and generating natural example sentences).
2. **Submitting full sentences or paragraphs** (e.g., translating a thought from Vietnamese to English, checking whether the generated English sentence is too easy/hard for their current level, and adapting the sentence to a target CEFR level).

Traditional dictionary applications only provide static bilingual lookups and predefined example sentences. However, dynamic pedagogical systems require **personalized, context-aware vocabulary assistance**. Learners at the A2 level cannot effectively learn from complex C1-level example sentences with intricate subordinate clauses, while advanced C1 learners require sophisticated collocations and nuanced expressions.

To power **CapyVocabApp**, the backend Machine Learning system (**CapyVocab ML**) must dynamically:
- Translate learner intent from Vietnamese to English ($VI \to EN$).
- Accurately assess the CEFR proficiency level of both single lexical units ($A1 \to C1$) and complete sentences.
- Generate level-appropriate contextual examples and rewrite sentences to match target proficiency levels ($A1 \to C1$).
- Automatically verify and sanitize outputs through an automated quality control layer (*Second Pair of Eyes*).

---

## 2. Target Proficiency Scope: A1 - C1 (5 Classes) & Future Work

For all classification, generation, and rewriting modules in CapyVocab ML, the **core operational scope is formally established as CEFR A1 through C1 (5 classes: $\{A1, A2, B1, B2, C1\}$)**:

- **Rationale for A1–C1 Core Scope**: Open-source educational corpora (Cambridge English Vocabulary Profile, Oxford 3000/5000, CEFR-J, Kelly List, and readability benchmarks) provide rich, statistically balanced distributions for levels A1 to C1.
- **Designation of C2 as Future Work**: Level C2 represents native/bilingual mastery characterized by highly idiosyncratic literary nuances, archaic idioms, and specialized domain knowledge. Validated C2 training data is extremely scarce in open corpora, leading to severe class imbalance if forced into a standard 6-class setting. Restricting the primary pipeline to 5 well-represented classes ($A1 \to C1$) ensures robust statistical learning, high classification confidence, and optimal pedagogical relevance for 99% of ESL learners. C2 extension is reserved for Future Work when specialized high-level literary corpora become available.

---

## 3. Overall System Input/Output & Dual-Branch Architecture

The system receives raw text input in Vietnamese from the user and automatically determines the downstream processing path via the `Input Type Detector`:

```mermaid
graph TD
    UI["Learner Input (Vietnamese Text)"] --> ITD["Input Type Detector"]
    
    %% Branch 0: Invalid Input
    ITD -- "Empty / Whitespace only" --> INV["Reject / Request Valid Input"]

    %% Branch 1: Word Mode
    ITD -- "<= 3 tokens, no terminal punct" --> WM["word_mode"]
    WM --> M1_W["Model 1: Translator (VI -> EN)"]
    M1_W --> M2a["Model 2a: CEFR Word Classifier (A1-C1)"]
    M2a --> M3a["Model 3a: Example Generator (Target Word + Level)"]
    M3a --> M4_W["Model 4: Second Pair of Eyes (Quality Verification)"]
    M4_W --> OUT_W["Final Word Learning Card"]

    %% Branch 2: Sentence Mode
    ITD -- "> 3 tokens or terminal punct" --> SM["sentence_mode"]
    SM --> M1_S["Model 1: Translator (VI -> EN)"]
    M1_S --> M2b["Model 2b: CEFR Sentence Classifier (A1-C1)"]
    M2b --> M3b["Model 3b: Sentence Rewriter (Adapt to Target Level)"]
    M3b --> M4_S["Model 4: Second Pair of Eyes (Quality Verification)"]
    M4_S --> OUT_S["Final Sentence Learning Card"]
```

### 3.1 Branch A: `word_mode`
- **Input**: Vietnamese word or phrase (e.g., *"kiên trì"*, *"thực hiện"*).
- **Pipeline**:
  1. Translate to candidate English target word/phrase (*"persevere"* via `Helsinki-NLP/opus-mt-vi-en`).
  2. Classify lexical difficulty ($C1$).
  3. Generate a natural, level-tailored English example sentence containing the target word (*"She persevered through all obstacles to complete her degree."*).
  4. Verify lexical inclusion, grammatical correctness, and CEFR level consistency.
- **Output**: Complete vocabulary card (English translation, phonetic/POS, CEFR level, level-appropriate example sentence).

### 3.2 Branch B: `sentence_mode`
- **Input**: Full Vietnamese sentence (e.g., *"Tôi đang cố gắng cải thiện khả năng giao tiếp của mình."*).
- **Pipeline**:
  1. Translate to English (*"I am striving to enhance my interpersonal communication abilities."* via `Helsinki-NLP/opus-mt-vi-en`).
  2. Classify the sentence CEFR level ($B2 / C1$).
  3. Rewrite/simplify or elevate the sentence to a target CEFR level requested by the learner (e.g., simplify to $A2$: *"I am trying to speak English better with people."*).
  4. Verify meaning preservation, fluency, and target CEFR adherence.
- **Output**: Multi-level sentence analysis (translation, original CEFR level, level-adapted sentence rewrites).

---

## 4. Why Machine Learning is Essential (Rule-Based Limitations)

Rule-based heuristics (such as regex matching, static lookup dictionaries, or purely heuristic syllable-counting formulas) completely fail in modern adaptive language education due to several fundamental NLP challenges:

### 4.1 Limitations of Rule-Based Translation & Generation
- **Contextual Polysemy**: A word like *"chạy"* can translate to *"run"*, *"operate"*, *"execute"*, or *"drive"* depending on context. Rule-based dictionaries cannot perform disambiguation.
- **Generative Diversity**: Generating realistic, natural example sentences cannot be templated with simple slot-filling without creating awkward, unnatural language.

### 4.2 The Asymmetric Complexity: Sentence CEFR vs. Word CEFR
Evaluating **Sentence Difficulty (Model 2b)** is fundamentally more non-linear and complex than evaluating **Single Word Difficulty (Model 2a)**:

| Dimension | Word Difficulty (Model 2a) | Sentence Difficulty (Model 2b) | Why ML is Required for Sentences |
| :--- | :--- | :--- | :--- |
| **Primary Determinants** | Lexical frequency (Zipf score), word length, morphological complexity (affixes). | Interplay of individual word levels, grammatical structures, syntactic depth, discourse coherence, sentence length. | A sentence composed solely of simple A1/A2 words can reach C1 complexity due to inversion, mixed conditionals, or subjunctive structures (e.g., *"Had you told me earlier, I would not have gone."*). |
| **Syntactic Non-Linearity** | Not applicable (isolated token). | Highly non-linear (dependency tree depth, subordinate clauses, passive voice, cleft sentences). | Rule-based heuristics (e.g., average word level or character count) completely miss syntactic nuance and clause subordination depth. |
| **Feature Interaction** | Features are largely independent (e.g., character length correlates with frequency). | Complex feature interactions (dense lexical items + short clause vs. sparse words + nested structure). | Gradient Boosted Decision Trees (XGBoost, Random Forest) capture non-linear interactions across syntactic depth, lexical rarity distributions, and readability indices. |

---

## 5. Architectural Clarification on Model 2b (Feature Engineering Scope)

To maintain architectural clarity and adhere to standard Machine Learning project taxonomy:
- **Model 2b belongs strictly to the Classical Machine Learning family** (utilizing algorithms such as Random Forest, XGBoost, or LightGBM for multi-class tabular classification).
- **Primary Feature Baseline (Handcrafted Linguistic Features)**: The primary input to Model 2b consists of an interpretable, domain-rich tabular feature vector combining:
  1. Traditional readability indices (Flesch-Kincaid Grade, Automated Readability Index, Gunning Fog, Dale-Chall via `textstat`).
  2. Syntactic & dependency tree metrics extracted via `spaCy` (maximum tree depth, ratio of subordinate clauses, passive voice counts, POS tag distributions).
  3. Aggregated token-level frequency statistics (mean/min Zipf frequency from `wordfreq`, ratio of rare vs. common words).
- **Role of DeBERTa (Optional Feature Extractor Only)**: If pre-trained language model representations (e.g., `microsoft/deberta-v3-base`) are utilized, they serve **solely as a frozen, off-the-shelf feature extractor** to produce a fixed dense embedding vector appended to the tabular feature matrix. **No fine-tuning of DeBERTa is performed**, ensuring Model 2b remains lean, computationally efficient, and strictly within the Classical ML paradigm. In the initial development phase, the model will rely entirely on handcrafted linguistic features to maintain fast training iterations and interpretability; frozen embeddings will only be introduced if baseline tabular accuracy proves insufficient.

---

## 6. Comprehensive Model Specifications (Models 1 to 4)

Below is the complete architectural specification for all 6 models comprising CapyVocab ML:

| Model ID | Module Name | Task Formulation | Input | Output | Extracted Features / Architecture | Target Label / Loss Metric |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model 1** | **Translator** | Seq2Seq Neural Machine Translation ($VI \to EN$) | Vietnamese string (word, phrase, or sentence) | English translated string | Pre-trained Sequence-to-Sequence Encoder-Decoder (`Helsinki-NLP/opus-mt-vi-en`) | Cross-Entropy Loss |
| **Model 2a** | **CEFR Word Classifier** | 5-Class Ordinal Classification ($A1 \to C1$) | English word/phrase | CEFR Level $\in \{A1, A2, B1, B2, C1\}$ | **13 Tabular Features**: Zipf frequency (`wordfreq`), syllable count (`pyphen`), char length, vowel count & ratio, POS tag, Google N-gram log frequency | Class label $y \in \{0, 1, 2, 3, 4\}$ / Multi-class Log-Loss, Macro F1, Adjacent Accuracy ($\pm 1$) |
| **Model 2b** | **CEFR Sentence Classifier** | 5-Class Sentence-Level Readability Classification | English full sentence | CEFR Level $\in \{A1, A2, B1, B2, C1\}$ | **Classical ML (XGBoost / Random Forest)**: <br>1. Syntactic & Readability features (Flesch-Kincaid, ARI, Gunning Fog, dependency tree depth via `spaCy`, POS distribution, word rarity stats).<br>2. *(Optional)* Frozen DeBERTa-v3 sentence embeddings. | Class label $y \in \{0, 1, 2, 3, 4\}$ / Multi-class Log-Loss, Macro F1, Quadratic Weighted Kappa (QWK) |
| **Model 3a** | **Example Generator** | Controlled Text Generation (Word + Target Level) | Input prompt: `"generate: word=<W> level=<L>"` | Example sentence containing word at level $L$ | Fine-tuned Seq2Seq LM (`google/flan-t5-base` or `t5-small`) with constrained decoding | Seq2Seq Cross-Entropy / BLEU, ROUGE-L, Lexical Constraint Satisfaction Rate |
| **Model 3b** | **Sentence Rewriter** | Controlled Sentence Simplification / Paraphrasing | Input prompt: `"rewrite: sentence=<S> target_level=<L>"` | Rewritten sentence at level $L$ preserving core semantics | Fine-tuned Seq2Seq LM (`google/flan-t5-base` or `t5-small`) | Cross-Entropy Loss / SARI, BERTScore, Semantic Cosine Similarity, Target FKGL Alignment |
| **Model 4** *(Optional)* | **Second Pair of Eyes** | Binary Verification Classifier | Candidate output text + metadata features | `acceptable` vs. `needs_review` | **Lightweight Classical ML**: Logistic Regression / Decision Tree on length anomaly, repetition, BLEU anomaly, readability drift | Binary Log-Loss / High-Recall on `needs_review` class ($\ge 0.90$) |

### 6.1 Ground Truth Labeling Methodology for Model 2a (CEFR Word Classifier)

To ensure methodological rigor during academic defense, the target label `cefr_label` ($y \in \{0, 1, 2, 3, 4\}$) is derived directly from the expert ground-truth annotations of **Guzey et al. (Istanbul Sehir University, 2014, Zenodo Record 12501)**:
1. **Continuous Expert Evaluations (`teachers_avg`)**: 30 certified English educators evaluated each word on a continuous difficulty scale $[1.0, 6.0]$.
2. **Deterministic Binning Thresholds (Guzey et al., 2014)**: The discrete CEFR categories are derived via the author's published continuous boundaries:
   $$\text{Level}(s) = \begin{cases} \mathbf{A1} & \text{if } s < 1.5 \\ \mathbf{A2} & \text{if } 1.5 \le s \le 2.5 \\ \mathbf{B1} & \text{if } 2.5 < s < 3.5 \\ \mathbf{B2} & \text{if } 3.5 \le s \le 4.5 \\ \mathbf{C1} & \text{if } 4.5 < s \le 5.5 \end{cases}$$
3. **Consistency Verification**: For all non-duplicate words, this exact threshold matches the author's original `Level.Teachers.Average` ground-truth with **100.0% fidelity (5,753/5,753 lines verified)**. For duplicate survey entries (50 groups), the aggregated score $\bar{s} = \frac{1}{k}\sum s_i$ resolves multi-annotator variance objectively under the exact same standard.
4. **Data Leakage Isolation**: The continuous `teachers_avg` score is strictly quarantined as a reference metadata column and **never exposed as an input feature $X$** during model training.

### 6.2 Empirical Distribution Comparison: Word-Level vs. Sentence-Level CEFR

Empirical analysis of the cleaned training datasets reveals a fundamental structural shift in class distributions between single words and complete sentences:
- **Word-Level Distribution** (5,697 words, Zenodo): Exhibits a relatively balanced bell-shaped distribution centered around intermediate vocabulary: A1 (15.5%), A2 (24.4%), B1 (30.3%), B2 (21.7%), C1 (8.1%). Foundational words (A1–A2) constitute ~40% of the lexical corpus.
- **Sentence-Level Distribution** (12,521 sentences, UniversalCEFR): Displays a pronounced rightward skew towards intermediate and upper-intermediate complexity: A1 (2.44%), A2 (15.52%), B1 (31.36%), B2 (33.74%), C1 (16.94%). Sentences in the B1–B2 range dominate nearly two-thirds (65.1%) of the corpus.
- **Linguistic Rationale & Sampling Bias Limitations**: While single tokens frequently reside at the A1 baseline (e.g., basic nouns, pronouns, numbers), complete natural sentences intrinsically require syntactic cohesion, prepositions, tense markers, and multi-word predicate structures that inherently elevate overall sentence readability to A2–B1. Furthermore, we explicitly acknowledge a **dataset sampling bias**: both `cefr_sp_en` (derived from standardized English proficiency examinations) and `readme_en` (compiled from academic textbooks) naturally target intermediate-to-advanced English learners, explaining why authentic A1 beginner sentences are scarce. Consequently, Model 2b will incorporate **balanced class weighting (`compute_class_weight`)** or cost-sensitive loss during training in Phase 3 to safeguard recall on the rare A1 sentence class.


---

## 7. Summary & Next Steps in Phase 1

With the mathematical, structural, and architectural scope fully clarified:
- **Phase 1 Part A**: Completed `input_type_detector.py` with robust `invalid_input` handling and 100% test pass rate.
- **Phase 1 Part B**: Construct feature engineering pipelines (`src/data/features.py`) and data curation scripts for both CEFR Word and CEFR Sentence datasets spanning levels A1–C1.

