import unittest

from services.ai_assistant import respond_to_voice_command
from styler_app.analysis import generate_outfit_recommendations


class VoiceAssistantTests(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "favourite_colours": ["Navy", "Olive green"],
            "colours_disliked": [],
            "common_occasions": ["Work"],
            "preferred_aesthetic": "Minimal luxury",
            "seasonal_family": "Autumn",
        }
        self.wardrobe = [
            {"id": "top-1", "name": "Olive shirt", "category": "TOP WEAR", "main_colour": "#7A8D5A"},
            {"id": "top-2", "name": "Navy tee", "category": "TOP WEAR", "main_colour": "#1F2A44"},
            {"id": "bottom-1", "name": "Cream trousers", "category": "BOTTOM WEAR", "main_colour": "#F7F1E7"},
            {"id": "bottom-2", "name": "Black jeans", "category": "BOTTOM WEAR", "main_colour": "#000000"},
        ]

    def test_recommendations_only_use_available_wardrobe_items(self):
        recommendations = generate_outfit_recommendations(self.profile, self.wardrobe)
        self.assertEqual(len(recommendations), 4)
        self.assertEqual(
            {(item["top"], item["bottom"]) for item in recommendations},
            {
                ("Olive shirt", "Cream trousers"),
                ("Olive shirt", "Black jeans"),
                ("Navy tee", "Cream trousers"),
                ("Navy tee", "Black jeans"),
            },
        )

    def test_unavailable_items_are_excluded(self):
        wardrobe = self.wardrobe + [
            {"id": "top-3", "name": "Laundry shirt", "category": "TOP WEAR", "available": False}
        ]
        recommendations = generate_outfit_recommendations(self.profile, wardrobe)
        self.assertTrue(all(item["top"] != "Laundry shirt" for item in recommendations))

    def test_another_request_does_not_repeat_a_combination(self):
        first_response, first, used, occasion = respond_to_voice_command(
            "What should I wear for college?", self.profile, self.wardrobe, [], None
        )
        self.assertIn(first["top"], first_response)
        second_response, second, _, second_occasion = respond_to_voice_command(
            "Hey STYLER, another one", self.profile, self.wardrobe, used, first, occasion
        )
        self.assertNotEqual(
            (first["top_id"], first["bottom_id"]),
            (second["top_id"], second["bottom_id"]),
        )
        self.assertIn("saved wardrobe", second_response)
        self.assertEqual(second_occasion, "College")

    def test_no_outfit_is_invented_when_wardrobe_is_incomplete(self):
        response, outfit, _, _ = respond_to_voice_command(
            "What should I wear today?",
            self.profile,
            [self.wardrobe[0]],
            [],
            None,
        )
        self.assertIsNone(outfit)
        self.assertIn("available wardrobe", response)


if __name__ == "__main__":
    unittest.main()
