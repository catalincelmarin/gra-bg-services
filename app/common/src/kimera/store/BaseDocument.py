from mongoengine import Document

from mongoengine.fields import ListField, ReferenceField
from bson import ObjectId

class BaseDocument(Document):
    meta = {'abstract': True}
    __private__ = []
    __expand__ = []  # optionally declare which refs to expand

    def to_dict(self):
        data = self.to_mongo().to_dict()
        data['id'] = str(data.pop('_id'))

        for k, v in data.items():
            if k in self.__private__:
                continue

            # Convert ObjectId to str
            if isinstance(getattr(self.__class__, k, None), ReferenceField):
                ref_obj = getattr(self, k)
                if k in self.__expand__ and ref_obj:
                    data[k] = ref_obj.to_dict() if hasattr(ref_obj, 'to_dict') else str(ref_obj)
                else:
                    if ref_obj is not None:
                        data[k] = str(ref_obj.id) if not isinstance(ref_obj,ObjectId) else str(ref_obj)
                    else:
                        data[k] = None

            # Expand list of references
            elif isinstance(getattr(self.__class__, k, None), ListField):
                field = getattr(self.__class__, k)
                if isinstance(field.field, ReferenceField):
                    ref_list = getattr(self, k)
                    if k in self.__expand__:
                        data[k] = [
                            r.to_dict() if hasattr(r, 'to_dict') else str(r.id)
                            for r in ref_list
                        ]
                    else:
                        data[k] = [str(r.id) for r in ref_list]

        return data
