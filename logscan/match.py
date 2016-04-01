import re


class Token:
    LEFTBRACKET = 'LEFTBRACKET'
    RIGHTBRACKET = 'RIGHTBRACKET'
    PATTEN = 'PATTEN'
    UNARY = 'UNARY'
    BINARY = 'BINARY'

    def __init__(self, value, optype=None):
        self.value = value
        self.optype = optype


class ASTree:
    bool_operator = {
            '|': lambda left,right: left | right,
            '&': lambda left,right: left & right,
            '!': lambda right: not right}

    def __init__(self, token):
        self.root = token
        self.left = None
        self.right = None

    def patten_match(self, line):
        return(re.search(self.root.value, line) is None)

    def add_left(self, tree):
        self.left = tree

    def add_right(self, tree):
        self.right = tree

    def __str__(self):
        return('tree:{0}:{1}'.format(self.root.optype, self.root.value))

    def __repr__(self):
        return(self.__str__())

    def first_front(self,fn):
        fn(self.root.value)
        if self.left:
            self.left.first_front(fn)
        if self.right:
            self.right.first_front(fn)

    def astree_match(self,line):
        if self.root.optype == Token.BINARY:
            left_value =  self.left.astree_match(line)
            right_value = self.right.astree_match(line)
            return(ASTree.bool_operator[self.root.value](left_value, right_value))
        elif self.root.optype == Token.UNARY:
            right_value = self.right.astree_match(line)
            return(ASTree.bool_operator[self.root.value](right_value))
        elif self.root.optype ==  Token.PATTEN:
            return(self.patten_match(line))
        else:
            raise Exception('Wrong ASTree')


class Matcher:
    def __init__(self, exprs):
        self.exprs = exprs
        self.exprs_token = []
        self.astree = None

    def tokenizer(self):
        expr = []
        is_expr = False
        for c in self.exprs:
            if not c.strip():
                continue
            if c == '(':
                self.exprs_token.append(Token(c, Token.LEFTBRACKET))
            elif c == ')':
                self.exprs_token.append(Token(c, Token.RIGHTBRACKET))
            elif c in '&|':
                self.exprs_token.append(Token(c, Token.BINARY))
            elif c == '!':
                self.exprs_token.append(Token(c, Token.UNARY))
            elif c == '#':
                is_expr = not is_expr
                if not is_expr:
                    self.exprs_token.append(Token(''.join(expr), Token.PATTEN))
                    expr = []
            else:
                if is_expr:
                    expr.append(c)

    def make_sub_tree(self, stack, current):
        t = current
        while stack and stack[-1].root.optype != Token.LEFTBRACKET:
            s = stack.pop()
            if s.root.optype == Token.BINARY:
                s.add_right(t)
                if stack[-1].root.optype == Token.LEFTBRACKET:
                    raise Exception('Binary operation without left')
                else:
                    left = stack.pop()
                    s.add_left(left)
                    t = s
            elif s.root.optype == Token.UNARY:
                s.add_right(t)
                t = s
            else:
                raise Exception('Two continue expression pattern without bool operator')
        stack.append(t)

    def make_astree(self):
        stack = []
        for token in self.exprs_token:
            tree = ASTree(token)
            if tree.root.optype == Token.LEFTBRACKET:
                stack.append(tree)
            elif tree.root.optype == Token.BINARY or tree.root.optype == token.UNARY:
                stack.append(tree)
            elif tree.root.optype == Token.PATTEN:
                self.make_sub_tree(stack, tree)
            else:
                subtree = stack.pop()
                s = stack.pop()
                if s.root.optype == Token.LEFTBRACKET:
                    self.make_sub_tree(stack, subtree)
                else:
                    raise Exception("Wrong expression, brackets not compatible")
        if len(stack) == 1:
            self.astree = stack.pop()
        else:
            raise Exception('Wrong expression')

    def ready(self):
        self.tokenizer()
        self.make_astree()

    def match(self,line):
        return(self.astree.astree_match(line))

if __name__ == '__main__':
    m = Matcher('!#e5# & (#e3# | #e2#)|!(#e3# & #e4#)')
    m.ready()
    line = 'e5afdbsakfsae2'
    m.match(line)
    print(m.match(line))
