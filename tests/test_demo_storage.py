import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from styler_app import storage


class DemoStorageTests(unittest.TestCase):
    def test_demo_mode_uses_empty_session_defaults_and_skips_disk_writes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile_path = root / "profile.json"
            wardrobe_path = root / "wardrobe.json"
            outfits_path = root / "outfits.json"
            with (
                patch.dict(os.environ, {"STYLER_DEMO_MODE": "true"}),
                patch.object(storage, "PROFILE_PATH", profile_path),
                patch.object(storage, "WARDROBE_PATH", wardrobe_path),
                patch.object(storage, "OUTFITS_PATH", outfits_path),
            ):
                self.assertTrue(storage.is_demo_mode())
                self.assertFalse(storage.load_profile()["is_onboarded"])
                self.assertEqual(storage.load_wardrobe(), [])
                self.assertEqual(storage.load_outfits(), [])
                storage.save_profile({"name": "Demo user"})
                storage.save_wardrobe([{"name": "Demo shirt"}])
                storage.save_outfits([{"name": "Demo outfit"}])

            self.assertFalse(profile_path.exists())
            self.assertFalse(wardrobe_path.exists())
            self.assertFalse(outfits_path.exists())


if __name__ == "__main__":
    unittest.main()
