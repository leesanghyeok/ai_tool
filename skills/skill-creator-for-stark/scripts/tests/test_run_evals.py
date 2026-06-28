"""scripts.run_evals_template용 단위 테스트다. 생성 skill에는 run_evals.py로 배포된다.

runner가 제공하는 두 모드, 즉 --validate(형식 검사)와 기본 실행
(golden baseline 대상 deterministic command check)을 다룬다.
"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from run_evals_template import (  # noqa: E402
    find_spec,
    llm_judge_criteria,
    main,
    parse_spec,
    run_command_checks,
    run_rollout,
    validate_spec,
)

# portable command check다(jq 의존성 없음). 기본 실행 모드에서는 {output}이
# expected baseline file에 binding된다.
PASS_CMD = "test -s {output}"          # expected file이 존재하고 비어 있지 않다
FAIL_CMD = "grep -q __NO_SUCH_TOKEN__ {output}"  # 존재하지 않는 token이므로 exit 1

WELL_FORMED_CRITERIA = [
    {"id": "non-empty", "text": "Output is non-empty", "type": "command", "cmd": PASS_CMD},
    {"id": "has-totals", "text": "Each region has a total", "type": "llm-judge"},
]


def _make_skill(
    tmp: Path,
    criteria: list[dict],
    golden: list[dict],
    run: str | None = None,
    pipeline_body: str | None = None,
) -> Path:
    """eval spec과 golden file을 가진 최소 skill directory를 만들고 반환한다.

    `run`이 주어지면 rollout command로 spec에 기록한다. `pipeline_body`가
    주어지면 보통 `run` command가 호출하는 scripts/run_pipeline.py에 기록해
    rollout이 실제 program을 실행하게 한다.
    """
    skill = tmp / "demo-skill"
    (skill / "scripts").mkdir(parents=True)
    evals = skill / "evals"
    evals.mkdir()
    for case in golden:
        case_dir = evals / "golden" / case["id"]
        case_dir.mkdir(parents=True)
        if case.get("input"):
            (evals / case["input"]).write_text("col\n1\n", encoding="utf-8")
        if case.get("expected"):
            (evals / case["expected"]).write_text('{"ok": true}\n', encoding="utf-8")
    if pipeline_body is not None:
        (skill / "scripts" / "run_pipeline.py").write_text(pipeline_body, encoding="utf-8")
    spec: dict = {"skill": "demo-skill", "criteria": criteria, "golden": golden}
    if run is not None:
        spec["run"] = run
    body = "# Eval Spec: demo-skill\n\nprose\n\n```json\n" + json.dumps(spec, indent=2) + "\n```\n"
    (evals / "demo-skill.eval.md").write_text(body, encoding="utf-8")
    return skill


# 단순한 실제 skill이다. --input을 읽고 canonical baseline을 --output에 쓴다.
# rollout test에서 produced output이 golden expected file과 일치하도록 사용한다.
_PIPELINE_COPIES_BASELINE = (
    "import argparse, pathlib\n"
    "ap = argparse.ArgumentParser()\n"
    "ap.add_argument('--input'); ap.add_argument('--output', required=True)\n"
    "a = ap.parse_args()\n"
    "pathlib.Path(a.output).write_text('{\"ok\": true}\\n')\n"
)
# command criterion이 틀렸다고 거부할 output을 쓰는 skill이다.
_PIPELINE_WRONG_OUTPUT = (
    "import argparse, pathlib\n"
    "ap = argparse.ArgumentParser()\n"
    "ap.add_argument('--input'); ap.add_argument('--output', required=True)\n"
    "a = ap.parse_args()\n"
    "pathlib.Path(a.output).write_text('WRONG\\n')\n"
)
_RUN_CMD = "python3 scripts/run_pipeline.py --input {input} --output {output}"


def _three_golden(with_expected: bool = True) -> list[dict]:
    cases = []
    for i in (1, 2, 3):
        case = {"id": f"case-{i}", "input": f"golden/case-{i}/input.csv", "split": "val"}
        if with_expected:
            case["expected"] = f"golden/case-{i}/expected.json"
        else:
            case["expected"] = None
            case["expected_status"] = "pending-first-green"
        cases.append(case)
    return cases


class ValidateSpecTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_well_formed_spec_has_no_errors(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        spec = parse_spec(find_spec(skill))
        self.assertEqual(validate_spec(spec, skill), [])

    def test_non_binary_grader_type_is_rejected(self) -> None:
        criteria = [{"id": "x", "text": "rate it", "type": "scale-1-5"}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("type" in e for e in validate_spec(spec, skill)))

    def test_command_criterion_without_cmd_is_rejected(self) -> None:
        criteria = [{"id": "x", "text": "valid json", "type": "command"}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("cmd" in e for e in validate_spec(spec, skill)))

    def test_fewer_than_three_golden_cases_is_rejected(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden()[:2])
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("golden cases" in e for e in validate_spec(spec, skill)))

    def test_null_expected_without_pending_flag_is_rejected(self) -> None:
        golden = _three_golden(with_expected=False)
        del golden[0]["expected_status"]  # null expected지만 flag가 없다
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, golden)
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("pending-first-green" in e for e in validate_spec(spec, skill)))

    def test_pending_first_green_is_valid(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden(with_expected=False))
        spec = parse_spec(find_spec(skill))
        self.assertEqual(validate_spec(spec, skill), [])

    def test_all_pending_first_green_warns_on_stderr(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden(with_expected=False))
        spec = parse_spec(find_spec(skill))
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(validate_spec(spec, skill), [])
        self.assertIn("pending-first-green", stderr.getvalue())

    def test_mixed_baselines_do_not_warn(self) -> None:
        golden = _three_golden()
        golden[0]["expected"] = None
        golden[0]["expected_status"] = "pending-first-green"
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, golden)
        spec = parse_spec(find_spec(skill))
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(validate_spec(spec, skill), [])
        self.assertEqual(stderr.getvalue(), "")


class RunCommandChecksTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_passing_command_check_zero_failures(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        spec = parse_spec(find_spec(skill))
        result = run_command_checks(spec, skill)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["passed"], 3)  # command criterion 1개 x case 3개

    def test_failing_command_check_is_counted(self) -> None:
        criteria = [{"id": "miss", "text": "has token", "type": "command", "cmd": FAIL_CMD}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        spec = parse_spec(find_spec(skill))
        result = run_command_checks(spec, skill)
        self.assertEqual(result["failed"], 3)

    def test_llm_judge_not_run_as_command(self) -> None:
        criteria = [{"id": "j", "text": "tone is right", "type": "llm-judge"}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        spec = parse_spec(find_spec(skill))
        result = run_command_checks(spec, skill)
        self.assertEqual(result["passed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(len(llm_judge_criteria(spec)), 1)

    def test_pending_first_green_case_is_skipped_not_failed(self) -> None:
        criteria = [{"id": "non-empty", "text": "non-empty", "type": "command", "cmd": PASS_CMD}]
        skill = _make_skill(self.tmp, criteria, _three_golden(with_expected=False))
        spec = parse_spec(find_spec(skill))
        result = run_command_checks(spec, skill)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["skipped"], 3)


class MainExitCodeTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_validate_well_formed_exits_zero(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        self.assertEqual(main([str(skill), "--validate"]), 0)

    def test_validate_malformed_exits_one(self) -> None:
        criteria = [{"id": "x", "text": "valid json", "type": "command"}]  # cmd 없음
        skill = _make_skill(self.tmp, criteria, _three_golden())
        self.assertEqual(main([str(skill), "--validate"]), 1)

    def test_run_all_pass_exits_zero(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        self.assertEqual(main([str(skill)]), 0)

    def test_run_with_failure_exits_one(self) -> None:
        criteria = [{"id": "miss", "text": "has token", "type": "command", "cmd": FAIL_CMD}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        self.assertEqual(main([str(skill)]), 1)

    def test_missing_spec_exits_two(self) -> None:
        empty = self.tmp / "no-evals-skill"
        empty.mkdir()
        self.assertEqual(main([str(empty)]), 2)


class RunFieldValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_absent_run_field_still_valid(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        spec = parse_spec(find_spec(skill))
        self.assertEqual(validate_spec(spec, skill), [])

    def test_run_without_output_placeholder_is_rejected(self) -> None:
        skill = _make_skill(
            self.tmp, WELL_FORMED_CRITERIA, _three_golden(), run="python3 scripts/run_pipeline.py"
        )
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("{output}" in e for e in validate_spec(spec, skill)))

    def test_empty_run_string_is_rejected(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden(), run="   ")
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("'run'" in e for e in validate_spec(spec, skill)))

    def test_well_formed_run_field_is_valid(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden(), run=_RUN_CMD)
        spec = parse_spec(find_spec(skill))
        self.assertEqual(validate_spec(spec, skill), [])


# rollout mode에서는 {output}이 PRODUCED output에 binding된다. skill이 baseline
# content를 쓰면 통과하고 WRONG을 쓰면 실패한다.
ROLLOUT_CRITERIA = [
    {"id": "has-ok", "text": "Output contains ok", "type": "command", "cmd": "grep -q ok {output}"},
]


class RunRolloutTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_happy_path_passes(self) -> None:
        skill = _make_skill(
            self.tmp, ROLLOUT_CRITERIA, _three_golden(), run=_RUN_CMD,
            pipeline_body=_PIPELINE_COPIES_BASELINE,
        )
        spec = parse_spec(find_spec(skill))
        result = run_rollout(spec, skill)
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["passed"], 3)  # criterion 1개 x case 3개

    def test_wrong_output_fails_not_errors(self) -> None:
        skill = _make_skill(
            self.tmp, ROLLOUT_CRITERIA, _three_golden(), run=_RUN_CMD,
            pipeline_body=_PIPELINE_WRONG_OUTPUT,
        )
        spec = parse_spec(find_spec(skill))
        result = run_rollout(spec, skill)
        self.assertEqual(result["errors"], 0)   # run 자체는 성공했다
        self.assertEqual(result["failed"], 3)   # 하지만 output이 틀렸다

    def test_failing_run_command_counts_as_error(self) -> None:
        skill = _make_skill(
            self.tmp, ROLLOUT_CRITERIA, _three_golden(),
            run="this_binary_does_not_exist_xyz --output {output}",
        )
        spec = parse_spec(find_spec(skill))
        result = run_rollout(spec, skill)
        self.assertEqual(result["errors"], 3)
        self.assertEqual(result["passed"], 0)

    def test_timeout_counts_as_error(self) -> None:
        skill = _make_skill(
            self.tmp, ROLLOUT_CRITERIA, _three_golden(),
            run="sleep 5; echo {output}",
        )
        spec = parse_spec(find_spec(skill))
        result = run_rollout(spec, skill, timeout=1)
        self.assertEqual(result["errors"], 3)

    def test_promote_captures_baseline_for_pending_case(self) -> None:
        skill = _make_skill(
            self.tmp, ROLLOUT_CRITERIA, _three_golden(with_expected=False), run=_RUN_CMD,
            pipeline_body=_PIPELINE_COPIES_BASELINE,
        )
        spec = parse_spec(find_spec(skill))
        result = run_rollout(spec, skill, promote=True)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(sorted(result["promoted"]), ["case-1", "case-2", "case-3"])
        # 캡처된 baseline이 이제 disk에 존재한다.
        captured = skill / "evals" / "golden" / "case-1" / "expected.json"
        self.assertTrue(captured.exists())
        self.assertIn("ok", captured.read_text())

    def test_only_case_restricts_rollout(self) -> None:
        skill = _make_skill(
            self.tmp, ROLLOUT_CRITERIA, _three_golden(), run=_RUN_CMD,
            pipeline_body=_PIPELINE_COPIES_BASELINE,
        )
        spec = parse_spec(find_spec(skill))
        result = run_rollout(spec, skill, only_case="case-2")
        self.assertEqual(result["passed"], 1)


class RolloutMainExitCodeTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_rollout_all_pass_exits_zero(self) -> None:
        skill = _make_skill(
            self.tmp, ROLLOUT_CRITERIA, _three_golden(), run=_RUN_CMD,
            pipeline_body=_PIPELINE_COPIES_BASELINE,
        )
        self.assertEqual(main([str(skill), "--rollout"]), 0)

    def test_rollout_wrong_output_exits_one(self) -> None:
        skill = _make_skill(
            self.tmp, ROLLOUT_CRITERIA, _three_golden(), run=_RUN_CMD,
            pipeline_body=_PIPELINE_WRONG_OUTPUT,
        )
        self.assertEqual(main([str(skill), "--rollout"]), 1)

    def test_rollout_without_run_field_exits_zero(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        self.assertEqual(main([str(skill), "--rollout"]), 0)


if __name__ == "__main__":
    unittest.main()
