import datetime
import copy
import re
import types
import db_client



class Document:
    def __init__(self, *args, **kwargs):
        self.fields = kwargs
        self.type = args[0] if args else None

    def __getitem__(self, item):
        return self.fields[item]

    def __setitem__(self, key, value):
        self.fields[key]=value

    def has_key(self, key):
        if key in self.fields:
            return True
        return False

    def save(self, safe_input=True, in_collection=None, output=False):
        # in collection is a list with dbname and collection name
        if safe_input:
            self.check_data()

        if output or in_collection:

            complete_dict = self.get_as_dict()

            if in_collection:
                db_client.get_collection(*in_collection).insert_one(complete_dict)

            if output:
                return complete_dict

    def get_as_dict(self):
        def get_dict_entry(value):
            if isinstance(value, Document):
                return value.get_as_dict()
            if isinstance(value, list):
                return [ get_dict_entry(in_list) for in_list in value ]
            return value

        complete_dict = {}
        for key,value in self.fields.items():
            complete_dict[key] = get_dict_entry(value)

        return complete_dict

    def check_data(self):
        if not self.type:
            raise ModelError('Unspecified Type')

        checked = copy.copy(self.fields)
        remaining = None
        for key, value in expected_fields[self.type].items():
            if key == '__remaining':
                remaining=value

            try:
                field = checked.pop(key)
            except KeyError:
                raise ModelError('Mandatory field {} missing from document of type {}'.format(key,self.type))

            self.check_one_field(value,key,field)

        if checked:
            if not remaining:
                raise ModelError('Unexpected fields {} in document of type {}'.format(list(checked.keys()),self.type ))
            for k,v in checked.items():
                self.check_one_field(remaining,k,v)

    @staticmethod
    def check_one_field(expected_type, field_key, field_value):

        if isinstance(expected_type, str):
            is_list = re.search('list of (.*)', str(expected_type))
            if is_list:
                Document.__isinstance_raise(field_key,field_value,list)
                inside_list = is_list.group(1)
                for in_list in field_value:
                    Document.check_one_field(inside_list, 'elements in list {}'.format(field_key), in_list)
                return
            try:
                expected_type = eval(expected_type)
            except NameError:
                field_value.check_data()
                return

        Document.__isinstance_raise(field_key,field_value,expected_type)

    @staticmethod
    def __isinstance_raise(field, value, expected_type):
        if not isinstance(value, expected_type):
            raise ModelError('Field {} is not of correct type {}'.format(field, str(expected_type)))


class Collection:
    def __init__(self, name):
        self.name = name
        self.documents = []

    def append(self, *args):
        self.documents = self.documents + [*args]

    def save(self, safe_input=True, in_db=None, client=None, output=False):
        to_add = []
        for doc in self.documents:
            to_add.append(doc.save(safe_input=safe_input, in_collection=None, output=True))

        if in_db or client:
            if client:
                db_collection = client
            else:
                db_collection = db_client.get_collection(in_db, self.name)
            db_collection.insert_many(to_add)

        if output:
            return to_add


class ModelError(Exception):
    pass


expected_fields = {
    'competition': {
        'name': str,
        'year': int,
        'participants': 'list of str'
    },
    'match': {
        'team_A': str,
        'team_B': str,
        'home': str,
        'date': datetime.date,
        'result': 'result',
        'pronos': 'list of prono',
        'competition': str,
        'day': (str, int)
    },
    'prono': {
            'participant_name': str,
        'team_A_goals': (int,type(None)),
        'team_B_goals': (int, type(None))
    },
    'result': {
        'team_A_goals': int,
        'team_B_goals': int
    }

}



