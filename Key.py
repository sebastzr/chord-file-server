import hashlib

class Key(object):

    def __init__(self, value):
        self.value = value
        self.idlength = 256
        
    def __repr__(self):
        return self.value[:9]
        
    def __init__(self, value):
        self.value = value
        self.idlength = 256

    def __repr__(self):   ### retorna el valor de la llave
        return self.value[:9]

    def __gt__(self, value):  ###   greater than  / mayor que key o str
        if isinstance(value, str):
            return self.value > value
        elif isinstance(value,  Key):
            return  self.value > value.value
        else:
            raise TypeError("__gt__ solo soporta str o Key como valor")

    def __ge__(self, value): ###   greater or equal  / mayor o igual key o str
        if isinstance(value, str):
            return self.value >= value
        elif isinstance(value,  Key):
            return  self.value >= value.value
        else:
            raise TypeError("__gt__  solo soporta str o Key como valor")

    def __lt__(self, value): ###   lower than  / menor que key o str
        if isinstance(value, str):
            return self.value < value
        elif isinstance(value,  Key):
            return  self.value < value.value
        else:
            raise TypeError("__lt__  solo soporta str o Key como valor")

    def __le__(self, value):###   lower or equal  / menor o igual key o str
        if isinstance(value, str):
            return self.value >= value
        elif isinstance(value,  Key):
            return  self.value >= value.value
        else:
            raise TypeError("__gt__  solo soporta str o Key como valor")

    def __eq__(self, value):###    equal  /  igual key o str
        if isinstance(value, str):
            return self.value == value
        elif isinstance(value,  Key):
            return  self.value == value.value
        else:
            raise TypeError("__eq__  solo soporta str o Key como valor")

    def __ne__(self, value): ### non equal  /  no igual key o str
        if isinstance(value, str):
            return self.value != value
        elif isinstance(value,  Key):
            return  self.value != value.value
        else:
            raise TypeError("__ne__  solo soporta str o Key como valor")
    
     
