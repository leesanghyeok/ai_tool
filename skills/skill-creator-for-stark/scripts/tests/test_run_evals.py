"""case-based scripts.run_evals runner의 검증 의도를 설명하는 단위 테스트다."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from run_evals import (  # noqa: E402
    find_spec,
    load_cases,
    main,
    parse_spec,
    run_suite,
    validate_spec,
)
def _spec_path(skill: Path) -> Path:
    spec = find_spec(skill)
    assert spec is not None
    return spec


def _capture_main(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


def _assert_cli_result(
    test: unittest.TestCase,
    result: tuple[int, str, str],
    *,
    code: int,
    stdout_token: str | None = None,
    stderr_token: str | None = None,
) -> None:
    actual_code, stdout, stderr = result
    test.assertEqual(actual_code, code)
    if stdout_token is None:
        test.assertEqual(stdout, "")
    else:
        test.assertIn(stdout_token, stdout)
    if stderr_token is None:
        test.assertEqual(stderr, "")
    else:
        test.assertIn(stderr_token, stderr)


def _inline_script(source: str) -> str:
    return dedent(source).lstrip()


PIPELINE_OK = _inline_script(
    """
    import argparse, pathlib
    ap = argparse.ArgumentParser()
    ap.add_argument('--input'); ap.add_argument('--output', required=True)
    a = ap.parse_args()
    pathlib.Path(a.output).write_text('{"ok": true}\\n')
    """,
)
PIPELINE_WRONG = _inline_script(
    """
    import argparse, pathlib
    ap = argparse.ArgumentParser()
    ap.add_argument('--input'); ap.add_argument('--output', required=True)
    a = ap.parse_args()
    pathlib.Path(a.output).write_text('{"ok": false}\\n')
    """,
)
PIPELINE_PROVENANCE = _inline_script(
    """
    import argparse, json, pathlib
    ap = argparse.ArgumentParser()
    ap.add_argument('--input'); ap.add_argument('--output', required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.output)
    artifact = out.parent / 'generated.md'
    artifact.write_text('generated evidence\\n', encoding='utf-8')
    payload = {
        'schema_version': 1,
        'status': 'success',
        'files_written': [{'path': str(artifact), 'action': 'create'}],
        'errors': [],
    }
    out.write_text(json.dumps(payload, ensure_ascii=False) + '\\n', encoding='utf-8')
    """,
)
JUDGE_PASS = _inline_script(
    """
    import argparse, json, pathlib, sys
    argv = sys.argv[1:]
    mode = argv.pop(0) if argv and argv[0] in {'output', 'assertion'} else 'legacy'
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True); ap.add_argument('--output', required=True)
    a = ap.parse_args(argv)
    p = json.load(open(a.input))
    assert p['schema_version'] == 1
    if mode == 'output':
        content = 'primary: ' + p['prompt'][:40]
        payload = {
            'schema_version': 1,
            'status': 'success',
            'output': {'format': 'text', 'content': content, 'summary': content},
            'artifacts': [],
            'redactions_applied': [],
            'errors': [],
        }
        pathlib.Path(a.output).write_text(json.dumps(payload, ensure_ascii=False))
    elif mode == 'assertion':
        results = [
            {'assertion_id': x['id'], 'status': 'pass', 'judge_output': 'ok', 'session_id': 'test'}
            for x in p['assertions']
        ]
        payload = {
            'schema_version': 1,
            'status': 'success',
            'method': p['method'],
            'primary_output_ref': {'sha256': 'x'},
            'results': results,
            'errors': [],
        }
        pathlib.Path(a.output).write_text(json.dumps(payload, ensure_ascii=False))
    else:
        pathlib.Path(a.output).write_text('상태: pass\\n판단: ' + p['prompt'][:20])
    """,
)
JUDGE_FAIL = _inline_script(
    """
    import argparse, pathlib, sys
    argv = sys.argv[1:]
    if argv and argv[0] in {'output', 'assertion'}:
        argv.pop(0)
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True); ap.add_argument('--output', required=True)
    a = ap.parse_args(argv)
    pathlib.Path(a.output).write_text('')
    """,
)


def _write_runner_scripts(skill: Path, *, pipeline: str, judge: str) -> None:
    scripts = skill / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "run_pipeline.py").write_text(pipeline, encoding="utf-8")
    (scripts / "run_llm_judge.py").write_text(judge, encoding="utf-8")


def _write_case_files(case_dir: Path, *, include_expected: bool, case_type: str) -> None:
    case_dir.mkdir(parents=True)
    input_text = '{"schema_version":1,"prompt":"make skill"}\n' if case_type == "llm-judge" else '{"request":"make skill"}\n'
    (case_dir / "input.json").write_text(input_text, encoding="utf-8")
    if include_expected:
        (case_dir / "expected.json").write_text('{"ok": true}\n', encoding="utf-8")


def _case_yaml(*, include_expected: bool, case_type: str, llm_setup: bool) -> str:
    if case_type == "llm-judge":
        expected_line = run_block = ""
        assertions = _llm_judge_assertions(llm_setup=llm_setup)
    else:
        expected_line = "expected: expected.json\n" if include_expected else ""
        run_block = _pipeline_run_block()
        assertions = COMMAND_ASSERTIONS
    return f"""id: case-1
