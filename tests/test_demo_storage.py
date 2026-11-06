import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from styler_app import storage
from styler_app.analysis import generate_outfit_recommendations


class DemoStorageTests(unittest.TestCase):
    def test_demo_mode_loads_sample_data_and_skips_disk_writes(self):
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
                profile = storage.load_profile()
                wardrobe = storage.load_wardrobe()
                self.assertTrue(profile["is_onboarded"])
                self.assertEqual(profile["name"], "Style Guest")
                self.assertGreaterEqual(len(wardrobe), 4)
                self.assertTrue(all(item.get("id", "").startswith("demo-") for item in wardrobe))
                recommendations = generate_outfit_recommendations(
                    profile,
                    wardrobe,
                    profile["default_occasion"],
                )
                self.assertTrue(recommendations)
                self.assertIn(recommendations[0]["top"], {item["name"] for item in wardrobe})
                self.assertIn(recommendations[0]["bottom"], {item["name"] for item in wardrobe})
                self.assertEqual(storage.load_outfits(), [])
                storage.save_profile({"name": "Demo user"})
                storage.save_wardrobe([{"name": "Demo shirt"}])
                storage.save_outfits([{"name": "Demo outfit"}])

            self.assertFalse(profile_path.exists())
            self.assertFalse(wardrobe_path.exists())
            self.assertFalse(outfits_path.exists())

    def test_demo_wardrobe_items_are_copied_between_sessions(self):
        with patch.dict(os.environ, {"STYLER_DEMO_MODE": "true"}):
            first_profile = storage.load_profile()
            first_profile["favourite_colours"].append("Changed locally")
            first_load = storage.load_wardrobe()
            first_load[0]["name"] = "Changed locally"
            second_profile = storage.load_profile()
            second_load = storage.load_wardrobe()

        self.assertNotIn("Changed locally", second_profile["favourite_colours"])
        self.assertNotEqual(second_load[0]["name"], "Changed locally")


if __name__ == "__main__":
    unittest.main()
