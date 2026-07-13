from financial_rag_eval.judge_agreement import compare_judge_decisions, render_agreement_markdown
from financial_rag_eval.qrels_review import QrelsReviewDecision


def test_compare_judge_decisions_reports_disagreements() -> None:
    baseline = [
        QrelsReviewDecision(case_id="case_1", chunk_id="a", decision="accepted", rationale="yes"),
        QrelsReviewDecision(case_id="case_1", chunk_id="b", decision="rejected", rationale="no"),
    ]
    candidate = [
        QrelsReviewDecision(case_id="case_1", chunk_id="a", decision="accepted", rationale="yes"),
        QrelsReviewDecision(case_id="case_1", chunk_id="b", decision="accepted", rationale="semantic match"),
    ]

    report = compare_judge_decisions(
        baseline=baseline,
        candidate=candidate,
        baseline_name="rubric",
        candidate_name="claude",
    )

    assert report.shared_decisions == 2
    assert report.agreements == 1
    assert report.disagreements == 1
    assert report.agreement_rate == 0.5
    assert report.deltas[0].chunk_id == "b"

    markdown = render_agreement_markdown(report)
    assert "Judge Agreement Report" in markdown
    assert "semantic match" in markdown
