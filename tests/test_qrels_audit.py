from financial_rag_eval.qrels_audit import build_qrels_audit, render_qrels_audit_markdown
from financial_rag_eval.schemas import EvalCase, QrelJudgment


def test_build_qrels_audit_reports_coverage_and_integrity_issues() -> None:
    cases = [
        EvalCase(id="case_1", question="q", category="simple"),
        EvalCase(id="case_2", question="q", category="comparison"),
    ]
    qrels = [
        QrelJudgment(case_id="case_1", chunk_id="chunk_a", relevance=1, status="candidate"),
        QrelJudgment(case_id="case_1", chunk_id="chunk_a", relevance=1, status="candidate"),
        QrelJudgment(case_id="unknown_case", chunk_id="chunk_x", relevance=1, status="accepted"),
    ]

    report = build_qrels_audit(cases, qrels)

    assert report.total_cases == 2
    assert report.total_judgments == 3
    assert report.status_counts == {"accepted": 1, "candidate": 2}
    assert report.unknown_case_ids == ["unknown_case"]
    assert report.duplicate_judgments == ["case_1::chunk_a"]
    assert report.unlabeled_case_ids == ["case_2"]

    markdown = render_qrels_audit_markdown(report)
    assert "Qrels Audit Report" in markdown
    assert "case_2" in markdown
    assert "case_1::chunk_a" in markdown
