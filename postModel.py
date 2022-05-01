from slugify import slugify
from xmlrpc.client import Boolean
from .validator import Validator
from .model import Model
import secrets


class Post(Model):
    '''
    needs initialized Flask-PyMongo instance for session attribute
    e.g.
    mongo = PyMongo()

    session = mongo.db

    collection = name of db collection e.g. 'posts'
    __ModelName__ = name of model e.g. 'Post'
    '''
    session='mongo.db'
    collection = 'posts'
    __ModelName__ = 'Post'


    '''
    The Schema is set as a dictionary with keys corresponding to desired field names.
    Each field is a dictionary with fields:

    type: the type of variable (str, int, float, list etc): e.g. type: str
    The type field can be a tuple with multiple allowed types e.g. type: (int, float)
    In case of multiple types the last element in the tuple will be enforced during validaton.
    Example: variable with allowed types of int and float will be forced into float type during validation if 
    in a different variable type like str: '1.2' ---forced--> float('1.2')

    validators: is a list of tuples containing validator methods from the Validator class (validator.py).
    First element of tuple is the validator method, second element is the dsired parameter.
    examples:

    Field 'title' must be at least 5 characters long:
    validators: [
        (Validator.minLength, 5)
    ]

    Field 'category' can contain only str type elements and the elements can only be 'Blog' or 'Science'
    validators: [
        (Validator.checkElementsType, str),
        (Validator.allowedListElements, ['Blog', 'Science'])
    ]

    required: boolean, sets if field is required (True/False). If required and missing an error if raised.
    If field is required and a default option is available, the field is populated with the default value

    default: default value of field if field value is not provided.

    unique: boolena. If a field (like id or email address) must be unique (primary key)
    '''



    Schema = {
        'title': {
            'type': str,
            'validators': [
                (Validator.minLength, 5)
            ],
            'required': True
        },
        'category': {
            'type': list,
            'validators': [
                (Validator.checkElementsType, (str)),
                (Validator.allowedListElements, ['Blog', "Science"])
            ],
            'required': True,
            'default': ['Blog']
        },
        'text': {
            'type': str,
            'validators': [
                (Validator.minLength, 10)
            ],
            'required': True
        },
        'coverImage': {
            'type': list,
            'required': False,
            'validators': [
                (Validator.checkElementsType, str)
            ]
        },
        'slug': {
            'type': str,
            'required': False
        },
        'active': {
            'type': Boolean,
            'required': True,
            'default': True
        },
        'authorName': {
            'type': str,
            'required': True
        },
        'author': {
            'type': str,
            'required': True
        },
        'dateEdited': {
            'type': str,
            'required': False
        }
    }
    
    def __init__(self, data, validate=True, onLoad=False):
        '''
        Initialized the parent with provided parameters (data)
        with optional parameters validate=True (validates the Schema) and 
        onLoad=False. If onLoad=True, the unique property is not tested (during loading from db for example)
        '''
        Model.__init__(self, data, validate=validate, onLoad=onLoad)
    

    ###added instance method for use as a pre_hook during saving
    def slugify(self):
        '''
        creates a unique slug for the post instance by combining a random 1 bit (2 chars) hex token 
        and the slugified post title.
        '''
        self.slug = secrets.token_hex(1) + '-' + slugify(getattr(self, 'title'))
        return self
        