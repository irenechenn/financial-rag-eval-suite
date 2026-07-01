from financial_rag_eval.agent_trace import (
    AgentTraceEvalCase,
    AgentTraceRun,
    ExpectedToolCall,
    ObservedToolCall,
    evaluate_agent_trace,
)


def test_agent_trace_passes_required_tool_sequence_and_arguments() -> None:
    case = AgentTraceEvalCase(
        case_id="compare",
        required_tool_calls=[
            ExpectedToolCall(
                tool_name="search_transcript_tool",
                ticker="MSFT",
                year=2023,
                query_terms=["cloud"],
            ),
            ExpectedToolCall(
                tool_name="search_transcript_tool",
                ticker="AMZN",
                year=2023,
                query_terms=["aws"],
            ),
        ],
    )
    run = AgentTraceRun(
        case_id="compare",
        provider="mock",
        tool_calls=[
            ObservedToolCall(
                tool_name="search_transcript_tool",
                step=1,
                arguments={"ticker": "MSFT", "year": 2023, "query": "cloud growth"},
            ),
            ObservedToolCall(
                tool_name="search_transcript_tool",
                step=2,
                arguments={"ticker": "AMZN", "year": 2023, "query": "aws demand"},
            ),
        ],
    )

    result = evaluate_agent_trace(case, run)

    assert result.tool_call_recall == 1.0
    assert result.argument_accuracy == 1.0
    assert result.tool_sequence_pass is True
    assert result.missing_tool_calls == []
    assert result.argument_failures == []


def test_agent_trace_catches_missing_tool_and_bad_arguments() -> None:
    case = AgentTraceEvalCase(
        case_id="compare",
        required_tool_calls=[
            ExpectedToolCall(
                tool_name="search_transcript_tool",
                ticker="MSFT",
                year=2023,
                query_terms=["cloud"],
            ),
            ExpectedToolCall(
                tool_name="search_transcript_tool",
                ticker="AMZN",
                year=2023,
                query_terms=["aws"],
            ),
        ],
    )
    run = AgentTraceRun(
        case_id="compare",
        provider="mock",
        tool_calls=[
            ObservedToolCall(
                tool_name="search_transcript_tool",
                step=1,
                arguments={"ticker": "MSFT", "year": 2024, "query": "cloud growth"},
            ),
        ],
    )

    result = evaluate_agent_trace(case, run)

    assert result.tool_call_recall == 0.5
    assert result.argument_accuracy == 0.5
    assert result.tool_sequence_pass is False
    assert result.missing_tool_calls == ["search_transcript_tool AMZN 2023 aws"]
    assert result.argument_failures == ["search_transcript_tool MSFT 2023 cloud"]