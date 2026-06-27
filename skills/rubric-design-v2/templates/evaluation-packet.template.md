# 평가 패킷 (Evaluation Packet)

## 평가 대상

{evaluation_target}

## 평가할 출력

{evaluated_output}

## 허용 근거

{allowed_evidence_bundle}

## 제외 context

- 현재 대화 기록: 명시적으로 포함하지 않았다면 제외한다.
- agent memory: 명시적으로 포함하지 않았다면 제외한다.
- implementation notes: 명시적으로 포함하지 않았다면 제외한다.
- unstated assumptions: 제외한다.

## 루브릭

{rubric_document_or_path}

## 판정 실행 모드

- `judging_mode`: `{clean_subagent | parallel_clean_subagents | same_context_exception}`
- `shard_boundary`: `{dimension_or_checklist_groups}`
- `parent_aggregation`: JSON parse, score bounds, 누락/중복 기준, local caps, global caps

## 출력 형식

`judge-scorecard.schema.json`과 호환되는 JSON만 반환한다.
