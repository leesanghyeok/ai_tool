"""case-based scripts.run_evals_template runner의 검증 의도를 설명하는 단위 테스트다."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from run_evals_template import (  # noqa: E402
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


PIPELINE_OK = (
    "import argparse, pathlib\n"
    "ap = argparse.ArgumentParser()\n"
    "ap.add_argument('--input'); ap.add_argument('--output', required=True)\n"
    "a = ap.parse_args()\n"
    "pathlib.Path(a.output).write_text('{\"ok\": true}\\n')\n"
)
PIPELINE_WRONG = (
    "import argparse, pathlib\n"
    "ap = argparse.ArgumentParser()\n"
    "ap.add_argument('--input'); ap.add_argument('--output', required=True)\n"
    "a = ap.parse_args()\n"
    "pathlib.Path(a.output).write_text('{\"ok\": false}\\n')\n"
)
PIPELINE_PROVENANCE = (
    "import argparse, json, pathlib\n"
    "ap = argparse.ArgumentParser()\n"
    "ap.add_argument('--input'); ap.add_argument('--output', required=True)\n"
    "a = ap.parse_args()\n"
    "out=pathlib.Path(a.output)\n"
    "artifact=out.parent/'generated.md'\n"
    "artifact.write_text('generated evidence\\n', encoding='utf-8')\n"
    "out.write_text(json.dumps({'schema_version':1,'status':'success','files_written':[{'path':str(artifact),'action':'create'}],'errors':[]}, ensure_ascii=False)+'\\n', encoding='utf-8')\n"
)
JUDGE_PASS = (
    "import argparse, json, pathlib, sys\n"
    "argv=sys.argv[1:]\n"
    "mode=argv.pop(0) if argv and argv[0] in {'output','assertion'} else 'legacy'\n"
    "ap = argparse.ArgumentParser()\n"
    "ap.add_argument('--input', required=True); ap.add_argument('--output', required=True)\n"
    "a = ap.parse_args(argv)\n"
    "p=json.load(open(a.input))\n"
    "assert p['schema_version'] == 1\n"
    "if mode == 'output':\n"
    "    content='primary: '+p['prompt'][:40]\n"
    "    pathlib.Path(a.output).write_text(json.dumps({'schema_version':1,'status':'success','output':{'format':'text','content':content,'summary':content},'artifacts':[],'redactions_applied':[],'errors':[]}, ensure_ascii=False))\n"
    "elif mode == 'assertion':\n"
    "    results=[{'assertion_id': x['id'], 'status':'pass', 'judge_output':'ok', 'session_id':'test'} for x in p['assertions']]\n"
    "    pathlib.Path(a.output).write_text(json.dumps({'schema_version':1,'status':'success','method':p['method'],'primary_output_ref':{'sha256':'x'},'results':results,'errors':[]}, ensure_ascii=False))\n"
    "else:\n"
    "    pathlib.Path(a.output).write_text('상태: pass\\n판단: ' + p['prompt'][:20])\n"
)
JUDGE_FAIL = (
    "import argparse, pathlib, sys\n"
    "argv=sys.argv[1:]\n"
    "if argv and argv[0] in {'output','assertion'}: argv.pop(0)\n"
    "ap = argparse.ArgumentParser()\n"
    "ap.add_argument('--input', required=True); ap.add_argument('--output', required=True)\n"
    "a = ap.parse_args(argv)\n"
    "pathlib.Path(a.output).write_text('')\n"
)


def _make_skill(tmp: Path, *, pipeline: str = PIPELINE_OK, judge: str = JUDGE_PASS,
                include_expected: bool = True, case_type: str = "happy-path",
                undeclared: bool = False, llm_setup: bool = False) -> Path:
    skill = tmp / "demo-skill"
    scripts = skill / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "run_pipeline.py").write_text(pipeline, encoding="utf-8")
    (scripts / "run_llm_judge.py").write_text(judge, encoding="utf-8")

    case_dir = skill / "evals" / "cases" / "case-1"
    case_dir.mkdir(parents=True)
    input_text = '{"schema_version":1,"prompt":"make skill"}\n' if case_type == "llm-judge" else '{"request":"make skill"}\n'
    (case_dir / "input.json").write_text(input_text, encoding="utf-8")
    if include_expected:
        (case_dir / "expected.json").write_text('{"ok": true}\n', encoding="utf-8")

    if case_type == "llm-judge":
        run_block = ""
        input_line = "input: input.json\n"
        expected_line = ""
    else:
        expected_line = "expected: expected.json\n" if include_expected else ""
        run_block = (
            "run:\n"
            "  command: {python} scripts/run_pipeline.py --input {input} --output {output}\n"
            "  timeout_sec: 30\n"
        )
        input_line = "input: input.json\n"

    if case_type == "llm-judge":
        setup_block = "" if not llm_setup else """setup:
  command: {python} scripts/run_pipeline.py --input {input} --output {pipeline_output}
  timeout_sec: 30
"""
        assertions = f"""{setup_block}judge:
  method: each-session
  command: {{python}} scripts/run_llm_judge.py assertion --input {{assertion_input}} --output {{judge_output}}
  timeout_sec: 30
