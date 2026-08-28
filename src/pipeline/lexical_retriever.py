"""Vietnamese-English lexical retrieval performed before CEFR classification."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
import sqlite3
import unicodedata
from pathlib import Path

from wordfreq import zipf_frequency

from src.pipeline.semantic_reranker import SemanticReranker
from src.pipeline.vocabulary_candidates import ENGLISH_TERM, normalize_to_lemma

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEXICON = PROJECT_ROOT / "data/external/vi_en_dictionary/vi_en_dict.db"
WORD_RE = re.compile(r"[0-9A-Za-zÀ-ỹĐđ]+", re.UNICODE)
SENSE_SPLIT = re.compile(r"\s*[;,]\s*")


def normalize_vietnamese(value: str) -> str:
    text = unicodedata.normalize("NFC", str(value)).casefold().strip()
    return " ".join(WORD_RE.findall(text))


def map_dictionary_pos(raw_pos: str | None) -> tuple[str, ...]:
    raw = normalize_vietnamese(raw_pos or "")
    located = []
    for marker, pos in (
        ("danh từ", "NOUN"),
        ("tính từ", "ADJ"),
        ("ngoại động từ", "VERB"),
        ("nội động từ", "VERB"),
        ("động từ", "VERB"),
        ("phó từ", "ADV"),
        ("giới từ", "ADP"),
        ("mạo từ", "DET"),
        ("đại từ", "PRON"),
        ("liên từ", "CONJ"),
    ):
        if marker in raw:
            located.append((raw.index(marker), pos))
    mapped = []
    for _, pos in sorted(located):
        if pos not in mapped:
            mapped.append(pos)
    return tuple(mapped)


def _query_variants(query: str) -> list[str]:
    variants = [query]
    tokens = query.split()
    if len(tokens) > 1 and tokens[0] in {"con", "cái", "sự", "tính", "việc"}:
        variants.append(" ".join(tokens[1:]))
    return variants


def _sense_match(query: str, definition: str) -> tuple[float, str]:
    """Return lexical relevance and the smallest matching dictionary sense."""
    best_score, best_sense = 0.0, ""
    for raw_sense in SENSE_SPLIT.split(definition):
        sense = normalize_vietnamese(raw_sense)
        if not sense:
            continue
        tokens = sense.split()
        score = 0.0
        for variant_index, variant in enumerate(_query_variants(query)):
            query_tokens = variant.split()
            variant_penalty = 0.02 * variant_index
            if sense == variant:
                candidate_score = 1.0 - variant_penalty
            elif len(query_tokens) <= len(tokens) and any(
                tokens[index : index + len(query_tokens)] == query_tokens
                for index in range(len(tokens) - len(query_tokens) + 1)
            ):
                # Prefer compact senses; this demotes dictionary rows where the
                # query appears only inside a long idiom or specialist note.
                candidate_score = (
                    0.9 - variant_penalty - min(0.3, 0.015 * (len(tokens) - len(query_tokens)))
                )
            else:
                overlap = len(set(query_tokens) & set(tokens)) / max(len(set(query_tokens)), 1)
                candidate_score = overlap * 0.45
            score = max(score, candidate_score)
        if score > best_score:
            best_score, best_sense = score, raw_sense.strip()
    return best_score, best_sense


@dataclass(frozen=True)
class LexicalCandidate:
    lemma: str
    part_of_speech: str | None
    sense_id: str
    vietnamese_gloss: str
    source: str
    lexical_score: float
    semantic_score: float
    relevance_score: float
    translation_rank: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class VietnameseEnglishLexicon:
    """Retrieve meaning/POS candidates without consulting CEFR."""

    def __init__(
        self,
        database_path: Path | str | None = None,
        semantic_reranker: SemanticReranker | None = None,
        device: str = "auto",
    ):
        self.database_path = Path(database_path or DEFAULT_LEXICON)
        if not self.database_path.exists():
            raise FileNotFoundError(f"Vietnamese-English lexicon is missing: {self.database_path}")
        self.semantic_reranker = semantic_reranker or SemanticReranker(device=device)

    def _rows(self, query: str) -> list[tuple]:
        variants = _query_variants(query)
        tokens = variants[-1].split()
        clauses = " AND ".join("lower(vi) LIKE ?" for _ in tokens)
        parameters = [f"%{token}%" for token in tokens]
        statement = f"""
            SELECT entry_id, en, pos, vi
            FROM dictionary_entries
            WHERE {clauses}
        """
        with sqlite3.connect(self.database_path) as connection:
            return connection.execute(statement, parameters).fetchall()

    def retrieve(self, vietnamese: str, limit: int = 40) -> list[LexicalCandidate]:
        query = normalize_vietnamese(vietnamese)
        if not query:
            return []
        preliminary = []
        for entry_id, english, raw_pos, definition in self._rows(query):
            english = str(english).strip().casefold()
            if not ENGLISH_TERM.fullmatch(english) or len(english.split()) > 3:
                continue
            lexical_score, matching_sense = _sense_match(query, str(definition or ""))
            if lexical_score < 0.6:
                continue
            positions = map_dictionary_pos(raw_pos) or (None,)
            for pos in positions:
                lemma = normalize_to_lemma(english, pos)
                preliminary.append(
                    {
                        "lemma": lemma,
                        "pos": pos,
                        "sense_id": f"avdict:{entry_id}:{pos or 'UNKNOWN'}",
                        "gloss": matching_sense,
                        "lexical": lexical_score,
                        "frequency": min(1.0, max(0.0, zipf_frequency(lemma, "en") / 7.0)),
                        "register_penalty": (
                            0.18
                            if any(
                                marker in normalize_vietnamese(raw_pos or "")
                                for marker in ("từ cổ", "nghĩa cổ", "từ hiếm", "nghĩa hiếm")
                            )
                            else 0.0
                        ),
                    }
                )

        # Deduplicate by lemma+POS before the heavier semantic pass.
        deduplicated: dict[tuple[str, str | None], dict] = {}
        for item in preliminary:
            key = (item["lemma"].casefold(), item["pos"])
            previous = deduplicated.get(key)
            if previous is None or item["lexical"] > previous["lexical"]:
                deduplicated[key] = item
        shortlist = sorted(
            deduplicated.values(), key=lambda item: (-item["lexical"], item["lemma"])
        )[: max(limit * 3, 80)]
        # Score against the English lemma itself. Including the Vietnamese
        # dictionary gloss here would let every exact substring look equally
        # semantic and would preserve idiomatic false positives such as
        # Vietnamese "giúp đỡ" -> English "see".
        passages = [item["lemma"] for item in shortlist]
        english_scores = self.semantic_reranker.score(vietnamese, passages)
        gloss_scores = self.semantic_reranker.score(
            vietnamese, [item["gloss"] for item in shortlist]
        )
        results = []
        for item, english_score, gloss_score in zip(shortlist, english_scores, gloss_scores):
            semantic = 0.6 * english_score + 0.4 * gloss_score
            # Lexical evidence dominates because the dictionary gloss is an
            # explicit bilingual link. E5 resolves ties and near matches.
            relevance = (
                0.25 * item["lexical"]
                + 0.65 * max(0.0, semantic)
                + 0.10 * item["frequency"]
                - item["register_penalty"]
            )
            results.append(
                LexicalCandidate(
                    lemma=item["lemma"],
                    part_of_speech=item["pos"],
                    sense_id=item["sense_id"],
                    vietnamese_gloss=item["gloss"],
                    source="AVDict Vietnamese-English dictionary",
                    lexical_score=round(item["lexical"], 4),
                    semantic_score=round(semantic, 4),
                    relevance_score=round(relevance, 4),
                    translation_rank=None,
                )
            )
        return sorted(results, key=lambda item: (-item.relevance_score, item.lemma))[:limit]

    def validate_english_candidates(
        self, vietnamese: str, english_candidates: list[str], limit: int = 40
    ) -> list[LexicalCandidate]:
        """Validate model-produced candidates against bilingual senses."""
        rows = []
        with sqlite3.connect(self.database_path) as connection:
            for rank, candidate in enumerate(english_candidates):
                lemma = normalize_to_lemma(candidate)
                if not ENGLISH_TERM.fullmatch(lemma) or len(lemma.split()) > 3:
                    continue
                matches = connection.execute(
                    "SELECT entry_id, en, pos, vi FROM dictionary_entries WHERE lower(en) = ?",
                    (lemma.casefold(),),
                ).fetchall()
                for entry_id, english, raw_pos, definition in matches:
                    lexical, gloss = _sense_match(normalize_vietnamese(vietnamese), definition)
                    positions = map_dictionary_pos(raw_pos) or (None,)
                    for pos in positions:
                        rows.append(
                            {
                                "lemma": normalize_to_lemma(english, pos),
                                "pos": pos,
                                "sense_id": f"avdict:{entry_id}:{pos or 'UNKNOWN'}",
                                "gloss": gloss or str(definition).split(";")[0].strip(),
                                "lexical": lexical,
                                "rank": rank,
                            }
                        )
        unique: dict[tuple[str, str | None], dict] = {}
        for item in rows:
            key = (item["lemma"].casefold(), item["pos"])
            if key not in unique or item["lexical"] > unique[key]["lexical"]:
                unique[key] = item
        shortlist = list(unique.values())
        english_scores = self.semantic_reranker.score(
            vietnamese, [item["lemma"] for item in shortlist]
        )
        gloss_scores = self.semantic_reranker.score(
            vietnamese, [item["gloss"] for item in shortlist]
        )
        best_gloss_score = max(gloss_scores, default=0.0)
        results = []
        for item, english_score, gloss_score in zip(shortlist, english_scores, gloss_scores):
            if (
                item["rank"] > 0
                and item["lexical"] < 0.6
                and (best_gloss_score == 0.0 or gloss_score < best_gloss_score - 0.015)
            ):
                continue
            semantic_score = 0.55 * english_score + 0.45 * gloss_score
            frequency = min(1.0, max(0.0, zipf_frequency(item["lemma"], "en") / 7.0))
            relevance = (
                0.25 * item["lexical"]
                + 0.63 * max(0.0, semantic_score)
                + 0.10 * frequency
                + 0.08 / (item["rank"] + 1)
            )
            results.append(
                LexicalCandidate(
                    lemma=item["lemma"],
                    part_of_speech=item["pos"],
                    sense_id=item["sense_id"],
                    vietnamese_gloss=item["gloss"],
                    source="Marian candidate validated by AVDict + multilingual E5",
                    lexical_score=round(item["lexical"], 4),
                    semantic_score=round(semantic_score, 4),
                    relevance_score=round(relevance, 4),
                    translation_rank=item["rank"],
                )
            )
        return sorted(results, key=lambda item: (-item.relevance_score, item.lemma))[:limit]
