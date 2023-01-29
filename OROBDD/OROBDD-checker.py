from datetime import datetime,timedelta


import shlex
import re
import graphviz

import os
path=os.path.dirname(os.path.abspath(__file__))


class SOPGenerator:

    def extract_variables(self,string_expression):
        """
        takes a string expression in form:
         NOT A AND NOT B OR NOT A AND B OR A AND NOT B OR A AND B for example
        and returns a list of all the variables in it"""
        tokens=shlex.split(string_expression)
        lst=[]
        for token in tokens:
            if len(token)==1 and token.isalpha() and token not in lst:
                lst.append(token)
        lst.sort()
        return lst

    def evaluate(self,string,values):
        """
           takes an expression in form of :NOT A AND NOT B OR NOT A AND B OR A AND NOT B OR A AND B,
           or its paranthesized output     
           and string representing variable values ie : "00"
           and returns the result
        """
        function_string=self.parenthesize_expression(string,['NOT','!','~','not'])
        #print(function_string)
        function_string=self.parenthesize_expression(function_string,['AND','&','*','and'])
        # print(function_string)
        vars=self.extract_variables(string)
        tokens= shlex.split(function_string)
        for i in range(len(vars)):
            for j,token in enumerate(tokens):
                if token in vars:
                    tokens[j]=values[vars.index(token)]
        function_string=' '.join(tokens)
        return self.parse_boolean_function(function_string)

    def parse_boolean_function(self,function_string):
        """
        takes a boolean expression :ie  True OR False , or 1 OR 0, or more complex expressions and returns the result
        """
        # Use the shlex module to split the function string into a list of tokens
        tokens = shlex.split(function_string)
        # Initialize a stack to hold the operands and a result variable to hold the final result
        stack = []
        result = None
        # Define a dictionary of operator functions
        operations = {
            'AND': lambda x, y:  x&y,
            'and': lambda x, y:  x&y,
            '*': lambda x, y:  x&y,
            '&': lambda x, y:  x&y,

            'OR': lambda x, y: x |y ,
            'or': lambda x, y: x |y ,
            '+': lambda x, y: x |y ,
            '|': lambda x, y: x |y ,

            'NOT': lambda x: not x,
            'not': lambda x: not x,
            '~': lambda x: not x,
            '!': lambda x: not x,

            'XOR': lambda x, y: x ^ y,
            'xor': lambda x, y: x ^ y,
            '^': lambda x, y: x ^ y,
            
        }
        # Define a dictionary that maps boolean values to their integer equivalents
        boolean_values = {
            'True': 1,
            'False': 0,
            0:0,
            1:1,
            '0':0,
            '1':1,
        }
        # Iterate through the tokens, index= ti
        ti=0 
        #print(tokens)
        while(ti<len(tokens)):
            
            if tokens[ti] in operations:
                #the result stack is empty so far
                #print(tokens[ti])
                if len(stack)==0:
                    operand=''
                    #if the current operand is NOT, get the operand. eg: NOT A, we find A in this case    
                    if tokens[ti] == 'NOT' or tokens[ti] == '~' or tokens[ti] == '!' or tokens[ti]=='not':
                        # A is an expression enclosed with parentheses
                        if(tokens[ti+1]=='('):
                            
                            # get the reuslt of this expression
                            nxt=self.get_until_close(tokens,ti+1)
                            # print(' '.join(tokens[ti+2:nxt]))
                            operand= self.parse_boolean_function(' '.join(tokens[ti+2:nxt]))
                            operand=boolean_values[operand]
                           # print(''.join(tokens[ti+2:nxt]),'with result of ',operand)
                            result = operations[tokens[ti]](operand)
                            ti=nxt+1

                        else:
                            # A is a boolean value. eg :True, False, 1, 0
                            operand = boolean_values[tokens[ti+1]]
                            result = operations[tokens[ti]](operand)
                            ti+=2
                        #get the operation result
                        
                        #move to the next token
                        
                    else:
                        #AND,XOR or any binary expression cannot start an expression, there should be an element stored in the stack.
                        print('invalid input')
                        return None
                    stack.append(result)
                else:
                    #the stack has one or more elements

                    #if the current operand is NOT, get the operand. eg: NOT A, we find A in this case    
                    if tokens[ti] == 'NOT' or tokens[ti] == '~' or tokens[ti] == '!' or tokens[ti]=='not':
                        # A is an expression enclosed with parentheses
                        if(tokens[ti+1]=='('):

                            nxt=self.get_until_close(tokens,ti+1)
                            operand= self.parse_boolean_function(' '.join(tokens[ti+2:nxt]))
                            operand=boolean_values[operand]
                            result = operations[tokens[ti]](operand)
                            ti=nxt+1 #move to the next expression this one is already calculated
                        else:
                            operand = boolean_values[tokens[ti+1]]
                            result = operations[tokens[ti]](operand)
                            ti+=1
                    else: 
                        # a binary operator
                        operand2 = ''
                        operand1 = boolean_values[stack.pop()]
                        #print ('operand1is ',operand1)
                        if(tokens[ti+1]=='('):
                            nxt=self.get_until_close(tokens,ti+1)
                            operand2= self.parse_boolean_function(' '.join(tokens[ti+2:nxt]))
                            operand2=boolean_values[operand2]
                            result = operations[tokens[ti]](operand1,operand2)
                            """ if(tokens[ti]=='OR'):
                                print('op is or, and  operands are ',operand1,operand2,' = ',result,tokens[nxt]) """
                            ti=nxt+1
                        else:
                            operand2 = boolean_values[tokens[ti+1]]
                            result = operations[tokens[ti]](operand1, operand2)
                            """ if(tokens[ti]=='OR'):
                                print('op is or, and  operands are ',operand1,operand2,' = ',result) """
                            
                            ti+=2

                        
                    stack.append(result)
            else:
                # if our expression starts with a parentheses or boolean value.
                if(tokens[ti]=='('):
                    nxt=self.get_until_close(tokens,ti)
                    result= self.parse_boolean_function(' '.join(tokens[ti+1:nxt]))
                    ti=nxt+1
                else:
                    result=tokens[ti]
                    ti+=1
                stack.append(result)
            # If there are no more tokens, return the final result
        return result

    def get_until_close(self,lst,index):
        """returns the index of the closing parentheses if a string 
        and the index of an opening parentheses is passed"""
        prec=0
        if lst[index]=='(':
            prec+=1
        for i in range(index+1,len(lst)):
            if lst[i]=='(':
                prec+=1
            elif lst[i]==')':
                prec-=1
            if prec==0:
                return i
        print('no matching closing parantheses to the one at ',index)
        return None


    
    def parenthesize_expression(self,string_expression,exepressions : list):
        """
        takes a boolean expression if form similar to :NOT A AND NOT B OR NOT A AND B OR A AND NOT B OR A AND B
        and an expression such as AND , or , NOT
        and add parantheses around the expression accordingly
        i.e: parenthesize_expression("A OR B AND C","AND")-> :A OR ( B AND C)
        """
        tokens= shlex.split(string_expression)
        #if unary expression such as 'NOT'
        
        if 'NOT' in exepressions or '~' in exepressions or '!' in exepressions or 'not' in exepressions:
            i = 0
            while(i<len(tokens)-1):
                if tokens[i] in exepressions:
                    #print()
                    tokens.insert(i,'(')
                    i+=1
                    if tokens[i+1]=='(':
                        p=1
                        j=i+2
                        while(p!=0):
                            if tokens[j]=='(':
                                p+=1
                            elif tokens[j]==')':
                                p-=1
                            if j>=len(tokens):
                                print("invalid input?")
                                return string_expression
                            j+=1
                        tokens.insert(j,')')
                        i=i+2
                    else:
                        tokens.insert(i+2,')')
                        i+=2
                else:
                    i+=1
            return ' '.join(tokens)
        else:
            i=0
            while(i<len(tokens)-1):
                if tokens[i] in exepressions:
                    if tokens[i-1]==')':
                        p=1
                        j=i-2
                        while(p!=0):
                            if tokens[j]==')':
                                p+=1
                            elif tokens[j]=='(':
                                p-=1
                            if j<0:
                                print("invalid input?")
                                return string_expression
                            j-=1
                        tokens.insert(j+1,'(')
                        i+=1
                    else:
                        tokens.insert(i-1,'(')
                        i+=1
                    if tokens[i+1]=='(':
                        p=1
                        j=i+2
                        while(p!=0):
                            if tokens[j]=='(':
                                p+=1
                            elif tokens[j]==')':
                                p-=1
                            if j>=len(tokens):
                                print("invalid input?")
                                return string_expression
                            j+=1
                        tokens.insert(j,')')
                        i=i+2
                    else:
                        tokens.insert(i+2,')')
                        i+=2
                else:
                    i+=1
            return ' '.join(tokens)

    def binary_combinations(self,n):
        """generate all possible binary values for n variables, result is an array of strings:
        example: binary_combinations(3)->["000","001",...]"""
        def binary_combinations_recursive(n: int, prefix: str) :
            if n == 0:
                return [prefix]
            return binary_combinations_recursive(n - 1, prefix + "0")\
               + binary_combinations_recursive(n - 1, prefix + "1")
        return binary_combinations_recursive(n, "")

    def generate_SOP(self,expression):
        """generates the sop expression given expression similar to :
        A OR A AND ( A XOR B ) OR B  -->  A'B + AB' + AB """
        vars=self.extract_variables(expression)
        inputs=self.binary_combinations(len(vars))
        #print(expression)
        outputs=[self.evaluate(expression,input) for input in inputs]
        #print(outputs)
        terms=[]
        for i,output in enumerate(outputs):
            if output==1 or output=='1' or output==True or output=='True':
                term=inputs[i]
                conv=''
                for j,c in enumerate(term):
                    if c=='0':
                        conv+=vars[j]+"'"
                    else:
                        conv+=vars[j]
                terms.append(conv)
        return ' + '.join(terms)
        


