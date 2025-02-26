from database.db import db
from playhouse.postgres_ext import (
    Model,
    CharField,
    DateTimeField,
    UUIDField,
    BinaryJSONField,
    SQL,
    ArrayField,
    BooleanField,
    IntegerField,
    DateField,
    FloatField,
    TextField,
    ForeignKeyField,
)
from playhouse.shortcuts import ThreadSafeDatabaseMetadata
from datetime import datetime

from services.users.models.users import User
from enums.image_enums import ProcessState

class ProcessedImages(Model):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    request_id = UUIDField(unique=True, index=True)
    user_id = ForeignKeyField(User, backref="processed_images")
    input_image_urls = ArrayField(CharField)
    product_name = CharField(index=True)
    output_image_urls = ArrayField(CharField, null=True)
    status = CharField(default=ProcessState.PENDING.value)
    processed_count = IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(ProcessedImages, self).save(*args, **kwargs)

    class Meta:
        database = db
        only_save_dirty = True
        model_metadata_class = ThreadSafeDatabaseMetadata
        table_name = "processed_images"