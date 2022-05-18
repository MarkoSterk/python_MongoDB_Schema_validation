from validate_email import validate_email
from flask import abort, jsonify

class Validator:

    @staticmethod
    def isEmail(fieldname, data, check):
        is_valid = bool(validate_email(data[fieldname]))
        return is_valid
    

    @staticmethod
    def checkElementsType(fieldname, modelData, checkType):
        if type(checkType) is tuple:
            errorStr = [checkEl.__name__ for checkEl in checkType]
            setType=checkType[-1]
        else:
            errorStr = checkType.__name__
            setType=checkType
        if hasattr(modelData[fieldname], '__getitem__'):
            for i, el in enumerate(modelData[fieldname]):
                if isinstance(el, checkType) == False:
                    try:
                        modelData[fieldname][i]=setType(modelData[fieldname][i])
                    except:
                        return False
            return True


    @staticmethod
    def allowedListElements(fieldname, modelData, allowedList):
        for elem in modelData[fieldname]:
            if elem not in allowedList:
                return False
        return True
    
    @staticmethod
    def inList(fieldname, modelData, allowedList):
        if modelData[fieldname] in allowedList:
            return True
        return False


    @staticmethod
    def minValue(fieldname, data, N):
        if data[fieldname]<N:
            return False
        return True
    

    @staticmethod
    def maxValue(fieldname, data, N):
        if data[fieldname]>N:
            return False
        return True


    @staticmethod
    def isLength(fieldname, data, N):
        if len(data[fieldname])!=N:
            return False
        return True


    @staticmethod
    def minLength(fieldname, data, N):
        if len(data[fieldname])<N:
            return False
        return True
    

    def maxLength(fieldname, data, N):
        if len(data[fieldname])>N:
            return False
        return True
    

    @staticmethod
    def mustMatch(fieldname, data, matchField):
        if data[fieldname]!=data[matchField]:
            return False
        return True