class BDDNode:
  def __init__(self, variable, low=None, high=None,parent=None):
    self.variable = variable
    self.low = low
    self.high = high
    self.parents=[] if parent==None else [parent]          
  def __str__(self) :
        return str(self.variable)

  

class ROBDD:

  """
  We have variable variables so we need to be dynamic
  Algorithm:
  1-extract all variables, add them to stack or list -> function extract_variables(string expression)->tokens
  2- pick one variable from them to be a root (must be poped?)
  3- we need the positive and negative cofactors: function(picked_variable, stack, string expression or token)-> find positive and negative cofactors
                                                                                                              -> convert each to bolean expression
                                                                                                              -> recursivley call parse function on each cofactor(node)                                    
  """
  def __init__(self):
    self.root = None
    self.variables = {}
    self.nodes = []
    self.myture=self.create_node(True,None,None)
    self.myfalse=self.create_node(False,None,None)

  def create_node (self, variable, low, high,parent=None):
    """creates a node and add it to the diagram nodes list"""
    node = BDDNode(variable, low, high,parent)
    self.nodes.append(node)
    return node
  def create_node2 (self, variable, low, high,parent=None):
    """creates a node and add it to the diagram nodes list"""
    node = BDDNode(variable, low, high,parent)
    return node

  def spacify_string(self,s):
    """
    input string example: "AB' + A'CD"
    """
    result = ""

    for i, c in enumerate(s):
        if c.isalpha() and (i == 0 or s[i - 1] != " "):
            result += " "
        result += c
    return result
  
  def stringify_tokens(self,tokens,joiner=' '):
    """convert a list of tokens to a string concatenaed by the joiner"""
    return joiner.join(tokens)

  def extract_variables(self,string_expression):
      """takes a string expression and returns a tuple of (all the variables in it,the string expresion itself) """
      string_expression= self.spacify_string(string_expression)
      tokens = string_expression.replace("'",'').split(" ")
      res=[]
      for token in tokens:
         if token!='+' and token!='' and token not in res:
          res.append(token)
      return (res,string_expression)
  
  def generate_positive_negative_cofactors(self,string_expression,node_variable):
    """takes a string expression, returns a list of positive and negative cofactors  (AS STRING EXPRESSION)"""
    terms=string_expression.split('+')
    positive_cofactors,negative_cofactors=[],[]
    
    adash=node_variable+"'"
      
    for term in terms:
      term=re.sub(' +', '', term) #removes extra spaces 
      if adash in term:
        t=term.replace(adash, "")
        if t!='':
          negative_cofactors.append(t)
        else:
          negative_cofactors.append('1')
      elif node_variable in term:
        t=term.replace(node_variable, "")
        if t!='':
          positive_cofactors.append(t)
        else:
          positive_cofactors.append('1')
      else:
        if term!='':
          negative_cofactors.append(term)
          positive_cofactors.append(term)
   # print(positive_cofactors)
    positive_cofactors_string= self.stringify_tokens(positive_cofactors,' + ')
    negative_cofactors_string= self.stringify_tokens(negative_cofactors,' + ')
    
    for c in positive_cofactors:  
      if c in positive_cofactors and c+"'" in positive_cofactors and len(c)==1:
        positive_cofactors_string=True
        break
    if('1' in positive_cofactors):
      positive_cofactors_string=True
    elif(len(positive_cofactors)==0):
      positive_cofactors_string=False
    
    for c in negative_cofactors:  
      if c in negative_cofactors and c+"'" in negative_cofactors and len(c)==1:
        negative_cofactors_string=True
        break
    if('1' in negative_cofactors):
      negative_cofactors_string=True
    elif(len(negative_cofactors)==0):
      negative_cofactors_string=False
      

    #print(node_variable , positive_cofactors , negative_cofactors)
    #print(node_variable , positive_cofactors_string , negative_cofactors_string)
    return (positive_cofactors_string,negative_cofactors_string)
      
  def build_tree(self,string_expression,my_node_variables):
    """
    input: takes a string expression
    algorithm: 
    1- picks a variable
    2- pop it from variables list
    3- create a node with this variable
    4- get positive and negative cofactors of this var
    5- recursivley call build_tree with the remaining tokens and positive and negative cofactor
      on each edge of our node
    5.1- ::edited: you should pick a variable to split upon, in the current case, each new node 
      will have randomly different variable to split upon
    6 return our node
    """
    
    string_expression= self.spacify_string(string_expression)
    
    #print(string_expression)
    if len(my_node_variables)==1:
      #here we have 1 term, we can evaluate it using evaluate
      tokens=[i for i in string_expression.split(' ') if i !='']
      myvar=my_node_variables[0]
      insertat=[]
      for i in range(len(tokens[0:-1])):
        if tokens[i]!= '+' and tokens[i+1] !='+':
          insertat.append(i+1)
      for i in range(len(tokens)):
        if tokens[i]==myvar+"'":
            tokens[i] = 'NOT '+myvar
      for i in reversed(insertat):
        tokens.insert(i,'AND')
      string_expression=' '.join(tokens)
      
      out=[SOPGenerator().evaluate(string_expression,i)for i in ['0','1']]
      
      lst=[self.myfalse,self.myture]
      boolean_values = {
          'True': 1,
          'False': 0,
          0:0,
          1:1,
          '0':0,
          '1':1,
      }
      thisnode= self.create_node(my_node_variables.pop(),lst[boolean_values[out[0]]],lst[boolean_values[out[1]]])
      lst[boolean_values[out[1]]].parents.append(thisnode)
      lst[boolean_values[out[0]]].parents.append(thisnode)
      return thisnode
    elif len(my_node_variables)==0:
      return None
    else:
      my_node_variable=my_node_variables.pop()
      pos_cofactors,neg_cofactors=self.generate_positive_negative_cofactors(string_expression,my_node_variable)

      myposchild=None
      mynegchild=None
      if(neg_cofactors==True):
        mynegchild=self.myture
      elif(neg_cofactors==False):
        mynegchild=self.myfalse
      else:
        mynegchild=self.build_tree(neg_cofactors,my_node_variables.copy())
      
      if(pos_cofactors==True):
        myposchild=self.myture
      elif(pos_cofactors==False):
        myposchild=self.myfalse
      else:
        myposchild=self.build_tree(pos_cofactors,my_node_variables.copy())
      
      thisnode=self.create_node (my_node_variable,mynegchild,myposchild)
      myposchild.parents.append(thisnode)
      mynegchild.parents.append(thisnode)
      
      return thisnode

  def build_tree2(self,string_expression,my_node_variables):#new approach, optimized bulding, rather than full bulid then trimming
    """
    input: takes a string expression
    algorithm: 
    1- picks a variable
    2- pop it from variables list
    3- create a node with this variable
    4- get positive and negative cofactors of this var
    5- recursivley call build_tree2 with the remaining tokens and positive and negative cofactor
      on each edge of our node
    5.1- ::edited: you should pick a variable to split upon, in the current case, each new node 
      will have randomly different variable to split upon
    6  - return our node * if unique else return the similar, already existing one *
    6.1- if a node's low and high branches point to the same child, the child is returned instead  
    """
    
    string_expression= self.spacify_string(string_expression)
    
    #print(string_expression)
    if len(my_node_variables)==1:
      #here we have 1 term, we can evaluate it using evaluate
      tokens=[i for i in string_expression.split(' ') if i !='']
      myvar=my_node_variables[0]
      insertat=[]
      for i in range(len(tokens[0:-1])):
        if tokens[i]!= '+' and tokens[i+1] !='+':
          insertat.append(i+1)
      for i in range(len(tokens)):
        if tokens[i]==myvar+"'":
            tokens[i] = 'NOT '+myvar
      for i in reversed(insertat):
        tokens.insert(i,'AND')
      string_expression=' '.join(tokens)
      
      out=[SOPGenerator().evaluate(string_expression,i)for i in ['0','1']]
      
      lst=[self.myfalse,self.myture]
      boolean_values = {
          'True': 1,
          'False': 0,
          0:0,
          1:1,
          '0':0,
          '1':1,
      }
      thisnode= self.create_node2(my_node_variables.pop(),lst[boolean_values[out[0]]],lst[boolean_values[out[1]]])
      if self.compare_nodes(lst[boolean_values[out[0]]],lst[boolean_values[out[1]]]):
        return lst[boolean_values[out[0]]]
      for node in self.nodes:
        if self.compare_nodes(node,thisnode):
          lst[boolean_values[out[1]]].parents.append(node)
          lst[boolean_values[out[0]]].parents.append(node)
          return node
          
      lst[boolean_values[out[1]]].parents.append(thisnode)
      lst[boolean_values[out[0]]].parents.append(thisnode)   
      self.nodes.append(thisnode)


      return thisnode
    elif len(my_node_variables)==0:
      return None
    else:
      my_node_variable=my_node_variables.pop()
      pos_cofactors,neg_cofactors=self.generate_positive_negative_cofactors(string_expression,my_node_variable)

      myposchild=None
      mynegchild=None
      if(neg_cofactors==True):
        mynegchild=self.myture
      elif(neg_cofactors==False):
        mynegchild=self.myfalse
      else:
        mynegchild=self.build_tree2(neg_cofactors,my_node_variables.copy())
      
      if(pos_cofactors==True):
        myposchild=self.myture
      elif(pos_cofactors==False):
        myposchild=self.myfalse
      else:
        myposchild=self.build_tree2(pos_cofactors,my_node_variables.copy())
      
      if self.compare_nodes(mynegchild,myposchild):
        return myposchild

      thisnode=self.create_node2 (my_node_variable,mynegchild,myposchild)
      for node in self.nodes:
        if self.compare_nodes(node,thisnode):
          myposchild.parents.append(node)
          mynegchild.parents.append(node)
          return node
          
      myposchild.parents.append(thisnode)
      mynegchild.parents.append(thisnode)
      self.nodes.append(thisnode)
      return thisnode


  def compare_nodes(self,node1, node2):
    """full comparison of 2 nodes"""
    if node1 is None and node2 is None:
      return True
    if node1 is None or node2 is None:
      return False
    if node1.variable != node2.variable:
      return False
    return self.compare_nodes(node1.low, node2.low) and\
     self.compare_nodes(node1.high, node2.high)
    
  def parse(self,string_expression):
    """
    the Robdd construcor.
    Takes input in form of :A OR A AND ( A XOR B ) OR B for example, and construct the tree accordingly
    """
    sop=SOPGenerator()
    try:
      string_expression=sop.generate_SOP(string_expression)
    except:
      print('non usual input')

    factors=self.extract_variables(string_expression)[0]
    factors= list(sorted(factors,reverse=True))
    self.variables=factors.copy()
    #print(factors ,string_expression)
    if string_expression=='':
      self.root=self.myfalse
    else:
      self.root = self.build_tree(string_expression,factors)
 
  def parse2(self,string_expression): #new approach, calls new build_tree2 function
    """
    the Robdd construcor.
    Takes input in form of :A OR A AND ( A XOR B ) OR B for example, and construct the tree accordingly
    """
    sop=SOPGenerator()
    try:
      string_expression=sop.generate_SOP(string_expression)
    except:
      print('non usual input')

    factors=self.extract_variables(string_expression)[0]
    factors= list(sorted(factors,reverse=True))
    self.variables=factors.copy()
    #print(factors ,string_expression)
    if string_expression=='':
      self.root=self.myfalse
    else:
      self.root = self.build_tree2(string_expression,factors)


  def trim_bdd(self):
    """
    algorithm:
     1- iterate over each node, compare it to the other nodes, if it is similar to one 
     of them, remove it and do corresponding changes(update its parent to ponit to the other node, update this and the other node's parents list)
     2- iterate over each node, if it low and high edges point to the same node, remove it and do corresponding changes made in step 1
    """
    now =datetime.now()
    toerase=[]
    for i,node in enumerate (self.nodes):
      if (len(node.parents)!=0):
        for j,node2 in enumerate(self.nodes):
          if(j>i):
            if (self.compare_nodes(node,node2)):
              for parent in node.parents:
                if(parent.low==node):
                  parent.low=node2
                  if i not in toerase:
                    toerase.append(i)
                if(parent.high==node):
                  parent.high=node2
                  if i not in toerase:
                    toerase.append(i)

              node2.parents.extend(node.parents)
              node.parents.clear()
                  

               # print([t.variable for t in node.parents],node)
    
    for i in reversed(toerase):
        del self.nodes[i]

    #remove nodes that lead to same result in low or high edges

    toerase=[]
    for i,node in enumerate (self.nodes):
      if self.compare_nodes(node.low,node.high) and node.high!=None:
        # node low equals node high
        for parent in node.parents:
          if(self.compare_nodes(parent.low,node)):
            parent.low=node.low
            if i not in toerase:
              toerase.append(i)
          if(self.compare_nodes(parent.high,node)):
            parent.high=node.low
            if i not in toerase:
              toerase.append(i)
            node.low.parents.append(parent)
              
        try:
          node.parents.clear()
        except:
          
          print("couldn't remove", node , 'from', node.low,' parents ')
          
        if node==self.root:
            toerase.append(i)
            self.root=node.low
   
    for i in reversed(toerase):
          del self.nodes[i]
   # print('done trimming')
    print('trimming  took: ',datetime.now()-now)

  def evaluate(self,expression):
    """takes string expression, and return the robdd output"""
    if self.root is None:
      print("the bdd hasn't parsed any functions yet")
      return None
    else:
      if type(expression) is str:
        lst=list(reversed([bool(int(i))for i in expression]))
        
        resnode=self.root
        while(resnode.variable!=True and resnode.variable!=False):
          n=lst[self.variables.index(resnode.variable)]
          if(n==False):
            resnode=resnode.low
          elif(n==True):
            resnode=resnode.high
          
      return resnode.variable 

  def generate_truthtable(self):
    """generates all possible inputs then evaluate each one of them"""
    inputs=self.binary_combinations(len(self.variables))
    res=[]
    for i in reversed(self.variables):
      print (i,end=' ')
    print ('  | f')
    print ((len(self.variables)+1)*'--',end='')
    print('+--')
    for input in inputs:
      for c in input:
        print( c, end=' ')
      out=int(self.evaluate(input))
      print('  |',out)
      res.append(out)
    
    print('number of combinations = ',2**len(inputs[0]))
    return res
 

  def binary_combinations(self,n):
    """generate all possible binary values for n variables, result is an array of strings:
    example: binary_combinations(3)->["000","001",...]"""
    def binary_combinations_recursive(n: int, prefix: str) :
        if n == 0:
            return [prefix]
        return binary_combinations_recursive(n - 1, prefix + "0") + binary_combinations_recursive(n - 1, prefix + "1")
    return binary_combinations_recursive(n, "")
  
  def construct(self,expression):
    self.parse(expression)  
    self.trim_bdd()

  def construct2(self,expression):
    self.parse2(expression)


