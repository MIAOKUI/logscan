## '(#e3# | #e2#) |(!#e3# & #e4#)', 'e1aaaaaae2'

class Token:
    LEFTBRACKET = 'LEFTBRACKET'
    RIGHTBRACKET = 'RIGHTBRACKET'
    PATTEN = 'PATTEN'
    UNARY = 'UNARY'
    BINARY = 'BINARY'

    def __init__(self,value, type = None):
        self.value = value
        self.type = type

class Node:
    def __init__(self, token):
        self.value = token
        self.left = None
        self.right = None

class ASTree:
    def __init__(self,Node):
        self.root = Node
        self.left = None
        self.right = None
    def add_left(self, tree):
        self.left = tree
    def add_right(self, tree):
        self.right = tree


class Match:
    def __init__(self,exprs):
        self.exprs = exprs
        self.exprsToken = []
        self.astTree = None

    def tokenizer(self):
        expr = []
        isExpr = False
        for c in exprs:
            if c == '(':
                self.exprsToken.append( Token(c, Token.LEFTBRACKET))
            elif c == ')':
                self.exprsToken.append(Token(c, Token.RIGHTBRACKET))
            elif c in '&|':
                self.exprsToken.append(Token(c, Token.BINARY))
            elif c == '!':
                self.exprsToken.append(Token(c, Token.UNARY))
            elif c == '#':
                isExpr = not isExpr
            else:
                if isExpr:
                    expr.append(c)
                else:
                    self.exprsToken.append(Token( ''.join(expr), Token.PATTEN))
                    expr = []

    def make_sub_tree(self, stack, currentTree):
        t = currentTree
        while stack[-1]:
            s = stack.pop()
            if t.root.type == Token.PATTEN:
                if s.root.type == Token.LEFTBRACKET:
                    stack.append(s)
                    stack.append(t)
                elif s.root.type == Token.BINARY or s.root.typ == Token.UNARY:
                    s.right = t
                    stack.append(s)
                else:
                    raise Exception('Wrong expression')
            elif t.root.type == Token.BINARY:
                if s.root.type == Token.RIGHTBRACKET:
                    raise Exception('Wrong expression: without left bracket')
                elif s.root.type == Token.LEFTBRACKET:
                    stack.append(t)
                else:
                    t.add_left(s)
                    stack.append(t)
            elif t.root.type == Token.UNARY:
                stack.append(t)


    def make_asTree(self):
        stack = []
        for token in self.exprsToken:
            tree = ASTree(token)
            if tree.root.type == Token.LEFTBRACKET:
                stack.append(tree)
            elif tree.root.type == Token.UNARY:
                stack.append(tree)
            elif tree.root.type == Token.BINARY:
                self.make_sub_tree(stack, tree)
            elif tree.root.type == Token.PATTEN:
                self.make_sub_tree(stack,tree)
            elif tree.root.type == Token.RIGHTBRACKET:
                self.make_sub_tree(stack, tree)
            else:
                raise Exception('Wrong expression')
        self.astTree = stack.pop()








