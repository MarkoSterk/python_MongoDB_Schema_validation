from validate_email import validate_email

'''
Validator class holda staticmethods for Schema field validation
Each method requires: 
fieldname <-- the key of the field in the Schema
data <-- the entire Schema data which is validated
argument <-- argument (value, list etc...) against which the Schema data is validated

examples:

Validator.isEmail('email', data, check=None):
    validates the 'email' field in the data (type: dict) if it is a valid email address
    It uses the validate-email module
    Third argument (check=None) is not required

Validator.checkElementsType('category', data, checkType):
    checks if elements in a list are of type 'checkType'
    returns True if all fields are of desired type(s)

Validator.minValue('rating', data, minValue):
    checks if the value of field 'rating' is larger or equal than minValue


Custom validators can be simply created by adhering to the 'design' 
of static methods in the Validator class
'''

class Validator:

    @staticmethod
    def isEmail(fieldname, modelData, check=None):
        is_valid = bool(validate_email(modelData[fieldname]))
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