def preorder_traverse(root):
  """
  Traverses the given binary tree in pre-order.
  """
  if root is not None:
    # Visit the root node
    print(root.variable,":" ,id(root.low)," , ",id(root.high)) 

    # Traverse the left subtree
    preorder_traverse(root.low)

    # Traverse the right subtree
    preorder_traverse(root.high)

def draw_graph(root,labe2l=None):
   # Graphically represents the given ROBDD using graphviz.
    g = graphviz.Digraph(format='pdf')
    g.attr(rankdir='TB')
    g.attr('node', shape='circle')
    g.attr(label=labe2l)
    draw_nodes=[]
    def draw_node(node):
       # Recursively draws the given node and all its children.
        if node in drawn_nodes:
        # Node has already been drawn, so just create a reference to it
          return
        # Mark the node as drawn
        drawn_nodes.add(node)
        if node.low == node.high and node.high==None:
        # Node is a terminal node, so label it with its variable
          g.node(str(id(node)), str(node),shape='square')
        else:
        # Node is not a terminal node, so label it with its variable name and draw its children
            g.node(str(id(node)), node.variable)
            g.edge(str(id(node)), str(id(node.low)),style='dashed')
            draw_node(node.low)
            g.edge(str(id(node)), str(id(node.high)))
            draw_node(node.high)
    drawn_nodes = set()
    draw_node(root)
    return g

