import copy
import json
from datetime import datetime

from bson import ObjectId
from bson.decimal128 import Decimal128


class DataMapper:

    @staticmethod
    def df_to_xlsx(dataframe, file_path, include_headers=True):
        """
        Create an Excel workbook from a Pandas DataFrame.

        Parameters:
            dataframe (pd.DataFrame): The Pandas DataFrame to be saved to Excel.
            file_path (str): The file path where the Excel workbook will be saved.

        Returns:
            None
        """
        success = True
        try:
            # Create a Pandas Excel writer using the file path
            dataframe.to_excel(file_path, index=False, header=include_headers)


        except Exception as e:
            success = False

        return success

    # Example usage:
    # Assuming you have a DataFrame named 'df' and want to save it to 'output.xlsx'
    # create_excel_from_dataframe(df, 'output.xlsx')

    @staticmethod
    def transform_document(example_document, mapper):
        new_document = {}
        for key in example_document.keys():

            if key in mapper.keys() and '_transform' in mapper[key].keys():
                value = mapper[key]["_transform"](example_document[key])
            else:
                value = example_document[key]

            map_key = key if "_to" not in mapper.keys() else mapper[key]["_to"]
            if isinstance(value, dict) and key in mapper.keys():
                sub = {} if "_sub" not in mapper[key].keys() else mapper[key]["_sub"]
                new_document[mapper[key]["_to"]] = DataMapper.transform_document(copy.deepcopy(value), sub)

                if "_push" in mapper[key].keys():
                    item = copy.deepcopy(new_document[mapper[key]["_to"]])
                    item["_name"] = mapper[key]["_to"]
                    if mapper[key]["_push"] in new_document:
                        new_document[mapper[key]["_push"]].append(item)

                    else:
                        new_document[mapper[key]["_push"]] = [item]

                    del new_document[mapper[key]["_to"]]
            elif key not in mapper.keys():

                new_document[key] = copy.deepcopy(value)
            else:
                new_document[map_key] = copy.deepcopy(value)

        return new_document

    @staticmethod
    def to_dict(doc):

        def _parse_dict(obj):


            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, Decimal128):
                        obj[key] = float(str(value))
                    elif isinstance(value, dict) or isinstance(value, list):
                        _parse_dict(value)
                    elif isinstance(value, datetime):
                        obj[key] = value.isoformat()
                    elif isinstance(value, ObjectId):
                        obj[key] = str(value)

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, dict) or isinstance(item, list):
                        _parse_dict(item)
                    elif isinstance(item, datetime):
                        obj[i] = item.isoformat()
                    elif isinstance(item, ObjectId):
                        obj[i] = str(item)


            return obj

        try:
            doc = _parse_dict(doc)
        except Exception as e:
            print(e)

        if not isinstance(doc,list):
            if "_id" in doc.keys():
                doc["id"] = doc["_id"]
                del doc["_id"]

        return doc

    @staticmethod
    def json(obj):
        return json.dumps(DataMapper.to_dict(obj))

    @staticmethod
    def from_json(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict) or isinstance(value, list):
                    DataMapper.from_json(value)
                elif isinstance(value, str):
                    try:
                        obj[key] = datetime.fromisoformat(value)
                    except ValueError:
                        pass
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, dict) or isinstance(item, list):
                    DataMapper.from_json(item)
                elif isinstance(item, str):
                    try:
                        obj[i] = datetime.fromisoformat(item)
                    except ValueError:
                        pass

        return obj
