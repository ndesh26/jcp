from parser_rules import symbol_table

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
        if self.label == "":
            return self.dst['value'] + ' = ' + '{}'.format(self.arg1['value']) + ' ' + self.op + ' ' + '{}'.format(self.arg2['value'])
        else:
            return self.label + ':' + self.dst['value'] + ' = ' + '{}'.format(self.arg1['value']) + ' ' + self.op + ' ' + '{}'.format(self.arg2['value'])

class AssignOp(Ins):
    def __init__(self, label="", op="", arg=None, dst=None):
        Ins.__init__(self, label, op)
        self.arg = arg
        self.dst = dst

    def __repr__(self):
        if self.label == "":
            return self.dst['value'] + ' = ' + '{}'.format(self.arg['value'])
        else:
            return self.label + ':' + self.dst['value'] + ' = ' + '{}'.format(self.arg['value'])

class IfStmt(Ins):
    def __init__(self, label="", op="", arg=None, target=""):
        Ins.__init__(self, label, op)
        self.arg = arg
        self.target = target

    def __repr__(self):
        return 'IfZ ' + '{}'.format(self.arg['value']) + ' Goto ' + self.target

class Label(Ins):
    def __init__(self, label=""):
        Ins.__init__(self, label)

    def __repr__(self):
        return self.label

class Tac(object):
    def __init__(self):
        self.code = []

    def generate_tac(self, node):
        if node.name == "BinaryOperator":
            if node.value == "=":
                arg1 = self.generate_tac(node.children[0])
                arg2 = self.generate_tac(node.children[1])
                assignop = AssignOp(arg=arg2, dst=arg1)
                self.code.append(assignop)
            else:
                arg1 = self.generate_tac(node.children[0])
                arg2 = self.generate_tac(node.children[1])
                dst = symbol_table.get_temp(node.type)
                binop = BinOp(op=node.value, arg1=arg1, arg2=arg2, dst=dst)
                self.code.append(binop)
                return dst

        elif node.name == "IfStmt":
            arg1 = self.generate_tac(node.children[0])
            iflbl = symbol_table.get_target()
            ifop = IfStmt(arg=arg1, target=iflbl)
            self.code.append(ifop)
            arg2 = self.generate_tac(node.children[2])
            afterlbl = symbol_table.get_target()
            afterop = Label(label="Goto"+afterlbl)
            self.code.append(afterop)
            ifop = Label(label=iflbl+":")
            self.code.append(ifop)
            arg3 = self.generate_tac(node.children[1])
            afterop = Label(label=afterlbl+":")
            self.code.append(afterop)

        elif node.name == "IntegerLiteral":
            return {'value': node.value, 'type': "int"}

        elif node.name == "DeclsRefExpr":
            return node.sym_entry

        else:
            for n in node.children:
                self.generate_tac(n);

    def print_tac(self):
        for ins in self.code:
            print(repr(ins))
