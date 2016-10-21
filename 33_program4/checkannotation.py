from goody import type_as_str
import inspect

class Check_All_OK:
    """
    Check_All_OK class implements __check_annotation__ by checking whether each
      annotation passed to its constructor is OK; the first one that
      fails (by raising AssertionError) prints its problem, with a list of all
      annotations being tried at the end of the check_history.
    """
       
    def __init__(self,*args):
        self._annotations = args
        
    def __repr__(self):
        return 'Check_All_OK('+','.join([str(i) for i in self._annotations])+')'

    def __check_annotation__(self, check, param, value,check_history):
        for annot in self._annotations:
            check(param, annot, value, check_history+'Check_All_OK check: '+str(annot)+' while trying: '+str(self)+'\n')


class Check_Any_OK:
    """
    Check_Any_OK implements __check_annotation__ by checking whether at least
      one of the annotations passed to its constructor is OK; if all fail 
      (by raising AssertionError) this classes raises AssertionError and prints
      its failure, along with a list of all annotations tried followed by the
      check_history.
    """
    
    def __init__(self,*args):
        self._annotations = args
        
    def __repr__(self):
        return 'Check_Any_OK('+','.join([str(i) for i in self._annotations])+')'

    def __check_annotation__(self, check, param, value, check_history):
        failed = 0
        for annot in self._annotations: 
            try:
                check(param, annot, value, check_history)
            except AssertionError:
                failed += 1
        if failed == len(self._annotations):
            assert False, repr(param)+' failed annotation check(Check_Any_OK): value = '+repr(value)+\
                         '\n  tried '+str(self)+'\n'+check_history                 



class Check_Annotation():
    # set name to True for checking to occur
    checking_on  = True
  
    # self._checking_on must also be true for checking to occur
    def __init__(self,f):
        self._f = f
        self.checking_on = True
        self.list_type = set()
        
    # Check whether param's annot is correct for value, adding to check_history
    #    if recurs; defines many local function which use it parameters.  
    def check(self,param,annot,value,check_history=''):
        
        
        # Define local functions for checking, list/tuple, dict, set/frozenset,
        #   lambda/functions, and str (str for extra credit)
        # Many of these local functions called by check, call check on their
        #   elements (thus are indirectly recursive)

        
        def check_list_tuple(ty):
            assert isinstance(value, ty), repr(param) +' failed annotation check(wrong type): value = ' + repr(value) + \
            '\n  was type ' + type_as_str(value) + ' ...should be type '+ str(ty) + '\n' + check_history
             
            if len(annot) == 1:
                for x in value:
                    self.check(param, annot[0], x, check_history + type_as_str(value) + '[' + str(value.index(x)) + '] check: ' + str(annot[0]) + '\n')
            else:
                assert len(annot) == len(value), repr(param) + ' failed annotation check(wrong number of elements): value = ' + repr(value) + \
                '\n annotation had ' + str(len(annot)) + ' elements' + str(annot) + '\n' + check_history
                 
                for x,y in zip(annot, value):
                    self.check(param, x, y, check_history + type_as_str(value) + '[' + str(value.index(y)) + '] check: ' + str(annot.index(x)) + '\n')
                
        def check_dict():
            assert isinstance(value, dict), repr(param) +' failed annotation check(wrong type): value = ' + repr(value) + \
            '\n  was type ' + type_as_str(value) + ' ...should be type dict\n' + check_history
            assert len(annot) == 1, repr(param) + ' annotation inconsistency: dict should have 1 item but had ' + str(len(annot)) + \
            '\n annotation = ' + str(annot)
            
            for x,y in value.items():
                self.check(param, list(annot.keys())[0], x, check_history + ' dict key check: ' + str(list(annot.keys())[0]) + '\n')
                self.check(param, list(annot.values())[0], y, check_history + ' dict value check: ' + str(list(annot.values())[0]) + '\n')
            
            
            

        # Decode the annotation here and check it 
        if annot is None:
            return
        elif type(annot) is type:
            assert isinstance(value, annot), repr(param) +' failed annotation check(wrong type): value = ' + repr(value) + \
            '\n  was type ' + type_as_str(value) +' ...should be type ' + str(annot)[8:-2] +'\n' + check_history 
        elif isinstance(annot, list):
            check_list_tuple(list)
        elif isinstance(annot, tuple):
            check_list_tuple(tuple)
        elif isinstance(annot, dict):
            check_dict()
        else:
            try:
                annot.__check_annotation__(self.check, param, value, check_history)

            except:
                assert
            else:
                
        
        
    # Return result of calling decorated function call, checking present
    #   parameter/return annotations if required
    def __call__(self, *args, **kargs):
        
        # Return a dictionary of the parameter/argument bindings (actually an
        #    ordereddict, in the order parameters occur in the function's header)
        def param_arg_bindings():
            f_signature  = inspect.signature(self._f)
            bound_f_signature = f_signature.bind(*args,**kargs)
            for param in f_signature.parameters.values():
                if param.name not in bound_f_signature.arguments:
                    bound_f_signature.arguments[param.name] = param.default
            return bound_f_signature.arguments

        # If annotation checking is turned off at the class or function level
        #   just return the result of calling the decorated function
        # Otherwise do all the annotation checking
        if not(self.checking_on and Check_Annotation.checking_on):
            return self._f(*args, **kargs)
        
        self.stuff = param_arg_bindings()
        
        try:
            # Check the annotation for every parameter (if there is one)
            for key, item in self.stuff.items():
                if key in self._f.__annotations__:
                    self.check(key, self._f.__annotations__[key], item)
            # Compute/remember the value of the decorated function
            answer = self._f(*args, **kargs)
            # If 'return' is in the annotation, check it
            if 'return' in self._f.__annotations__:
                self.stuff['_return'] = answer
                self.check('_return', self._f.__annotations__['return'], answer)
            # Return the decorated answer
            return answer
            
        # On first AssertionError, print the source lines of the function and reraise 
        except AssertionError:
#             print(80*'-')
#             for l in inspect.getsourcelines(self._f)[0]: # ignore starting line #
#                 print(l.rstrip())
#             print(80*'-')
            raise




  
if __name__ == '__main__':     
    # an example of testing a simple annotation 
     
    def f(x:int): pass
#     f = Check_Annotation(f)
#     f(3)
#     f('a')
           
    import driver
    driver.driver()