type: {case_type}
title: 기본 케이스
input: input.json
{expected_line}{run_block}{assertions}"""


def _pipeline_run_block() -> str:
    return """run:
  command: {python} scripts/run_pipeline.py --input {input} --output {output}
  timeout_sec: 30
"""


COMMAND_ASSERTIONS = """assertions:
  - id: valid-json
    title: 출력이 JSON인지 검증
    type: command
    cmd: {python} -m json.tool {output}
"""


def _llm_judge_assertions(*, llm_setup: bool) -> str:
    setup_block = "" if not llm_setup else """setup:
  command: {python} scripts/run_pipeline.py --input {input} --output {pipeline_output}
  timeout_sec: 30
"""
    return f"""{setup_block}judge:
  method: each-session
  command: {{python}} scripts/run_llm_judge.py assertion --input {{assertion_input}} --output {{judge_output}}
  timeout_sec: 30
assertions:
  - id: semantic-quality
    title: 의미 품질 검증
    type: llm-judge
    prompt: 출력이 실행 가능한 절차를 포함한다.
"""


def _write_manifest(skill: Path, *, case_type: str) -> None:
    (skill / "evals" / "demo-skill.eval.yaml").write_text(
        f"""version: 1
skill: demo-skill
title: 데모 스킬 eval suite
test_policy:
  expected_compare: auto
  llm_judge: required
  promote: allow-overwrite
cases:
  - id: case-1
    type: {case_type}
    title: 기본 케이스
    path: cases/case-1/case.yaml