assertions:
  - id: semantic-quality
    title: 의미 품질 검증
    type: llm-judge
    prompt: 출력이 실행 가능한 절차를 포함한다.
"""
    else:
        assertions = """assertions:
  - id: valid-json
    title: 출력이 JSON인지 검증
    type: command
    cmd: {python} -m json.tool {output}
"""

    (case_dir / "case.yaml").write_text(
        f"""id: case-1
type: {case_type}
title: 기본 케이스
{input_line}{expected_line}{run_block}{assertions}""",
        encoding="utf-8",
    )
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
    if undeclared:
        extra = skill / "evals" / "cases" / "extra"
        extra.mkdir(parents=True)
        (extra / "case.yaml").write_text("id: extra\ntype: happy-path\ntitle: 미선언\n", encoding="utf-8")
    return skill


class EvalRunnerTestBase(unittest.TestCase):
    """run_evals_template runner 테스트가 공유하는 임시 skill fixture lifecycle을 제공한다."""
    """각 테스트 호출 전"""
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    """각 테스트 호출 후"""
    def tearDown(self) -> None:
        self._tmp.cleanup()



class EvalManifestDiscoveryTest(EvalRunnerTestBase):
    """manifest/spec validation과 case discovery 계약을 검증하기 위해 분리한 class다."""

    def test_validate_well_formed_case_suite(self) -> None:
        """정상적인 eval suite가 validation error 없이 로드되는지 검증한다."""
        skill = _make_skill(self.tmp)
        spec = parse_spec(_spec_path(skill))
        self.assertEqual(validate_spec(spec, skill), [])
        self.assertEqual(len(load_cases(spec, skill)), 1)


    def test_eval_yaml_is_source_of_truth_for_cases(self) -> None:
        """manifest에 선언된 case만 실행 대상이 되고, 디렉터리에 남은 미선언 case는 무시되는지 검증한다."""
        skill = _make_skill(self.tmp, undeclared=True)
        spec = parse_spec(_spec_path(skill))
        self.assertEqual(validate_spec(spec, skill), [])
        self.assertEqual([case["id"] for case in load_cases(spec, skill)], ["case-1"])


    def test_declared_missing_case_file_is_validation_error(self) -> None:
        """manifest가 선언한 case.yaml 파일이 없으면 validation error로 잡는지 검증한다."""
        skill = _make_skill(self.tmp)
        (skill / "evals" / "cases" / "case-1" / "case.yaml").unlink()
        spec = parse_spec(_spec_path(skill))
        self.assertTrue(any("case file not found" in e for e in validate_spec(spec, skill)))


    def test_eval_yaml_description_is_rejected(self) -> None:
        """eval manifest top-level description 필드를 금지하는 계약을 검증한다."""
        skill = _make_skill(self.tmp)
        spec_path = _spec_path(skill)
        spec_path.write_text(spec_path.read_text() + "description: no\n", encoding="utf-8")
        spec = parse_spec(spec_path)
        self.assertTrue(any("description" in e for e in validate_spec(spec, skill)))



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



class EvalEntriesFlattenMigrationTest(EvalRunnerTestBase):
    """entries[] manifest와 flatten evals/<case-id>/case.yaml migration behavior를 검증하기 위해 분리한 class다."""

    def test_entries_manifest_and_flatten_case_group_expand_cases(self) -> None:
        """entries[] manifest와 evals/<case-id>/case.yaml의 cases[] 실행 단위 확장을 검증한다."""
        skill = _make_skill(self.tmp)
        legacy_dir = skill / "evals" / "cases" / "case-1"
        flat_dir = skill / "evals" / "case-group"
        flat_dir.mkdir(parents=True)
        (flat_dir / "input.json").write_text('{"request":"make skill"}\n', encoding="utf-8")
        (flat_dir / "expected.json").write_text('{"ok": true}\n', encoding="utf-8")
        (flat_dir / "case.yaml").write_text(
            """id: case-group
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
        self.assertTrue(legacy_dir.exists())  # legacy undeclared directory is ignored.
        spec = parse_spec(_spec_path(skill))
        self.assertEqual(validate_spec(spec, skill), [])
        cases = load_cases(spec, skill)
        self.assertEqual([case["id"] for case in cases], ["alpha 실행", "beta 실행"])
        self.assertTrue(all(case["__artifact_slug"].startswith(("01-", "02-")) for case in cases))
        result = run_suite(spec, skill)
        self.assertEqual(result["failed"], 0)


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



class EvalCliExitBehaviorTest(EvalRunnerTestBase):
    """CLI main의 validate/run/not-found exit behavior를 검증하기 위해 분리한 class다."""

    def test_main_validate_and_run_exit_codes(self) -> None:
        """CLI main의 --validate, 기본 실행, 깨진 skill directory exit code를 검증한다."""
        skill = _make_skill(self.tmp)
        self.assertEqual(main([str(skill), "--validate"]), 0)
        self.assertEqual(main([str(skill)]), 0)
        broken = self.tmp / "empty"
        broken.mkdir()
        self.assertEqual(main([str(broken)]), 2)


if __name__ == "__main__":
    unittest.main()
