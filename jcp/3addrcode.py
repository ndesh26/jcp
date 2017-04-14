from parser_rules import symbol_table
from symbol_table import type_width

class Ins(object):
    def __init__(self, label="", op=""):
        self.label = label
        self.op = op

class BinOp(Ins):
    def __init__(self, label="", op="", arg1=None, arg2=None, dst=None):
        Ins.__init__(self, label, op)
        self.arg1 = arg1
        self.arg2 = arg2
        self.dst = dst

    def __repr__(self):
        return '\t' + self.dst['value'] + ' = ' + '{}'.format(self.arg1['value']) + ' ' + self.op + ' ' + '{}'.format(self.arg2['value'])

class AssignOp(Ins):
    def __init__(self, label="", op="", arg=None, dst=None, argp=False, dstp=False):
        Ins.__init__(self, label, op)
        self.arg = arg
        self.dst = dst
        self.argp = argp
        self.dstp = dstp

    def __repr__(self):
        if self.argp:
            arg = '*({})'.format(self.arg['value'])
        else:
            arg = '{}'.format(self.arg['value'])

        if self.dstp:
            dst = '*({})'.format(self.dst['value'])
        else:
            dst = '{}'.format(self.dst['value'])
        return '\t' + dst + ' = ' + arg

class BranchOp(Ins):
    def __init__(self, label="", op="", arg=None, target=""):
        Ins.__init__(self, label, op)
        self.arg = arg
        self.target = target

    def __repr__(self):
        return '\tIfZ ' + '{}'.format(self.arg['value']) + ' Goto ' + self.target

class GotoStmt(Ins):
    def __init__(self, label=""):
        Ins.__init__(self, label)

    def __repr__(self):
        return '\tGoto ' + self.label

class Label(Ins):
    def __init__(self, label=""):
        Ins.__init__(self, label)

    def __repr__(self):
        return self.label

class BeginFunc(Ins):
    def __init__(self, width=0):
        Ins(self)
        self.width = width

    def __repr__(self):
        return '\tBeginFunc {}'.format(self.width)

class EndFunc(Ins):
    def __init__(self):
        Ins(self)

    def __repr__(self):
        return '\tEndFunc'

class PushParam(Ins):
    def __init__(self, param):
        Ins(self)
        self.param = param

    def __repr__(self):
        return '\tPushParam {}'.format(self.param['value'])

class PopParam(Ins):
    def __init__(self, width):
        Ins(self)
        self.width = width

    def __repr__(self):
        return '\tPopParam {}'.format(self.width)

class Call(Ins):
    def __init__(self, func, dst=None):
        Ins(self)
        self.func = func
        self.dst = dst

    def __repr__(self):
        if self.dst == None:
            return '\tCall {}'.format(self.func['value'])
        else:
            return '\t{} = Call {}'.format(self.dst['value'], self.func['value'])

