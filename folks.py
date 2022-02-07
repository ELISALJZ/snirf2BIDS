"""
Writing up this quick script because there was SO much to learn about Python just
in Andy's snippet we discussed today that I figured it'd be worth it to show it all to you

This design that should let you do what you want to do, giving you total
control over a dynamic named list of named stuff via the . interface
"""


"""
First, we give you data whatever attributes it needs by defining some classses

Organize error checking and access into classes like you had with your String_field.

Think of each type of guy like a data type you might see like string or number or array,
with different error checking and get/set functions as you see fit.

In this silly example, all the data are strings, but we parse the strings to
prevent our user from making mistakes when modifying a Folks instance...
"""


class Guy:
    
    def __init__(self, val):
        
        self._value = val  # The value of the guy

    @property
    def value(self):
        # The simplest possible getter. You could add error checking or view logic here
        return self._value

    @value.setter
    def value(self, val):
        # The simplest possible setter
        # You could do error checking right here if you wanted to, but in this
        # example it is the responsibility of the Folks class
        self._value = val


class LameGuy(Guy):  # A derivative of Guy. I used a base class for no real reason here
    
    def __init__(self, val):
        super().__init__(val)
    
    @staticmethod
    def error_check(val):
        # I use a static method to define my error checking. You mentioned doing that,
        # but read my comments to see where else you could do error checking
        # You could expose an error checking function for a type like this
        return 'cool' not in val and type(val) is str
    

class CoolGuy(Guy):  # Another type. For your app, instead of LameGuy/CoolGuy, consider 'String' or 'NumericList' as derivatives of a 'Field'
    
    def __init__(self, val):
        super().__init__(val)
    
    @staticmethod
    def error_check(val):
        return 'cool' in val and type(val) is str


class Folks(object):
    """
    Our Folks class wraps collection of things we want to manage
    
    This is like your NIRSCoordinateSystem class
    """
    
    def __init__(self):
        
        # Init with some known values. Use our classes defined above to specify what they are
        self._fields = {
            'chrsthur': CoolGuy('a cool string'),
            'ljz24': CoolGuy('a cool string'),
            'jchoi00': LameGuy('a lame string'),
            'andyzjc': CoolGuy('a cool string')
            }
        
    # Overload __setattr__ and __getattr__ to give our users the . interface
    
    def __setattr__(self, name, val):
        
        if name.startswith('_'):  # Need to exclude internal attributes from this treatment or else we can't even add _fields in the constructor

            super(Folks, self).__setattr__(name, val)  # Fall back to the original __setattr__ behavior
            
        elif name in self._fields.keys():  # If writing to a field
            
            if self._fields[name].error_check(val):
                
                self._fields[name].value = val  # Set new value or raise an error if its invalid
                
            else:
                
                # Note there is no good reason to outsource the error checking from the Guy classes
                # Unless you want some control flow out here
                raise ValueError(name + ' might not be the right type of guy for value ' + str(val))
                
        elif name not in self._fields.keys():  # It's a new guy...
            
            # Do some logic to figure out the type of the new thing and add it to our collection
            # Realistically, you would want to use the value of the new thing, not it's name, but...
            
            if 'sstucker' in name or 'dboas' in name:
                
                if CoolGuy.error_check(val):  # Use our static method to validate a guy of this type before creating it
                    
                    self._fields[name] = CoolGuy(val)
                    
                else:
                    
                    raise ValueError('invalid guy')
                
            else:
                
                if LameGuy.error_check(val):
                    
                    self._fields[name] = LameGuy(val)
                    
                else:
                    
                    raise ValueError('invalid guy')

    def __getattr__(self, name):
        
        if name in self._fields.keys():
            
            return self._fields[name].value  # Use the property of the Guy in our managed collection

        else:
            
            return super(Folks, self).__getattribute__(name)  # Fall back to the original __setattr__ behavior
    
    def write_to_text(self, dst):  # Some utility function on our data :)
        
        with open(dst, 'w') as f:
        
            for key in self._fields.keys():
                
                f.write(key + ': ' + str(self._fields[key].value) + '\n')
                
    def people(self):
        return list(self._fields.keys())
            
        
if __name__ == '__main__':
    
    folks = Folks()
    folks.jchoi00 = 'he is alright i guess'  # Change a field's value
    folks.dboas = 'a string fit for a cool boss'  # Create a new field

    print(folks.dboas)
    
    more_folks = Folks()  # new instance doesn't have the changes, because we aren't dealing with attributes!
    
    print('new:', folks.jchoi00)
    print('old:', more_folks.jchoi00)

    print(folks.andyzjc)
    
    folks.andyzjc = 'this will raise a ValueError because it doesnt have the c word in it'

    
    # Play around with it and raise some errors!
    
    
    
    
    