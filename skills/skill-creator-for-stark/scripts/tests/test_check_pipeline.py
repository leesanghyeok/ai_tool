"""scripts.check_pipeline, 즉 생성 skill pipeline verifier용 테스트다."""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from check_pipeline import check, main  # noqa: E402

STEP = "def main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n"
BAD_PIPELINE = "import sys\nif '--help' in sys.argv:\n    raise SystemExit(3)\n"


def _skill(tmp: Path, files: dict[str, str], requirements: str | None = None) -> Path:
    """skill directory를 만든다. `files`는 skill 아래 상대 경로를 text에 mapping한다."""
    skill = tmp / "demo-skill"
    for rel, text in files.items():
        p = skill / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if requirements is not None:
        (skill / "requirements.txt").write_text(requirements, encoding="utf-8")
    skill.mkdir(parents=True, exist_ok=True)
    return skill


class CompileCheckTest(unittest.TestCase):
    """script compile/syntax validation 경계를 검증하기 위해 분리한 class다."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_clean_script_passes(self) -> None:
        """문법 문제가 없는 단일 script는 error 없이 통과하는지 검증한다."""
        skill = _skill(self.tmp, {"scripts/main.py": "import json\nprint(json.dumps({}))\n"})
        result = check(skill)
        self.assertEqual(result["errors"], [])

    def test_syntax_error_is_an_error(self) -> None:
        """Python syntax error가 compile failure error와 exit code 1로 잡히는지 검증한다."""
        skill = _skill(self.tmp, {"scripts/broken.py": "def main(:\n    pass\n"})
        result = check(skill)
        self.assertTrue(any("does not compile" in e for e in result["errors"]))
        self.assertEqual(main([str(skill)]), 1)


class DependencyCheckTest(unittest.TestCase):
    """stdlib/local/third-party dependency detection 경계를 검증하기 위해 분리한 class다."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_third_party_without_requirements_is_error(self) -> None:
        """third-party import가 있는데 requirements.txt가 없으면 dependency error로 잡는지 검증한다."""
        skill = _skill(self.tmp, {"scripts/fetch.py": "import requests\n"})
        result = check(skill)
        self.assertTrue(any("third-party import" in e and "requirements.txt" in e for e in result["errors"]))

    def test_third_party_with_requirements_ok(self) -> None:
        """requirements.txt에 선언된 third-party import는 허용되는지 검증한다."""
        skill = _skill(
            self.tmp,
            {"scripts/fetch.py": "import requests\n"},
            requirements="requests>=2.0\n",
        )
        self.assertEqual(check(skill)["errors"], [])

    def test_stdlib_only_needs_no_requirements(self) -> None:
        """stdlib import만 쓰는 script에는 requirements.txt를 요구하지 않는지 검증한다."""
        skill = _skill(self.tmp, {"scripts/main.py": "import json, os, re\nfrom pathlib import Path\n"})
        self.assertEqual(check(skill)["errors"], [])

    def test_local_sibling_import_not_flagged(self) -> None:
        """scripts/ 내부 local sibling import를 third-party import로 오탐하지 않는지 검증한다."""
        skill = _skill(
            self.tmp,
            {
                "scripts/main.py": "from helpers import go\n",
                "scripts/helpers.py": "def go():\n    pass\n",
            },
        )
        self.assertEqual(check(skill)["errors"], [])


class EntrypointWarningTest(unittest.TestCase):
    """multi-step script와 run_pipeline.py entrypoint warning 경계를 검증하기 위해 분리한 class다."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_two_steps_without_orchestrator_warns(self) -> None:
        """여러 step script가 있는데 run_pipeline.py orchestrator가 없으면 warning만 내는지 검증한다."""
        skill = _skill(self.tmp, {"scripts/fetch.py": STEP, "scripts/parse.py": STEP})
        result = check(skill)
        self.assertEqual(result["errors"], [])
        self.assertTrue(any("orchestrator" in w or "sequence" in w for w in result["warnings"]))
        self.assertEqual(main([str(skill)]), 0)  # warning이며 error는 아니다

    def test_two_steps_with_orchestrator_no_warning(self) -> None:
        """여러 step script와 run_pipeline.py가 함께 있으면 orchestrator warning을 내지 않는지 검증한다."""
        skill = _skill(
            self.tmp,
            {
                "scripts/fetch.py": STEP,
                "scripts/parse.py": STEP,
                "scripts/run_pipeline.py": STEP,
            },
        )
        self.assertEqual(check(skill)["warnings"], [])

    def test_run_pipeline_smoke_failure_is_error(self) -> None:
        """run_pipeline.py가 기본 --help smoke 실행에 실패하면 package verifier error로 잡는다."""
        skill = _skill(self.tmp, {"scripts/run_pipeline.py": BAD_PIPELINE})
        result = check(skill)
        self.assertTrue(any("smoke --help failed" in e for e in result["errors"]))

    def test_single_step_no_warning(self) -> None:
        """단일 step script만 있는 경우 orchestrator warning을 내지 않는지 검증한다."""
        skill = _skill(self.tmp, {"scripts/main.py": STEP})
        self.assertEqual(check(skill)["warnings"], [])


class MainExitTest(unittest.TestCase):
    """CLI main exit code behavior를 검증하기 위해 분리한 class다."""

    def test_missing_dir_exits_two(self) -> None:
        """존재하지 않는 skill directory 입력은 CLI exit code 2로 처리되는지 검증한다."""
        self.assertEqual(main(["/no/such/skill/dir/xyz"]), 2)


if __name__ == "__main__":
    unittest.main()
