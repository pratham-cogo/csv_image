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
    DateField,
    FloatField,
    TextField,
    ForeignKeyField,
)
from playhouse.shortcuts import ThreadSafeDatabaseMetadata
from datetime import datetime

class User(Model):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    username = CharField(index=True)
    password_hash = CharField()
    created_at = DateTimeField(index=True, default=datetime.now)
    updated_at = DateTimeField(index=True, default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(User, self).save(*args, **kwargs)

    class Meta:
        database = db
        only_save_dirty = True
        model_metadata_class = ThreadSafeDatabaseMetadata
        table_name = "users"