""",
        encoding="utf-8",
    )


def _write_undeclared_case(skill: Path) -> None:
    extra = skill / "evals" / "cases" / "extra"
    extra.mkdir(parents=True)
    (extra / "case.yaml").write_text("id: extra\ntype: happy-path\ntitle: 미선언\n", encoding="utf-8")


def _make_skill(
    tmp: Path,
    *,
    pipeline: str = PIPELINE_OK,
    judge: str = JUDGE_PASS,
    include_expected: bool = True,
    case_type: str = "happy-path",
    undeclared: bool = False,
    llm_setup: bool = False,
) -> Path:
    skill = tmp / "demo-skill"
    case_dir = skill / "evals" / "cases" / "case-1"
    _write_runner_scripts(skill, pipeline=pipeline, judge=judge)
    _write_case_files(case_dir, include_expected=include_expected, case_type=case_type)
    (case_dir / "case.yaml").write_text(_case_yaml(include_expected=include_expected, case_type=case_type, llm_setup=llm_setup), encoding="utf-8")
    _write_manifest(skill, case_type=case_type)
    if undeclared:
        _write_undeclared_case(skill)
    return skill


class EvalRunnerTestBase(unittest.TestCase):
    """run_evals runner 테스트가 공유하는 임시 skill fixture lifecycle을 제공한다."""
    """각 테스트 호출 전"""
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    """각 테스트 호출 후"""
    def tearDown(self) -> None:
        self._tmp.cleanup()



class EvalManifestDiscoveryTest(EvalRunnerTestBase):
    """eval.yaml validation과 case discovery 계약을 검증한다; class명 Manifest는 legacy/internal 명칭이다."""

    def test_validate_well_formed_case_suite(self) -> None:
        """정상적인 eval suite가 validation error 없이 로드되는지 검증한다."""
        skill = _make_skill(self.tmp)
        spec = parse_spec(_spec_path(skill))
        self.assertEqual(validate_spec(spec, skill), [])
        self.assertEqual(len(load_cases(spec, skill)), 1)


    def test_eval_yaml_is_source_of_truth_for_cases(self) -> None:
        """eval.yaml에 선언되지 않은 leftover case directory는 validate/run 대상에서 제외되어야 한다."""
        skill = _make_skill(self.tmp, undeclared=True)
        spec = parse_spec(_spec_path(skill))
        self.assertEqual(validate_spec(spec, skill), [])
        self.assertEqual([case["id"] for case in load_cases(spec, skill)], ["case-1"])


    def test_declared_missing_case_file_is_validation_error(self) -> None:
        """declared case.yaml 누락 시 validation error 반환."""
        skill = _make_skill(self.tmp)
        (skill / "evals" / "cases" / "case-1" / "case.yaml").unlink()
        spec = parse_spec(_spec_path(skill))
        self.assertTrue(any("case file not found" in e for e in validate_spec(spec, skill)))


    def test_eval_yaml_unknown_top_level_field_is_schema_error(self) -> None:
        """eval.yaml top-level field set을 schema source of truth로 검증한다."""
        skill = _make_skill(self.tmp)
        spec_path = _spec_path(skill)
        spec_path.write_text(spec_path.read_text() + "description: no\n", encoding="utf-8")
        spec = parse_spec(spec_path)
        errors = validate_spec(spec, skill)
        self.assertTrue(any("unknown field 'description'" in e for e in errors))

    def test_nested_case_yaml_unknown_field_is_schema_error(self) -> None:
        """declared case.yaml 하위 object의 unknown field도 schema violation으로 잡는다."""
        skill = _make_skill(self.tmp)
        cpath = skill / "evals" / "cases" / "case-1" / "case.yaml"
        cpath.write_text(cpath.read_text() + "extra_field: no\n", encoding="utf-8")
        errors = validate_spec(parse_spec(_spec_path(skill)), skill)
        self.assertTrue(any("unknown field 'extra_field'" in e for e in errors))

    def test_nested_assertion_malformed_field_is_schema_error(self) -> None:
        """assertions[] 내부 field type과 허용 field set을 nested schema로 검증한다."""
        skill = _make_skill(self.tmp)
        cpath = skill / "evals" / "cases" / "case-1" / "case.yaml"
        cpath.write_text(cpath.read_text().replace("timeout_sec: 30", "timeout_sec: nope"), encoding="utf-8")
        errors = validate_spec(parse_spec(_spec_path(skill)), skill)
        self.assertTrue(any("run.timeout_sec: must be int" in e for e in errors))



class EvalExpectedPromotionTest(EvalRunnerTestBase):
    """expected equality와 --promote behavior를 검증하기 위해 분리한 class다."""

    def test_expected_file_triggers_automatic_equality_pass(self) -> None:
        """expected.json이 있으면 output과 자동 equality 비교를 수행하고 통과로 기록되는지 검증한다."""
        skill = _make_skill(self.tmp)
        result = run_suite(parse_spec(_spec_path(skill)), skill)
        self.assertEqual(result["failed"], 0)
        checks = result["cases"][0]["checks"]
        self.assertTrue(any(c["id"] == "expected-equality" and c["status"] == "pass" for c in checks))


    def test_expected_file_triggers_automatic_equality_failure(self) -> None:
        """expected.json과 실제 output이 다르면 자동 equality 비교가 실패로 기록되는지 검증한다."""
        skill = _make_skill(self.tmp, pipeline=PIPELINE_WRONG)
        result = run_suite(parse_spec(_spec_path(skill)), skill)
        self.assertEqual(result["failed"], 1)
        checks = result["cases"][0]["checks"]
        self.assertTrue(any(c["id"] == "expected-equality" and c["status"] == "fail" for c in checks))


    def test_promote_creates_expected_when_missing(self) -> None:
        """--promote 실행 시 누락된 expected.json을 현재 output으로 생성하는지 검증한다."""
        skill = _make_skill(self.tmp, include_expected=False)
        result = run_suite(parse_spec(_spec_path(skill)), skill, promote=True)
        self.assertEqual(result["failed"], 0)
        self.assertTrue((skill / "evals" / "cases" / "case-1" / "expected.json").exists())


    def test_promote_overwrites_existing_expected(self) -> None:
        """--promote 실행 시 기존 expected.json을 현재 output으로 덮어쓰는지 검증한다."""
        skill = _make_skill(self.tmp, pipeline=PIPELINE_WRONG)
        result = run_suite(parse_spec(_spec_path(skill)), skill, promote=True)
        self.assertEqual(result["failed"], 0)
        self.assertEqual((skill / "evals" / "cases" / "case-1" / "expected.json").read_text(), '{"ok": false}\n')



class EvalLlmJudgeProvenanceTest(EvalRunnerTestBase):
    """llm-judge execution/provenance boundary를 검증하기 위해 분리한 class다."""

    def test_llm_judge_failure_fails_case(self) -> None:
        """llm-judge가 빈 output을 내는 실패 상황을 case 실패로 처리하는지 검증한다."""
        skill = _make_skill(self.tmp, judge=JUDGE_FAIL, case_type="llm-judge")
        result = run_suite(parse_spec(_spec_path(skill)), skill)
        self.assertEqual(result["failed"], 1)
        self.assertTrue(any(c["type"] == "llm-judge" and c["status"] == "fail" for c in result["cases"][0]["checks"]))


    def test_llm_judge_case_must_not_define_run_command(self) -> None:
        """llm-judge case가 run.command를 직접 정의하면 안 된다는 boundary를 검증한다."""
        skill = _make_skill(self.tmp, case_type="llm-judge")
        spec = parse_spec(_spec_path(skill))
        self.assertEqual(validate_spec(spec, skill), [])
        result = run_suite(spec, skill)
        self.assertEqual(result["failed"], 0)
        # llm-judge case에 금지된 run block을 강제로 넣어 validation boundary를 확인한다.
        cpath = skill / "evals" / "cases" / "case-1" / "case.yaml"
        cpath.write_text(cpath.read_text() + "run:\n  command: echo bad > {output}\n", encoding="utf-8")
        self.assertTrue(any("must not define run.command" in e for e in validate_spec(spec, skill)))


    def test_llm_judge_setup_provenance_uses_pipeline_output(self) -> None:
        """llm-judge setup.command 결과와 pipeline_output provenance가 judge evidence에 연결되는지 검증한다."""
        skill = _make_skill(self.tmp, pipeline=PIPELINE_PROVENANCE, case_type="llm-judge", llm_setup=True)
        spec = parse_spec(_spec_path(skill))
        self.assertEqual(validate_spec(spec, skill), [])
        result = run_suite(spec, skill)
        self.assertEqual(result["failed"], 0)
        checks = result["cases"][0]["checks"]
        setup = next(c for c in checks if c["id"] == "judge.setup")
        self.assertEqual(setup["pipeline_output_status"], "success")
        judge_check = next(c for c in checks if c["id"] == "semantic-quality")
        evidence = judge_check["evidence"]["provenance"]
        self.assertEqual(evidence["setup"]["pipeline_output_status"], "success")
        self.assertEqual(evidence["primary_output"]["kind"], "pipeline-output")
        self.assertTrue(evidence["files_written_read_back"][0]["exists"])



FLAT_CASE_GROUP_YAML = """id: case-group
type: happy-path
cases:
  - id: alpha 실행
    input: input.json
    expected: expected.json
    run:
      command: {python} scripts/run_pipeline.py --input {input} --output {output}
      timeout_sec: 30
    assertions:
      - id: valid-json
        title: 출력이 JSON인지 검증
        type: command
        cmd: {python} -m json.tool {output}
  - id: beta 실행
    input: input.json
    expected: expected.json
    run:
      command: {python} scripts/run_pipeline.py --input {input} --output {output}
      timeout_sec: 30
    assertions:
      - id: valid-json
        title: 출력이 JSON인지 검증
        type: command
        cmd: {python} -m json.tool {output}
