OPERATORS = ["+","-","*"]
UNARY_OPERATOR_RANKING = 4

def get_ranking(operator):
    if operator in OPERATORS:
        return OPERATORS.index(operator)
    return 0

def value(l_input,l_output,ranking):
    element = l_input.pop(0)
    if element in OPERATORS:
        value(l_input,l_output,UNARY_OPERATOR_RANKING)
        l_output.append(("uo",element)) # unary operator
    else:
        l_output.append(("op",element)) # operand
    while l_input and get_ranking(l_input[0])>=ranking:
        operator = l_input.pop(0)
        value(l_input,l_output,get_ranking(operator))
        l_output.append(("bo",operator)) # binary operator
    return

#a+-b*c-d
infix = ["a","+","-","b","*","-","c","-","d"]

output = []
value(infix,output,0)
