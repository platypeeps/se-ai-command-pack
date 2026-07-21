from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = ROOT / "package.json"
REVIEW_FULL_CHECK = ROOT / "scripts" / "sd-ai-command-pack-review-full-check.sh"


class ProjectCheckConfigurationTest(unittest.TestCase):
    def test_package_json_owns_dependency_free_full_check_wrapper(self) -> None:
        payload = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))

        self.assertIs(payload.get("private"), True)
        self.assertEqual(
            payload.get("scripts"),
            {
                "check": "make check",
                "check:full": (
                    "npm run check && "
                    "bash scripts/sd-ai-command-pack-full-check.sh"
                ),
            },
        )
        for field in (
            "dependencies",
            "devDependencies",
            "optionalDependencies",
            "peerDependencies",
        ):
            self.assertNotIn(field, payload)
        for lock_name in (
            "package-lock.json",
            "npm-shrinkwrap.json",
            "pnpm-lock.yaml",
            "yarn.lock",
        ):
            self.assertFalse((ROOT / lock_name).exists(), lock_name)

    def test_review_selector_runs_configured_wrapper_with_reviews_disabled(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runner = Path(temp_dir) / "package-runner"
            runner.write_text(
                "#!/usr/bin/env bash\n"
                "printf 'args=%s\\n' \"$*\"\n"
                "printf 'prism=%s\\n' \"$SD_AI_COMMAND_PACK_FULL_CHECK_PRISM\"\n"
                "printf 'gito=%s\\n' \"$SD_AI_COMMAND_PACK_FULL_CHECK_GITO\"\n",
                encoding="utf-8",
            )
            runner.chmod(0o755)
            env = os.environ.copy()
            env["SD_AI_COMMAND_PACK_FULL_CHECK_PACKAGE_RUNNER"] = str(runner)

            result = subprocess.run(
                ["bash", str(REVIEW_FULL_CHECK)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("args=run check:full", result.stdout)
        self.assertIn("prism=0", result.stdout)
        self.assertIn("gito=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