"""

ENTRIES_MANIFEST_YAML = """version: 1
skill: demo-skill
title: 데모 스킬 eval suite
entries:
  - id: case-group
    type: happy-path
    path: case-group/case.yaml
"""


def _write_flat_case_group(skill: Path) -> None:
    flat_dir = skill / "evals" / "case-group"
    flat_dir.mkdir(parents=True)
    (flat_dir / "input.json").write_text('{"request":"make skill"}\n', encoding="utf-8")
    (flat_dir / "expected.json").write_text('{"ok": true}\n', encoding="utf-8")
    (flat_dir / "case.yaml").write_text(FLAT_CASE_GROUP_YAML, encoding="utf-8")


def _write_entries_manifest(skill: Path) -> None:
    (skill / "evals" / "demo-skill.eval.yaml").write_text(ENTRIES_MANIFEST_YAML, encoding="utf-8")


def _assert_flattened_case_group(test: unittest.TestCase, spec: dict, skill: Path) -> None:
    test.assertEqual(validate_spec(spec, skill), [])
    cases = load_cases(spec, skill)
    test.assertEqual([case["id"] for case in cases], ["alpha 실행", "beta 실행"])
    test.assertTrue(all(case["__artifact_slug"].startswith(("01-", "02-")) for case in cases))
    test.assertEqual(run_suite(spec, skill)["failed"], 0)


class EvalEntriesFlattenMigrationTest(EvalRunnerTestBase):
    """eval.yaml entries[]와 flatten evals/<case-id>/case.yaml migration behavior를 검증하기 위해 분리한 class다."""

    def test_entries_manifest_and_flatten_case_group_expand_cases(self) -> None:
        """eval.yaml entries[]와 evals/<case-id>/case.yaml의 cases[] 실행 단위 확장을 검증한다."""
        skill = _make_skill(self.tmp)
        legacy_dir = skill / "evals" / "cases" / "case-1"
        _write_flat_case_group(skill)
        _write_entries_manifest(skill)
        self.assertTrue(legacy_dir.exists())  # legacy undeclared directory is ignored.
        _assert_flattened_case_group(self, parse_spec(_spec_path(skill)), skill)


    def test_new_cases_shape_requires_assertion_id(self) -> None:
        """새 cases[] shape에서 assertion.id 누락을 validation error로 잡는지 검증한다."""
        skill = _make_skill(self.tmp)
        flat_dir = skill / "evals" / "case-group"
        flat_dir.mkdir(parents=True)
        (flat_dir / "input.json").write_text('{"request":"make skill"}\n', encoding="utf-8")
        (flat_dir / "case.yaml").write_text(
            """id: case-group