def compare_expressions(exp1,exp2):
    robdd1,robdd2=ROBDD(),ROBDD()
    robdd1.construct(exp1)
    robdd2.construct(exp2)
    g=draw_graph(robdd1.root,exp1)
    g2=draw_graph(robdd2.root,exp2)
    print('_______________________________________________________')
    print('comparing: ',exp1 , 'with', exp2)
    now = datetime.now()
    if robdd1.compare_nodes(robdd1.root,robdd2.root):
      print("from ROBDD: Expressions are identical")
    else:
      print("from ROBDD: Expressions are not identical")
    after= datetime.now()
    d1=after-now

    aa='1'
    while (aa!='0'):
      aa=input('would u like to see the ROBDD visuialization? [1 , 0]: ')
      if aa=='0':
        break
      try:
        g.render(exp1.replace('|', ' OR ').replace('*', ' AND ').replace('!',' NOT ').replace('~','NOT'),path,view=True)
        g2.render(exp2.replace('|', ' OR ').replace('*', ' AND ').replace('!',' NOT ').replace('~','NOT'),path,view=True)
        aa='0'
      except:
        print("permission denied, one or both of the files might be already open, close them and try again")
        aa=='1'
  
    aa=input('would u like to see the truth table? [1 , 0]: ')
    now=datetime.now()
    if aa!='0':
      a=robdd1.generate_truthtable()
      b=robdd2.generate_truthtable()
      if a==b:
          print("from truth table: Expressions are identical")
      else:
          print("from truth table: Expressions are not identical")
    after=datetime.now()
    d2=after-now

    print("ROBDD verification  approach took: ", d1)
    print("Truth table verification approach took: ", d2)

    return robdd1.compare_nodes(robdd1.root,robdd2.root)