class Tac(object):
    def __init__(self):
        self.code = []
        self.table = None # represents the table of currently processing funtion

    def generate_tac(self, node):
        if node.name == "BinaryOperator":
            if node.value == "=":
                if node.children[0].name == "ArrayAccess":
                    dstp = True
                else:
                    dstp = False

                if node.children[1].name == "ArrayAccess":
                    argp = True
                else:
                    argp = False

                arg1 = self.generate_tac(node.children[0])
                arg2 = self.generate_tac(node.children[1])
                assignop = AssignOp(arg=arg2, dst=arg1, dstp=dstp, argp=argp)
                self.code.append(assignop)
            else:
                arg1 = self.generate_tac(node.children[0])
                arg2 = self.generate_tac(node.children[1])
                dst = symbol_table.get_temp(node.type, self.table)
                binop = BinOp(op=node.value, arg1=arg1, arg2=arg2, dst=dst)
                self.code.append(binop)
                return dst

        elif node.name == "VarDecl":
            if node.children and node.children[0].name == "InitListExpr":
                arg1 = node.sym_entry
                i = 0
                element = symbol_table.get_temp(node.type, self.table)
                size = {'value': type_width(node.type), 'type': node.type, 'arraylen': []}
                index = symbol_table.get_temp(node.type, self.table)
                indexop = AssignOp(arg=arg1, dst=index)
                self.code.append(indexop)
                for child in node.children[0].children:
                    arg2 = self.generate_tac(child)
                    assignop = AssignOp(arg=arg2, dst=index, dstp=True)
                    indexinc = BinOp(op="+", arg1=index, arg2=size, dst=index)
                    self.code.append(assignop)
                    self.code.append(indexinc)
                    i = i + 1

            elif node.children and node.children[0].name is not "ArrayInitialization":
                arg1 = node.sym_entry
                arg2 = self.generate_tac(node.children[0])
                assignop = AssignOp(arg=arg2, dst=arg1)
                self.code.append(assignop)


        elif node.name == "IfStmt":
            arg1 = self.generate_tac(node.children[0])
            iflbl = symbol_table.get_target()
            ifop = BranchOp(arg=arg1, target=iflbl)
            self.code.append(ifop)
            if len(node.children) == 3:
                arg2 = self.generate_tac(node.children[2])
                afterlbl = symbol_table.get_target()
                afterop = Label(label="\tGoto"+afterlbl)
                self.code.append(afterop)
                ifop = Label(label=iflbl+":")
                self.code.append(ifop)
                arg3 = self.generate_tac(node.children[1])
                afterop = Label(label=afterlbl+":")
                self.code.append(afterop)
            else:
                afterlbl = symbol_table.get_target()
                afterop = Label(label="\tGoto"+afterlbl)
                self.code.append(afterop)
                ifop = Label(label=iflbl+":")
                self.code.append(ifop)
                arg3 = self.generate_tac(node.children[1])
                afterop = Label(label=afterlbl+":")
                self.code.append(afterop)

        elif node.name == "WhileStmt":
            arg1 = self.generate_tac(node.children[0])
            whilelbl = symbol_table.get_target()
            whileop = Label(label=whilelbl+":")
            self.code.append(whileop)
            branchlbl = symbol_table.get_target()
            whileop = BranchOp(arg=arg1, target=branchlbl)
            self.code.append(whileop)
            afterlbl = symbol_table.get_target()
            afterop = Label(label="\tGoto"+afterlbl)
            self.code.append(afterop)
            whileop = Label(label=branchlbl+":")
            self.code.append(whileop)
            arg2 = self.generate_tac(node.children[1])
            whilestart = GotoStmt(label=whilelbl)
            self.code.append(whilestart)
            afterop = Label(label=afterlbl+":")
            self.code.append(afterop)

        elif node.name == "ForStmt":
            arg1 = self.generate_tac(node.children[0].children[0])
            forchecklbl = symbol_table.get_target()
            forcheckop = Label(label=forchecklbl+":")
            self.code.append(forcheckop)
            arg2 = self.generate_tac(node.children[1])
            forbodylbl = symbol_table.get_target()
            forendlbl = symbol_table.get_target()
            checkop = BranchOp(arg=arg2, target=forbodylbl)
            self.code.append(checkop)
            afterop = Label(label="\tGoto"+forendlbl)
            self.code.append(afterop)
            forbodyop = Label(label=forbodylbl+":")
            self.code.append(forbodyop)
            arg4 = self.generate_tac(node.children[3])
            arg3 = self.generate_tac(node.children[2].children[0])
            loopcheckop = Label(label="\tGoto"+forchecklbl)
            self.code.append(loopcheckop)
            forendop = Label(label=forendlbl+":")
            self.code.append(forendop)

        elif node.name == "MethodDecl":
            func = Label(label=node.children[0].sym_entry['value']+":")
            self.code.append(func)
            begin_func = BeginFunc()
            self.code.append(begin_func)
            self.table = node.children[0].sym_entry['table'];
            self.generate_tac(node.children[1])
            begin_func.width = node.children[0].sym_entry['table'].get_width()
            end_func = EndFunc()
            self.code.append(end_func)

        elif node.name == "MethodInvocation":
            k = 0
            if len(node.children) != 1:
                for i in (len(node.children) - 1, 1):
                    param = self.generate_tac(node.children[i])
                    k += type_width(param['type'])
                    self.code.append(PushParam(param))
            if node.type != "void":
                dst = symbol_table.get_temp(node.type, self.table)
            else:
                dst = None
            call = Call(func=node.children[0].sym_entry, dst=dst)
            self.code.append(call)
            if k != 0:
                self.code.append(PopParam(k))
            return dst


        elif node.name == "FloatLiteral":
            return {'value': node.value, 'type': "int", 'arraylen': []}

        elif node.name == "IntegerLiteral":
            return {'value': node.value, 'type': "int", 'arraylen': []}

        elif node.name == "DeclsRefExpr":
            return node.sym_entry

        elif node.name == "ArrayAccess":
            arg1 = self.generate_tac(node.children[0])
            index = self.generate_tac(node.children[1])
            size = type_width(node.type)
            length = len(node.arraylen)- node.dims
            for i in node.arraylen[length:]:
                size *= i
            dst = symbol_table.get_temp(node.type, self.table)
            multi = BinOp(op="*", arg1={'value': size, 'type': "int", 'arraylen': []}, arg2=index, dst=dst)
            binop = BinOp(op="+", arg1=arg1, arg2=dst, dst=dst)
            self.code.append(multi)
            self.code.append(binop)
            return dst

        else:
            for n in node.children:
                self.generate_tac(n);

    def print_tac(self):
        for ins in self.code:
            print(repr(ins))
