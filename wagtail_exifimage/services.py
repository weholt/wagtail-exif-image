from dataclasses import dataclass
from typing import Dict, List

from django.contrib.auth import get_user_model
from wagtail.models import Collection

from .models import (
    MetadataDefaultValue,
    MetadataTransformationSetup,
    MetadataTransformationValue,
)

User = get_user_model()


@dataclass
class TransformationValue:
    source_field: str
    keywords: List[str]
    target_value: str
    target_field: str


class MetadataTransformationService:
    """
    A service for metadata transformation.
    """

    def __init__(self, user: User):
        self.user = user
        self.setups = MetadataTransformationSetup.objects.filter(user=self.user)

    def setup_for_image(
        self, camera_make: str, camera_model: str
    ) -> MetadataTransformationSetup:
        if not camera_make or not camera_model:
            return

        for setup in self.setups:
            if (
                setup.camera_make.lower() == camera_make.lower()
                and setup.camera_model.lower() == camera_model.lower()
            ):
                return setup

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass

    def get_transformation_values(
        self,
    ) -> Dict[str, List[TransformationValue]]:
        result = {}
        for row in MetadataTransformationValue.objects.filter(user=self.user):
            keywords = [s.strip() for s in row.keywords.split(",")]
            result.setdefault(row.source_field, []).append(
                TransformationValue(
                    source_field=row.source_field,
                    keywords=keywords,
                    target_value=row.target_value,
                    target_field=row.target_field or row.source_field,
                )
            )
        return result

    def transform_metadata(self, metadata: Dict[str, str]) -> Dict[str, str]:
        """
        Will transform metadata in the form of a key-value dictionary for a given user,
        based on values stored in the database. The provided metadata is not changed.
        """
        result = {}
        result.update(metadata)

        transformation_values = self.get_transformation_values()
        for t_field, t_values in transformation_values.items():
            for transformation in t_values:
                for field in metadata.keys():
                    if field == t_field:
                        transformated_value = None
                        target_field = None
                        if metadata[field].lower() in transformation.keywords:
                            transformated_value = transformation.target_value
                            target_field = transformation.target_field
                        result[target_field or field] = (
                            transformated_value or metadata[field]
                        )

        return result

    def get_default_metadata(self, metadata):
        """
        Will add default metadata if make and model matches keys in provided metadata.
        """
        result = {}
        result.update(metadata)
        camera_make = metadata.get("camera_make")
        camera_model = metadata.get("camera_model")
        if not camera_make or not camera_model:
            return result

        default_values = MetadataDefaultValue.objects.filter(
            user=self.user,
            camera_make=camera_make.lower(),
            camera_model=camera_model.lower(),
        )

        if not default_values:
            return result

        for default_value in default_values:
            if default_value.target_field not in result:
                result[default_value.target_field] = default_value.target_value

        return result

    def assign_missing_fields(self, image):
        setup = self.setup_for_image(image.camera_make, image.camera_model)
        if (
            setup
            and setup.copy_caption_abstract_headline_to_title_if_missing
            and not image.title
        ):
            image.title = image.caption or image.headline

    def clean_up_keywords(
        self, keywords, characters_to_remove, keywords_to_ignore
    ) -> List[str]:
        result = []
        for keyword in keywords:
            keyword = keyword.lower().strip()
            for character in characters_to_remove:
                keyword = keyword.replace(character, "")

            if keyword in [s.lower().strip() for s in keywords_to_ignore.split(",")]:
                continue
            result.append(keyword.capitalize())
        return result

    def assign_tags(self, image, keywords):
        """
        This will add tags to an image based on the IPTC keywords field.
        """
        setup = self.setup_for_image(image.camera_make, image.camera_model)
        tags = keywords
        tags += [
            s.strip().capitalize() for s in image.category.split(setup.category_divider)
        ]

        if image.software:
            tags.append(image.software)

        if setup:
            if setup.convert_camera_make_to_tag and image.camera_make:
                tags.append(image.camera_make)
            if setup.convert_camera_model_to_tag and image.camera_model:
                tags.append(image.camera_model)
            if setup.convert_lens_make_to_tag and image.lens_make:
                tags.append(image.lens_make)
            if setup.convert_lens_model_to_tag and image.lens_model:
                tags.append(image.lens_model)

        for tag in tags:
            image.tags.add(tag)

    def assign_collection(self, image, collections: List[str] = []):
        """
        This will assign an image to a collection based on either the supploed collection-list
        or based on the IPTC category field if the transformation setup has this turned on.
        """
        if not collections and image.category:
            setup = self.setup_for_image(image.camera_make, image.camera_model)
            if setup and setup.convert_categories_to_collections:
                collections = [
                    s.strip() for s in image.category.split(setup.category_divider)
                ]

        if collections:
            root_coll = Collection.get_first_root_node()
            for collection in collections:
                children = [c for c in root_coll.get_children()]
                if collection not in [c.name for c in children]:
                    root_coll = root_coll.add_child(name=collection)
                else:
                    root_coll = [c for c in children if c.name == collection][0]

            image.collection = root_coll

    def process_image(self, image, default_metadata: dict[str, str]):
        setup = self.setup_for_image(
            default_metadata.get("camera_make"), default_metadata.get("camera_model")
        )
        metadata = self.transform_metadata(default_metadata)
        keywords = (
            setup
            and self.clean_up_keywords(
                metadata["keywords"].split(", "),
                setup.characters_to_trim_from_keywords,
                setup.keywords_to_ignore,
            )
            or metadata["keywords"].split(", ")
        )

        for attr, value in metadata.items():
            setattr(image, attr, value)

        image.keywords = ", ".join(keywords)

        self.assign_tags(image, keywords)
        self.assign_collection(image, default_metadata.get("collections", []))
        self.assign_missing_fields(image)
        image.has_processed_metadata = True
        image.save()
        return image
