from app import mongo
from xmlrpc.client import Boolean
from .validator import Validator
from .model import Model
import secrets
from slugify import slugify
from datetime import datetime


class Post(Model):
    session=mongo.db
    collection = 'post'
    __ModelName__ = 'Post'

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
                (Validator.allowedListElements, ['Blog', 'Science', 'News', 'Media'])
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
            'type': str,
            'required': False
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
        #super().__init__(user)
        Model.__init__(self, data, validate=validate, onLoad=onLoad)
    
    def slugify(self):
        self.slug = secrets.token_hex(1) + '-' + slugify(getattr(self, 'title'))
        return self