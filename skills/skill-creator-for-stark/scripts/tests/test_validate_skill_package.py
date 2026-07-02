"""validate-skill-package.py package completeness regression 테스트다."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent
VALIDATOR = SCRIPTS_DIR / "validate-skill-package.py"


class PackageCompletenessTest(unittest.TestCase):
    """generated package 필수 artifact 누락을 validator가 실패로 처리하는지 검증한다."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_missing_skill_md_is_package_completeness_error(self) -> None:
        """SKILL.md 없는 generated package fixture는 validator exit code 1과 path error를 반환한다."""
        skill = self.tmp / "incomplete-skill"
        (skill / "references").mkdir(parents=True)

        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(skill)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("SKILL.md not found", proc.stderr)


if __name__ == "__main__":
    unittest.main()