type: happy-path
cases:
  - id: alpha
    input: input.json
    run:
      command: {python} scripts/run_pipeline.py --input {input} --output {output}
    assertions:
      - title: 출력이 JSON인지 검증
        type: command
        cmd: {python} -m json.tool {output}
""",
            encoding="utf-8",
        )
        (skill / "evals" / "demo-skill.eval.yaml").write_text(
            """version: 1
skill: demo-skill
title: 데모 스킬 eval suite
entries:
  - id: case-group
    type: happy-path
    path: case-group/case.yaml
""",
            encoding="utf-8",
        )
        errors = validate_spec(parse_spec(_spec_path(skill)), skill)
        self.assertTrue(any("missing 'id'" in e for e in errors))



class EvalCliFlagIoTest(EvalRunnerTestBase):
    """CLI flag별 exit code, stdout/stderr routing, JSON shape를 검증한다."""

    def test_main_validate_and_run_exit_codes(self) -> None:
        """CLI main의 --validate, 기본 실행, 깨진 skill directory exit code를 검증한다."""
        skill = _make_skill(self.tmp)
        validate_code, validate_stdout, validate_stderr = _capture_main([str(skill), "--validate"])
        run_code, run_stdout, run_stderr = _capture_main([str(skill)])
        broken = self.tmp / "empty"
        broken.mkdir()
        broken_code, broken_stdout, broken_stderr = _capture_main([str(broken)])
        _assert_cli_result(self, (validate_code, validate_stdout, validate_stderr), code=0, stdout_token="VALID")
        _assert_cli_result(self, (run_code, run_stdout, run_stderr), code=0, stdout_token="summary:")
        _assert_cli_result(
            self,
            (broken_code, broken_stdout, broken_stderr),
            code=2,
            stderr_token="no evals/*.eval.yaml",
        )

    def test_validate_human_output_shape(self) -> None:
        """--validate는 human-readable VALID line을 stdout에 쓰고 stderr를 비워둔다."""
        skill = _make_skill(self.tmp)
        code, stdout, stderr = _capture_main([str(skill), "--validate"])
        self.assertEqual(code, 0)
        self.assertIn("VALID demo-skill.eval.yaml", stdout)
        self.assertEqual(stderr, "")

    def test_validate_json_output_shape(self) -> None:
        """--validate --json은 valid/errors machine-readable shape를 유지한다."""
        skill = _make_skill(self.tmp)
        code, stdout, stderr = _capture_main([str(skill), "--validate", "--json"])
        payload = json.loads(stdout)
        self.assertEqual(code, 0)
        self.assertEqual(payload, {"valid": True, "errors": []})
        self.assertEqual(stderr, "")

    def test_malformed_validate_json_output_shape(self) -> None:
        """malformed suite의 --validate --json은 parse 가능한 failure shape를 stdout에 쓴다."""
        skill = _make_skill(self.tmp)
        _spec_path(skill).write_text("version: 1\nskill: demo-skill\ntitle: bad\nentries:\n", encoding="utf-8")
        code, stdout, stderr = _capture_main([str(skill), "--validate", "--json"])
        payload = json.loads(stdout)
        self.assertEqual(code, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(payload["errors"])
        self.assertEqual(stderr, "")

    def test_run_json_output_shape(self) -> None:
        """기본 실행 --json은 summary와 case/check 배열을 JSON으로 출력한다."""
        skill = _make_skill(self.tmp)
        code, stdout, stderr = _capture_main([str(skill), "--json"])
        payload = json.loads(stdout)
        self.assertEqual(code, 0)
        self.assertEqual(payload["passed"], 1)
        self.assertEqual(payload["failed"], 0)
        self.assertTrue(payload["cases"])
        self.assertTrue(payload["cases"][0]["checks"])
        self.assertEqual(stderr, "")

    def test_promote_human_output_stays_in_temp_fixture(self) -> None:
        """--promote CLI write는 temp fixture 안 expected.json 생성과 promoted line으로 제한한다."""
        skill = _make_skill(self.tmp, include_expected=False)
        expected = skill / "evals" / "cases" / "case-1" / "expected.json"
        code, stdout, stderr = _capture_main([str(skill), "--promote"])
        self.assertEqual(code, 0)
        self.assertTrue(expected.exists())
        self.assertIn(f"promoted: {expected.resolve()}", stdout)
        self.assertEqual(stderr, "")

    def test_promote_json_output_shape_and_read_back(self) -> None:
        """--promote --json은 promoted path와 생성 파일 content를 함께 검증 가능하게 출력한다."""
        skill = _make_skill(self.tmp, include_expected=False)
        code, stdout, stderr = _capture_main([str(skill), "--promote", "--json"])
        payload = json.loads(stdout)
        promoted = Path(payload["cases"][0]["promoted"])
        self.assertEqual(code, 0)
        self.assertTrue(promoted.exists())
        self.assertEqual(promoted.read_text(encoding="utf-8"), '{"ok": true}\n')
        self.assertEqual(stderr, "")

    def test_missing_suite_json_error_shape(self) -> None:
        """missing eval suite의 --json error는 stderr에 parse 가능한 error object로 출력된다."""
        broken = self.tmp / "empty"
        broken.mkdir()
        code, stdout, stderr = _capture_main([str(broken), "--json"])
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("error", json.loads(stderr))


if __name__ == "__main__":
    unittest.main()
