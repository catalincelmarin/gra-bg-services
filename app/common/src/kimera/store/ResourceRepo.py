from typing import TypeVar, Type

from bson import ObjectId
from fastapi import HTTPException, status
from mongoengine.errors import DoesNotExist, NotUniqueError
from passlib.hash import bcrypt

from kimera.store.BaseRepo import BaseRepo

# Define a type variable for the schema
T = TypeVar("T")


class ResourceRepo(BaseRepo):
    def __init__(self, schema_cls: Type[T], model_cls):
        super().__init__(connection_name=model_cls._meta["db_alias"])
        self.collection = self.use(model_cls._meta["collection"])
        self.schema_cls = schema_cls
        self.model_cls = model_cls

    def create(self, obj_data):
        # Serialize the input data using the schema

        obj = self.schema_cls(**obj_data)

        # Encrypt the password if needed
        if hasattr(obj, "password"):
            obj.password = bcrypt.hash(obj.password)

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
        return str(new_obj.id)

    def all(self):
        objects = self.model_cls.objects.all()
        # Retrieve all documents from the collection
        return [{"id":str(obj.id),**self.schema_cls(**obj.to_mongo()).model_dump()} for obj in objects]

    def update(self, id: str, obj_data):

        try:
            obj = self.model_cls.objects.get(id=ObjectId(id))

        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object does not exist")

        # Update the document with the new data
        for key, value in obj_data.items():

            if key == "password":
                value = bcrypt.hash(obj_data["password"])

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

        return self.schema_cls(**obj.to_mongo()).model_dump()

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
        return self.schema_cls(**obj.to_mongo()).model_dump()

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
        return obj

    def find(self,**kwargs):
        objects = self.model_cls.objects(**kwargs)
        # Retrieve all documents from the collection
        return [{"id":str(obj.id), **self.schema_cls(**obj.to_mongo()).model_dump()} for obj in objects]

