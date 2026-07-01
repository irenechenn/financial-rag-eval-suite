from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExpectedToolCall(BaseModel):
    tool_name: str
    ticker: str | None = None
    year: int | None = None
    query_terms: list[str] = Field(default_factory=list)


class ObservedToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    step: int = Field(ge=1)


class AgentTraceEvalCase(BaseModel):
    case_id: str
    required_tool_calls: list[ExpectedToolCall] = Field(default_factory=list)


class AgentTraceRun(BaseModel):
    case_id: str
    provider: str = "unknown"
    tool_calls: list[ObservedToolCall] = Field(default_factory=list)
    runtime_error: str | None = None


class AgentTraceMetricResult(BaseModel):
    case_id: str
    provider: str
    required_tool_calls: int
    observed_tool_calls: int
    tool_call_recall: float
    argument_accuracy: float
    tool_sequence_pass: bool
    missing_tool_calls: list[str] = Field(default_factory=list)
    argument_failures: list[str] = Field(default_factory=list)
    runtime_error: str | None = None


def evaluate_agent_trace(case: AgentTraceEvalCase, run: AgentTraceRun) -> AgentTraceMetricResult:
    required = case.required_tool_calls
    observed = sorted(run.tool_calls, key=lambda call: call.step)

    missing = _missing_tool_calls(required, observed)
    argument_failures = _argument_failures(required, observed)
    required_count = len(required)

    matched_tools = required_count - len(missing)
    argument_matches = required_count - len(argument_failures)

    return AgentTraceMetricResult(
        case_id=case.case_id,
        provider=run.provider,
        required_tool_calls=required_count,
        observed_tool_calls=len(observed),
        tool_call_recall=matched_tools / required_count if required_count else 1.0,
        argument_accuracy=argument_matches / required_count if required_count else 1.0,
        tool_sequence_pass=_tool_sequence_pass(required, observed),
        missing_tool_calls=missing,
        argument_failures=argument_failures,
        runtime_error=run.runtime_error,
    )


def _missing_tool_calls(
    required: list[ExpectedToolCall],
    observed: list[ObservedToolCall],
) -> list[str]:
    missing: list[str] = []
    used_indices: set[int] = set()
    for expected in required:
        match_index = _find_tool_name_match(expected, observed, used_indices)
        if match_index is None:
            missing.append(_expected_label(expected))
        else:
            used_indices.add(match_index)
    return missing


def _argument_failures(
    required: list[ExpectedToolCall],
    observed: list[ObservedToolCall],
) -> list[str]:
    failures: list[str] = []
    used_indices: set[int] = set()
    for expected in required:
        match_index = _find_tool_name_match(expected, observed, used_indices)
        if match_index is None:
            continue
        used_indices.add(match_index)
        actual = observed[match_index]
        if not _arguments_match(expected, actual.arguments):
            failures.append(_expected_label(expected))
    return failures


def _find_tool_name_match(
    expected: ExpectedToolCall,
    observed: list[ObservedToolCall],
    used_indices: set[int],
) -> int | None:
    for index, actual in enumerate(observed):
        if index in used_indices:
            continue
        if actual.tool_name == expected.tool_name:
            return index
    return None


def _tool_sequence_pass(
    required: list[ExpectedToolCall],
    observed: list[ObservedToolCall],
) -> bool:
    if not required:
        return True
    required_names = [item.tool_name for item in required]
    cursor = 0
    for actual in observed:
        if actual.tool_name == required_names[cursor]:
            cursor += 1
            if cursor == len(required_names):
                return True
    return False


def _arguments_match(expected: ExpectedToolCall, arguments: dict[str, Any]) -> bool:
    if expected.ticker is not None and str(arguments.get("ticker", "")).upper() != expected.ticker.upper():
        return False
    if expected.year is not None and arguments.get("year") != expected.year:
        return False
    if expected.query_terms:
        query = str(arguments.get("query", "")).lower()
        if not all(term.lower() in query for term in expected.query_terms):
            return False
    return True


def _expected_label(expected: ExpectedToolCall) -> str:
    pieces = [expected.tool_name]
    if expected.ticker:
        pieces.append(expected.ticker)
    if expected.year:
        pieces.append(str(expected.year))
    if expected.query_terms:
        pieces.append("+".join(expected.query_terms))
    return " ".join(pieces)