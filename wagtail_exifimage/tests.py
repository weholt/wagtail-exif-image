from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

from .models import MetadataDefaultValue, MetadataTransformationValue
from .services import MetadataTransformationService


class MetadataTransformationValueTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username="user1",
            first_name="user1",
            last_name="user1",
            email="user1@example.com",
        )
        self.user2 = User.objects.create(
            username="user2",
            first_name="user2",
            last_name="user2",
            email="user2@example.com",
        )

    def test_1(self):
        """Testing metadata transformation values"""
        MetadataTransformationValue.objects.create(
            user=self.user1,
            source_field="make",
            keywords="fuji, fujifilm, fuj",
            target_value="Fujiking",
        )

        self.assertEqual(
            len(MetadataTransformationService(self.user1).get_transformation_values()),
            1,
        )
        self.assertEqual(
            len(MetadataTransformationService(self.user2).get_transformation_values()),
            0,
        )

    def test_2(self):
        """Testing metadata transformation values"""
        MetadataTransformationValue.objects.create(
            user=self.user1,
            source_field="make",
            keywords="fuji, fujifilm, fuj",
            target_value="Fujiking",
        )

        metadata = {"make": "Fuji"}
        transformed_metadata = MetadataTransformationService(
            self.user1
        ).remap_metadata_to_model_fields(metadata=metadata)
        self.assertEqual(transformed_metadata["make"], "Fujiking")

    def test_3(self):
        """Testing metadata transformation values"""
        MetadataTransformationValue.objects.create(
            user=self.user1,
            source_field="location",
            keywords="home",
            target_value="Some place",
        )
        MetadataTransformationValue.objects.create(
            user=self.user1,
            source_field="location",
            keywords="home",
            target_value="Some street",
            target_field="street",
        )

        MetadataTransformationValue.objects.create(
            user=self.user1,
            source_field="location",
            keywords="home",
            target_value="Some city",
            target_field="city",
        )

        MetadataTransformationValue.objects.create(
            user=self.user1,
            source_field="model",
            keywords="A73",
            target_value="Some sony camera",
            target_field="model",
        )

        metadata = {"location": "home", "make": "Fujifilm"}
        transformed_metadata = MetadataTransformationService(
            self.user1
        ).remap_metadata_to_model_fields(metadata=metadata)

        self.assertEqual(transformed_metadata["location"], "Some place")
        self.assertEqual(transformed_metadata["street"], "Some street")
        self.assertEqual(transformed_metadata["city"], "Some city")

    def test_4(self):
        MetadataDefaultValue.objects.create(
            user=self.user1,
            make="Fujifilm",
            model="XT-5",
            target_field="Creator",
            target_value="Thomas Weholt",
        )
        metadata = {"location": "home", "make": "Fujifilm"}
        transformed_metadata = MetadataTransformationService(
            self.user1
        ).get_default_metadata(metadata)
        self.assertFalse(transformed_metadata.get("creator"))

        metadata["model"] = "XT-5"
        transformed_metadata = MetadataTransformationService(
            self.user1
        ).get_default_metadata(metadata)
        print(transformed_metadata)
        self.assertEqual(transformed_metadata.get("creator"), "Thomas Weholt")
