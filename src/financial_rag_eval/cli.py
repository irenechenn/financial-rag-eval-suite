from __future__ import annotations

import argparse

from financial_rag_eval.compare import (
    compare_reports,
    load_eval_report,
    write_comparison_json,
    write_comparison_markdown,
)
from financial_rag_eval.datasets import load_cases, load_retrieval_run
from financial_rag_eval.labeling import generate_label_candidates
from financial_rag_eval.project1_runner import run_project1_retrieval_sync
from financial_rag_eval.qrels import export_candidate_qrels
from financial_rag_eval.qrels_scoring import score_qrels_run
from financial_rag_eval.reports import build_report, write_json_report, write_markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate financial-rag-engine retrieval runs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-cases", help="Validate an eval case JSONL file.")
    validate.add_argument("cases")

    run_project1 = subparsers.add_parser("run-project1-retrieval", help="Run Project 1 FAISS retrieval for eval cases.")
    run_project1.add_argument("--cases", required=True)
    run_project1.add_argument("--out", required=True)
    run_project1.add_argument("--project1-path", default="C:\\Users\\18518\\Desktop\\ireneProjects\\financial-rag-engine")
    run_project1.add_argument("--index-path", default="C:\\Users\\18518\\Desktop\\ireneProjects\\financial-rag-engine\\indexes\\naive_voyage_finance")
    run_project1.add_argument("--top-k", type=int, default=3)
    run_project1.add_argument("--provider", default="voyage-faiss")
    run_project1.add_argument("--use-expected-filters", action="store_true")

    score = subparsers.add_parser("score-run", help="Score a retrieval run JSONL file.")
    score.add_argument("--cases", required=True)
    score.add_argument("--run", required=True)
    score.add_argument("--k", type=int, default=3)
    score.add_argument("--out-json", required=True)
    score.add_argument("--out-md", required=True)

    score_qrels = subparsers.add_parser("score-qrels", help="Score a retrieval run using qrel judgments.")
    score_qrels.add_argument("--cases", required=True)
    score_qrels.add_argument("--run", required=True)
    score_qrels.add_argument("--qrels", required=True)
    score_qrels.add_argument("--k", type=int, default=3)
    score_qrels.add_argument(
        "--judgment-status",
        action="append",
        choices=["candidate", "accepted", "rejected"],
        default=None,
        help="Qrel status to include. Defaults to accepted. Repeat to include multiple statuses.",
    )
    score_qrels.add_argument("--out-json", required=True)
    score_qrels.add_argument("--out-md", required=True)

    compare = subparsers.add_parser("compare-runs", help="Compare two retrieval evaluation reports.")
    compare.add_argument("--baseline", required=True)
    compare.add_argument("--candidate", required=True)
    compare.add_argument("--baseline-name", default="baseline")
    compare.add_argument("--candidate-name", default="candidate")
    compare.add_argument("--out-json", required=True)
    compare.add_argument("--out-md", required=True)

    labels = subparsers.add_parser("suggest-labels", help="Generate candidate relevant chunk IDs for human review.")
    labels.add_argument("--cases", required=True)
    labels.add_argument("--run", required=True)
    labels.add_argument("--k", type=int, default=3)
    labels.add_argument("--out-jsonl", required=True)
    labels.add_argument("--out-md", required=True)

    qrels = subparsers.add_parser("export-qrels", help="Export pooled candidate qrels for human review.")
    qrels.add_argument("--cases", required=True)
    qrels.add_argument("--run", required=True)
    qrels.add_argument("--k", type=int, default=3)
    qrels.add_argument("--source", default="retrieval-pool")
    qrels.add_argument("--out-jsonl", required=True)
    qrels.add_argument("--out-md", required=True)

    args = parser.parse_args()

    if args.command == "validate-cases":
        cases = load_cases(args.cases)
        categories = sorted({case.category for case in cases})
        print(f"Validated {len(cases)} cases across categories: {', '.join(categories)}")
        return

    if args.command == "run-project1-retrieval":
        runs = run_project1_retrieval_sync(
            cases_path=args.cases,
            output_path=args.out,
            project1_path=args.project1_path,
            index_path=args.index_path,
            top_k=args.top_k,
            provider=args.provider,
            use_expected_filters=args.use_expected_filters,
        )
        errors = sum(1 for run in runs if run.runtime_error)
        print(f"Wrote {len(runs)} retrieval cases to {args.out} ({errors} runtime errors)")
        return

    if args.command == "score-run":
        cases = load_cases(args.cases)
        run = load_retrieval_run(args.run)
        report = build_report(cases, run, args.k)
        write_json_report(report, args.out_json)
        write_markdown_report(report, args.out_md)
        print(f"Scored {len(report.case_results)} cases at k={args.k}")
        print(f"Wrote {args.out_json}")
        print(f"Wrote {args.out_md}")
        return

    if args.command == "score-qrels":
        report = score_qrels_run(
            cases_path=args.cases,
            run_path=args.run,
            qrels_path=args.qrels,
            out_json=args.out_json,
            out_md=args.out_md,
            k=args.k,
            judgment_statuses=set(args.judgment_status or ["accepted"]),
        )
        print(f"Scored {len(report.case_results)} cases at k={args.k} using {report.label_source}")
        print(f"Wrote {args.out_json}")
        print(f"Wrote {args.out_md}")
        return

    if args.command == "compare-runs":
        comparison = compare_reports(
            baseline=load_eval_report(args.baseline),
            candidate=load_eval_report(args.candidate),
            baseline_name=args.baseline_name,
            candidate_name=args.candidate_name,
        )
        write_comparison_json(comparison, args.out_json)
        write_comparison_markdown(comparison, args.out_md)
        print(f"Compared {len(comparison.case_deltas)} shared cases")
        print(f"Wrote {args.out_json}")
        print(f"Wrote {args.out_md}")
        return

    if args.command == "suggest-labels":
        candidates = generate_label_candidates(
            cases_path=args.cases,
            run_path=args.run,
            out_jsonl=args.out_jsonl,
            out_md=args.out_md,
            k=args.k,
        )
        candidate_count = sum(len(item.candidates) for item in candidates)
        print(f"Generated {candidate_count} candidate chunk labels across {len(candidates)} cases")
        print(f"Wrote {args.out_jsonl}")
        print(f"Wrote {args.out_md}")
        return

    if args.command == "export-qrels":
        qrels_output = export_candidate_qrels(
            cases_path=args.cases,
            run_path=args.run,
            out_jsonl=args.out_jsonl,
            out_md=args.out_md,
            k=args.k,
            source=args.source,
        )
        print(f"Exported {len(qrels_output)} candidate qrels")
        print(f"Wrote {args.out_jsonl}")
        print(f"Wrote {args.out_md}")
        return


if __name__ == "__main__":
    main()
