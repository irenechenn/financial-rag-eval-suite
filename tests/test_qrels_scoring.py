from financial_rag_eval.qrels_scoring import build_qrels_report
from financial_rag_eval.reports import render_markdown_report
from financial_rag_eval.schemas import EvalCase, QrelJudgment, RetrievedChunk, RetrievalRunCase


def test_build_qrels_report_scores_only_selected_statuses() -> None:
    cases = [EvalCase(id="case_1", question="q", category="simple")]
    runs = [
        RetrievalRunCase(
            case_id="case_1",
            provider="mock",
            retrieved_chunks=[
                RetrievedChunk(chunk_id="a", rank=1),
                RetrievedChunk(chunk_id="b", rank=2),
            ],
        )
    ]
    qrels = [
        QrelJudgment(case_id="case_1", chunk_id="a", relevance=1, status="candidate"),
        QrelJudgment(case_id="case_1", chunk_id="c", relevance=1, status="accepted"),
    ]

    accepted_report = build_qrels_report(cases, runs, qrels, k=2, judgment_statuses={"accepted"})
    accepted_result = accepted_report.case_results[0]
    assert accepted_report.label_source == "qrels:accepted"
    assert accepted_result.precision_at_k == 0.0
    assert accepted_result.recall_at_k == 0.0
    assert accepted_result.missed_targets == ["c"]

    candidate_report = build_qrels_report(cases, runs, qrels, k=2, judgment_statuses={"candidate"})
    candidate_result = candidate_report.case_results[0]
    assert candidate_report.label_source == "qrels:candidate"
    assert candidate_result.precision_at_k == 0.5
    assert candidate_result.recall_at_k == 1.0
    assert candidate_result.covered_targets == ["a"]


def test_qrels_report_markdown_includes_label_source() -> None:
    report = build_qrels_report(
        cases=[EvalCase(id="case_1", question="q", category="simple")],
        runs=[
            RetrievalRunCase(
                case_id="case_1",
                provider="mock",
                retrieved_chunks=[RetrievedChunk(chunk_id="a", rank=1)],
            )
        ],
        qrels=[QrelJudgment(case_id="case_1", chunk_id="a", relevance=1, status="candidate")],
        k=1,
        judgment_statuses={"candidate"},
    )

    markdown = render_markdown_report(report)

    assert "Label source" in markdown
    assert "qrels:candidate" in markdown