def compare_appraoches(exp1):
    """
    for testing purposes, takes an expression, and build an robdd tree using 2 approaches.
    1- build a BDD tree, then optimizing it by removing redundancy and merging isomorphic nodes
    2- build an ROBDD tree from the beginning, using memoization to check if the node to be added already exists
       if so, it uses the already created node instead of adding new one, also if a node found to be of the same positive
       and negative cofactors, it uses one of these child nodes instead of the created nodes to as a reduction teqnique
    """
    robdd1,robdd2=ROBDD(),ROBDD()
    constr=datetime.now()
    print('comparing: ',exp1 , 'with building then trimming and trimming itself')
    robdd1.construct(exp1)

    print('old approach construction took: ' ,datetime.now()-constr)
    constr=datetime.now()
    robdd2.construct2(exp1)
    print('new approach construction took: ' ,datetime.now()-constr)
    g=draw_graph(robdd1.root,exp1)
    g2=draw_graph(robdd2.root,exp1+'appraoch2')
    now = datetime.now()
    if robdd1.compare_nodes(robdd1.root,robdd2.root):
      print("from ROBDD: Expressions are identical")
    else:
      print("from ROBDD: Expressions are not identical")
    after= datetime.now()
    d1=after-now
    print('______________________________________________________________________________________________________________')

    aa='1'
    while (aa!='0'):
      aa=input('would u like to see the ROBDD visuialization? [1 , 0]: ')
      if aa=='0':
        break
      try:
        g.render(exp1.replace('|', ' OR ').replace('*', ' AND ').replace('!',' NOT ').replace('~','NOT'),path,view=True)
        g2.render((exp1+'appraoch2').replace('|', ' OR ').replace('*', ' AND ').replace('!',' NOT ').replace('~','NOT'),path,view=True)
        aa='0'
      except:
        print("permission denied, one or both of the files might be already open, close them and try again")
        aa=='1'
  
    aa=input('would u like to see the truth table? [1 , 0]: ')
    now=datetime.now()
    if aa!='0':
      a=robdd1.generate_truthtable()
      b=robdd2.generate_truthtable()
      if a==b:
          print("from truth table: Expressions are identical")
      else:
          print("from truth table: Expressions are not identical")
    after=datetime.now()
    d2=after-now

    print("ROBDD verification  approach took: ", d1)
    print("Truth table verification approach took: ", d2)

    return robdd1.compare_nodes(robdd1.root,robdd2.root)

