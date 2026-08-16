from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = ROOT / "package.json"


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
                    "bash ~/.agents/bin/sd-ai-command-pack-full-check.sh"
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

    # The companion test that executed the pack's own
    # review-full-check wrapper is gone with the thin conversion: the wrapper is
    # not in this repository any more, and a CI runner has no machine install to
    # run it from. What the wrapper does is the pack's contract to test; what
    # this repository configures is the package.json above.


if __name__ == "__main__":
    unittest.main()
