from typing import Type, TypeVar

from fastapi import HTTPException, status
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from kimera.store.BaseRepo import BaseRepo

# Define a type variable for the schema
T = TypeVar("T")


class ResourceRepo(BaseRepo):
    def __init__(self, schema_cls: Type[T], model_cls, db: Session):
        super().__init__()
        self.schema_cls = schema_cls
        self.model_cls = model_cls
        self.db = db
        self.dao = model_cls

    def create(self, obj_data):
        # Serialize the input data using the schema
        obj = self.schema_cls(**obj_data)

        # Encrypt the password if needed
        if hasattr(obj, "password"):
            obj.password = bcrypt.hash(obj.password)

        # Create a new model instance
        new_obj = self.model_cls(**obj.model_dump())

        # Add the new model instance to the session and commit
        try:
            self.db.add(new_obj)
            self.db.commit()
            self.db.refresh(new_obj)
        except Exception as err:
            error_details = {
                "error": "DatabaseError",
                "message": str(err)
            }
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_details)

        # Return the created object's ID
        return str(new_obj.id)

    def all(self):
        objects = self.db.query(self.model_cls).all()
        # Retrieve all objects from the table
        return [self.schema_cls.from_orm(obj).model_dump() for obj in objects]

    def update(self, id: int, obj_data):
        obj = self.db.query(self.model_cls).filter(self.model_cls.id == id).first()

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object does not exist")

        # Update the object with the new data
        for key, value in obj_data.items():
            if key == "password":
                value = bcrypt.hash(obj_data["password"])

            setattr(obj, key, value)

        # Commit the changes
        try:
            self.db.commit()
            self.db.refresh(obj)
        except Exception as err:
            error_details = {
                "error": "DatabaseError",
                "message": str(err)
            }
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_details)

        # Return the updated object
        return self.schema_cls.from_orm(obj).model_dump()

    def delete(self, id: int):
        obj = self.db.query(self.model_cls).filter(self.model_cls.id == id).first()

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object does not exist")

        # Delete the object from the database
        self.db.delete(obj)
        self.db.commit()

        # Return True to indicate successful deletion
        return True

    def one(self, id: int):
        obj = self.db.query(self.model_cls).filter(self.model_cls.id == id).first()

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object does not exist")

        # Serialize the retrieved object using the schema
        return self.schema_cls.from_orm(obj).model_dump()
