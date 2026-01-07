from typing import TypeVar, Type

from bson import ObjectId
from fastapi import HTTPException, status
from mongoengine.errors import DoesNotExist, NotUniqueError
from passlib.hash import bcrypt

from kimera.store.BaseRepo import BaseRepo

# Define a type variable for the schema
T = TypeVar("T")


class AutoRepo(BaseRepo):
    def __init__(self, schema_cls: Type[T], model_cls):
        super().__init__(connection_name=model_cls._meta["db_alias"])
        self.collection = self.use(model_cls._meta["collection"])
        self.schema_cls = schema_cls
        self.model_cls = model_cls

    def create(self, obj_data):
        # Serialize the input data using the schema

        obj = self.schema_cls(**obj_data)

        # Create a new document
        new_obj = self.model_cls(**obj.model_dump())

        # Save the new document to the database
        try:
            new_obj.save()
        except NotUniqueError as err:
            error_details = {
                "error": "NotUniqueError",
                "message": str(err)
            }
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_details)

        # Return the created object's ID
        return new_obj.to_dict()

    def all(self):
        objects = self.model_cls.objects.all()
        # Retrieve all documents from the collection

        return [obj.to_dict() for obj in objects]

    def update(self, id: str, obj_data):

        try:
            obj = self.model_cls.objects.get(id=ObjectId(id))

        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object does not exist")

        new_values = self.schema_cls(**obj_data).model_dump(exclude_unset=True)

        for key, value in new_values.items():
            setattr(obj, key, value)

        # Save the updated document
        try:
            obj.save()
        except NotUniqueError as err:
            error_details = {
                "error": "NotUniqueError",
                "message": str(err)
            }
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_details)

        # Return the updated object

        return obj.to_dict()

    def delete(self, id: str):
        try:
            obj = self.model_cls.objects.get(id=ObjectId(id))
        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object does not exist")

        # Delete the document
        obj.delete()

        # Return True to indicate successful deletion
        return True

    def one(self, id: str):
        try:
            obj = self.model_cls.objects.get(id=ObjectId(id))
        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object does not exist")

        # Serialize the retrieved document using the schema
        return obj.to_dict()

    def findOne(self, **kwargs):
        try:
            obj = self.model_cls.objects.get(**kwargs)

        except DoesNotExist:
            return None

        # Serialize the retrieved document using the schema
        return {"id":str(obj.id), **self.schema_cls(**obj.to_mongo()).model_dump()}

    def getOne(self, **kwargs):
        try:
            obj = self.model_cls.objects.get(**kwargs)

        except DoesNotExist:
            return None

        # Serialize the retrieved document using the schema
        return obj.to_dict()

    def find(self,**kwargs):
        objects = self.model_cls.objects(**kwargs)
        # Retrieve all documents from the collection
        return [obj.to_dict() for obj in objects]

