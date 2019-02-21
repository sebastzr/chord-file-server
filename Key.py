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
    
     def canonicalize(self, value):
        '''
        Retorna el valor hexadecimal con el numero correcto de caracteres
        se encarga de retirar '0x' y 'L'
        '''
        return format(value, '0>{}x'.format(self.idlength/4))
        
     def __add__(self, value):
        if isinstance(value, int) or isinstance(value, long):
            return self.sumint(value)
        elif isinstance(value, str):
            return self.sumhex(value)
        elif isinstance(value, Key):
            return self.sumhex(value.value)
        else:
            #self.log.error("Sum with unknow type")
            print type(value)
            raise TypeError
    
    def sumint(self, value):
        '''
        Retorna suma uid + value en representacion hexadecimal
        @param value: int para sumar  con valor uid 
        '''
        res = (int(self.value, 16) + value) % pow(2, self.idlength)  
        return self.canonicalize(res)

    def sumhex(self, value):
		'''
        Retorna suma uid + value en representacion hexadecimal
        @param  str repr del numero hexadecimal
        '''
        res = (int(self.value, 16) + int(value, 16)) % pow(2, self.idlength)
        return self.canonicalize(res)   
        
    def __sub__(self, value):
        if isinstance(value, int):
            return self.subint(value)
        elif isinstance(value, str):
            return self.subhex(value)
        elif isinstance(value, Key):
            return self.subhex(value.value)
        else:
            #self.log.error("Sub with unknow type")
            raise TypeError
    
    def subint(self, value):
        '''
        Retorna resta uid + value en representacion hexadecimal
        @param value: int para restar con valor uid 
        '''
        
        res = (int(self.value, 16) - value) % pow(2, self.idlength)
        return self.canonicalize(res)

    def subhex(self, value):
        '''
        Retorna resta uid + value en representacion hexadecimal
        @param  str repr del numero hexadecimal
        '''
        res = (int(self.value, 16) - int(value, 16)) % pow(2, self.idlength)
        return self.canonicalize(res)

     
	def __len__(self):
        return len(self.value)
        
     def isbetween(self, limit1, limit2):
        '''
        Retrona verdadero si el valor esta contenido entre limites [limit1,  limit2]
        Raise exception si limit1 == limit2
        '''
        if len(self.value) != len(limit1) != len(limit2):
            #self.log.error("Unable to compare.")
            raise Exception
        if self.value == limit1 or self.value == limit2:
            return True

        if limit1 > limit2:
            if self.value > limit1 or self.value < limit2:
                return True
            else:
                return False
        elif limit1 < limit2:
            if self.value > limit1 and self.value < limit2:
                return True
            else:
                return False
        else:
            # limit1 == limit2
            raise Exception
        
class Uid(Key):
    
    def __init__(self, strtohash):
        hash = hashlib.sha256(strtohash)
        Key.__init__(self, hash.hexdigest())    
