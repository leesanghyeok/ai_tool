"""scripts.run_llm_judge output/assertion adapter 계약을 검증하는 단위 테스트다."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from run_llm_judge import main  # noqa: E402


class RunLlmJudgeTestBase(unittest.TestCase):
    """run_llm_judge adapter 테스트가 공유하는 임시 파일 helper를 제공한다."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_json(self, name: str, payload: object) -> Path:
        path = self.tmp / name
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


class RunLlmJudgeOutputModeTest(RunLlmJudgeTestBase):
    """output mode public schema와 primary output contract를 검증하기 위해 분리한 class다."""

    def test_output_mode_happy_path_writes_primary_output_contract(self) -> None:
        """output mode가 public input에서 primary output JSON 계약을 생성하는지 검증한다."""
        inp = self._write_json("input.json", {"schema_version": 1, "prompt": "새 스킬을 만들어줘"})
        out = self.tmp / "primary-output.json"

        self.assertEqual(main(["output", "--input", str(inp), "--output", str(out)]), 0)
        payload = self._read_json(out)

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["output"]["format"], "text")
        self.assertIn("새 스킬", payload["output"]["content"])
        self.assertIsInstance(payload["artifacts"], list)
        self.assertEqual(payload["redactions_applied"], [])
        self.assertEqual(payload["errors"], [])

    def test_output_mode_rejects_non_public_schema_fields(self) -> None:
        """output mode public schema가 schema_version과 prompt 외 필드를 거부하는지 검증한다."""
        inp = self._write_json("input.json", {"schema_version": 1, "prompt": "x", "case_id": "leak"})
        out = self.tmp / "primary-output.json"

        self.assertEqual(main(["output", "--input", str(inp), "--output", str(out)]), 1)
        payload = self._read_json(out)

        self.assertEqual(payload["status"], "failed")
        self.assertIn("allows only schema_version and prompt", payload["errors"][0])


class RunLlmJudgeAssertionModeTest(RunLlmJudgeTestBase):
    """assertion mode internal schema와 result contract를 검증하기 위해 분리한 class다."""

    def test_assertion_mode_aggregate_writes_results_and_primary_hash(self) -> None:
        """assertion aggregate mode가 결과 목록과 primary_output sha256 참조를 쓰는지 검증한다."""
        primary = "결과 본문"
        inp = self._write_json(
            "assertion-input.json",
            {
                "schema_version": 1,
                "method": "aggregate",
                "primary_output": primary,
                "assertions": [
                    {"id": "a1", "title": "A1", "prompt": "본문이 충분한가"},
                    {"id": "a2", "title": "A2", "prompt": "승인 경계를 지켰는가"},
                ],
            },
        )
        out = self.tmp / "assertion-output.json"

        self.assertEqual(main(["assertion", "--input", str(inp), "--output", str(out)]), 0)
        payload = self._read_json(out)

        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["method"], "aggregate")
        self.assertEqual(payload["primary_output_ref"]["sha256"], hashlib.sha256(primary.encode()).hexdigest())
        self.assertEqual([r["assertion_id"] for r in payload["results"]], ["a1", "a2"])
        self.assertEqual({r["session_id"] for r in payload["results"]}, {"aggregate"})
        self.assertTrue(all(r["status"] == "pass" for r in payload["results"]))

    def test_assertion_mode_each_session_uses_deterministic_independent_markers(self) -> None:
        """each-session mode가 assertion별 deterministic session marker를 부여하는지 검증한다."""
        inp = self._write_json(
            "assertion-input.json",
            {
                "schema_version": 1,
                "method": "each-session",
                "primary_output": "primary",
                "assertions": [
                    {"id": "first", "title": "First", "prompt": "첫 판단"},
                    {"id": "second", "title": "Second", "prompt": "둘째 판단"},
                ],
            },
        )
        out = self.tmp / "assertion-output.json"

        self.assertEqual(main(["assertion", "--input", str(inp), "--output", str(out)]), 0)
        payload = self._read_json(out)

        self.assertEqual(payload["method"], "each-session")
        self.assertEqual(
            [r["session_id"] for r in payload["results"]],
            ["each-session:1:first", "each-session:2:second"],
        )

    def test_assertion_mode_normalizes_subagent_alias(self) -> None:
        """legacy subagent method alias가 each-session으로 normalize되는지 검증한다."""
        inp = self._write_json(
            "assertion-input.json",
            {
                "schema_version": 1,
                "method": "subagent",
                "primary_output": "primary",
                "assertions": [{"id": "a", "title": "A", "prompt": "판단"}],
            },
        )
        out = self.tmp / "assertion-output.json"

        self.assertEqual(main(["assertion", "--input", str(inp), "--output", str(out)]), 0)
        payload = self._read_json(out)

        self.assertEqual(payload["method"], "each-session")
        self.assertEqual(payload["results"][0]["session_id"], "each-session:1:a")

    def test_assertion_mode_rejects_invalid_internal_schema(self) -> None:
        """assertion mode internal schema에서 필수 primary_output 누락을 실패로 처리하는지 검증한다."""
        inp = self._write_json(
            "assertion-input.json",
            {"schema_version": 1, "method": "aggregate", "assertions": []},
        )
        out = self.tmp / "assertion-output.json"

        self.assertEqual(main(["assertion", "--input", str(inp), "--output", str(out)]), 1)
        payload = self._read_json(out)

        self.assertEqual(payload["status"], "failed")
        self.assertTrue(payload["errors"])


class RunLlmJudgeLegacyAliasTest(RunLlmJudgeTestBase):
    """legacy --input/--output compatibility alias를 검증하기 위해 분리한 class다."""

    def test_legacy_input_output_alias_accepts_public_judge_packet_and_writes_text(self) -> None:
        """기존 --input/--output alias가 public judge packet을 받아 legacy text output을 쓰는지 검증한다."""
        inp = self._write_json("judge-packet.json", {"schema_version": 1, "prompt": "판단해줘"})
        out = self.tmp / "judge-output.txt"

        self.assertEqual(main(["--input", str(inp), "--output", str(out)]), 0)
        text = out.read_text(encoding="utf-8")

        self.assertIn("상태: pass", text)
        self.assertIn("legacy assertion alias", text)


if __name__ == "__main__":
    unittest.main()