######################################################################################################################################################





#test cases  

s= " A'B' + A'B + AB' + AB " #old subscription, MIGHT NOT WORK FOR NOW
compare_appraoches(s)

# You can any of the following formats
s= " A * B  + ! A * C + A * ! B * C  "
compare_appraoches(s)

s= " A * B * C + ! A + A * ! B * C"

s1 = " ( NOT D XOR C ) AND ( B XOR A ) AND ( E OR ! E ) * ( E OR F ) AND G XOR X AND Y OR Z OR V OR N OR C " # will take long time
compare_appraoches(s)
s= " ! A + C + B * ! B "

s = " A OR B XOR C"

s1= " ( a * b + ! a * ! b ) AND ( c * d + ! c * ! d )"
s= " ! ( ! ( ! A ) ) "

s= ' ab + cd + ef'
s1= ' ab + ef + cd '

#compare_expressions(s,s1)


s= " NOT A AND NOT B OR NOT A AND B OR A AND NOT B OR A AND B"

s= " ( A * B ) OR ( NOT A AND B ) | ( A XOR NOT B ) OR ( NOT A AND NOT B ) "

s1 = " A AND ! A + B & ~ B "
s1=' A OR B AND C OR ( C XOR A ) '


s = " ( A XOR B ) AND ( C XOR NOT D )  & ( E or ! E )"

s1 = "(  NOT D XOR C ) AND ( B XOR A )  "



s1= " a or b "
s= " a and b or c and d or e and f "