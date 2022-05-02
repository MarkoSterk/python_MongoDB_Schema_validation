from flask import abort, jsonify, Response
from datetime import datetime
import secrets
from copy import deepcopy

class Model:
    collection = 'db'
    session = object()
    __ModelName__ = 'Model'

    Schema = {}

    ##list of all available methods on the collection object

    def __init__(self, modelData, validate=True, onLoad=False):
        ##deleted all protected fields before continuing
        for key in self.Schema:
            if 'protected' in self.Schema[key]:
                if self.Schema[key]['protected'] and key in modelData.keys():
                    del modelData[key]

        if validate: Model.validate(self, self.Schema, modelData, onLoad=onLoad)
        for key in modelData: ##loads data into model
            if key in self.Schema: ##ignores data that is not in the Schema
                setattr(self, key, modelData[key]) ##sets attributes
        
        if onLoad:
            setattr(self, '_id', modelData['_id'])
            setattr(self, '_createdAt', modelData['_createdAt'])
        if '_id' not in modelData.keys(): setattr(self, '_id', secrets.token_hex(16))
        if '_createdAt' not in modelData.keys(): setattr(self, '_createdAt', datetime.utcnow().strftime('%d-%m-%Y %H:%M'))


    def __repr__(self):
        return f'{self.collection}(_id: {self._id}, _createdAt: {self._createdAt})'


    def insertDefaults(Schema, modelData):
        for key in Schema:
            if(('default' in Schema[key])
                and (key not in modelData)):
                if callable(Schema[key]['default']):
                    modelData[key] = Schema[key]['default']()
                else:
                    modelData[key] = Schema[key]['default']
        return modelData
    

    def checkRequired(Schema, modelData, validationErrors):
        for key in Schema:
            if 'required' in Schema[key]:
                if((Schema[key]['required']==True) and (key not in modelData)):
                    #Model.ModelError('Validation error', f'{key} is a required field', 400)
                    validationErrors.append({key: ['required', f'required field']})
        return validationErrors
    

    def checkTypes(Schema, modelData, validationErrors):
        for key in Schema:
            if key in modelData:
                if isinstance(Schema[key]['type'], tuple):
                    errorStr = [checkEl.__name__ for checkEl in Schema[key]['type']]
                    setType = Schema[key]['type'][-1]
                else:
                    errorStr = Schema[key]['type'].__name__
                    setType = Schema[key]['type']
                ##tries to force type conversion
                if isinstance(modelData[key], Schema[key]['type']) == False: 
                    try:
                        modelData[key] = setType(modelData[key])
                    except:
                        ##if conversion fails it return an error
                        #Model.ModelError('Validation error', f'{key} must be of type {errorStr}', 400)
                        validationErrors.append({key: ['type', f'Must be of type {errorStr}']})
        return modelData, validationErrors


    def checkUnique(self, Schema, modelData, validationErrors):
        for key in Schema:
            if 'unique' in Schema[key]:
                if Schema[key]['unique']:
                    if self.session[self.collection].find_one({key: modelData[key]}):
                        #Model.ModelError('Validation error', f'{key} is already present in the database', 400)
                        validationErrors.append({key: ['unique field', 'Already present in database']})
        return validationErrors


    def checkValidators(Schema, modelData, validationErrors):
        for key in Schema:
            if 'validators' in Schema[key]:
                for validator in Schema[key]['validators']:
                    if key in modelData: ##SKIP: if data is not present and is also not required and has no default 
                        if not validator[0](key, modelData, validator[1]):
                            validationErrors.append({key: [validator[0].__name__, validator[1]]})
        return validationErrors


    def validate(self, Schema, modelData, onLoad):
        validationErrors=[]

        modelData = Model.insertDefaults(Schema, modelData)
        validationErrors=Model.checkRequired(Schema, modelData, validationErrors)
        modelData, validationErrors=Model.checkTypes(Schema, modelData, validationErrors)
        if onLoad==False: ##not loaded from DB 
            validationErrors=Model.checkUnique(self, Schema, modelData, validationErrors)
        validationErrors=Model.checkValidators(Schema, modelData, validationErrors)
        
        if len(validationErrors)>0: 
            return Model.ModelError('Validation error', validationErrors, 400)
        return True
    

    @staticmethod
    def updateAttributes(updateObject, Schema, data):
        for operation in data:
            for key in data[operation]:
                if key in Schema:
                    if operation=='$set': setattr(updateObject, key, data[operation][key])
                    if operation=='$unset': delattr(updateObject, key)
        return updateObject

    ############################################################################################
    ##################################instance methods##########################################
    #############################################################################################
    def save(self, pre_hooks=None):
        if self.session[self.collection].find_one({'_id': self._id})==None:
            
            if pre_hooks is None:
                pre_hooks=[]
            
            for func in pre_hooks:
                self = func()

            self.session[self.collection].insert_one(vars(self))
        else:
            return Model.ModelError('This object already exists. Please use update, to change object.', 400)
    

    def delete(self):
        return self.session[self.collection].delete_one({'_id': self._id})
    

    def update(self, data, onLoad=True, pre_hooks=None):
        newSelf = deepcopy(self)
        newSelf = Model.updateAttributes(newSelf, newSelf.Schema, data)
        if newSelf.validate(newSelf.Schema, vars(newSelf), onLoad=onLoad):
            self = Model.updateAttributes(self, self.Schema, data)

            if pre_hooks is None:
                pre_hooks=[]
            for func in pre_hooks:
                self = func()
            
            self.session[self.collection].replace_one({'_id': self._id}, vars(self))
    
    def populate(self, populateData=None):
        try:
            data = populateData['model'].findOne({'_id': getattr(self, populateData['field'])})

            for key in populateData['hideFields']:
                if key in vars(data):
                    delattr(data, key)
            
            setattr(self, populateData['field'], vars(data))
            return self
        except:
            return self


    ##########################################################################################
    ##################################Class methods############################################
    ##########################################################################################
    @classmethod
    def ModelError(cls, errorType, validationErrors, statusCode):
        response = {
        'status': errorType,
        'message': validationErrors,
        'code': statusCode
        }
        return abort(statusCode, response)

    @classmethod
    def filterData(cls, data):
        filteredData = {}
        for key in data:
            if key in cls.Schema:
                filteredData[key]=data[key]
        return filteredData

    @classmethod
    def findOne(cls, query, validate=True, onLoad=True):
        query = cls.session[cls.collection].find_one(query)
        if query:
            return cls(query, validate=validate, onLoad=onLoad)
        return None
    
    @classmethod
    def findMany(cls, query, validate=True, onLoad=True):
        query = cls.session[cls.collection].find(query)
        if query:
            return [cls(q, validate=validate, onLoad=onLoad) for q in query]
        return None
    

    
        



