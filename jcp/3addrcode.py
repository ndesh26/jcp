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
    def __init__(self, width, dst=None):
        Ins(self)
        self.width = width
        self.dst = dst

    def __repr__(self):
        if self.dst:
            return '\t{} = PopParam {}'.format(self.dst['value'], self.width)
        else:
            return '\tPopParam {}'.format(self.width)

class SetStack(Ins):
    def __init__(self, change):
        Ins(self)
        self.change = change

    def __repr__(self):
        return '\tSetStack {}'.format(self.change)

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

class Cmp(Ins):
    def __init__(self, arg1, arg2):
        Ins(self)
        self.arg1 = arg1
        self.arg2 = arg2

    def __repr__(self):
        return '\tCMP {}, {}'.format(self.arg1['value'], self.arg2['value'])

class Jmp(Ins):
    def __init__(self, cond, target):
        Ins(self)
        self.cond = cond
        self.target = target

    def __repr__(self):
        return '\t{} {}'.format(self.cond, self.target)

class Ret(Ins):
    def __init__(self, value):
        Ins(self)
        self.value = value

    def __repr__(self):
        return '\tReturn {}'.format(self.value['value'])

class Tac(object):
    def __init__(self):
        self.code = []
        self.table = None # represents the table of currently processing funtion

    def generate_tac(self, node, parent=None, true_lbl=None, false_lbl=None):
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

            elif node.value == "&&":
                arg1_true_lbl = symbol_table.get_target()
                arg1 = self.generate_tac(node.children[0], true_lbl=arg1_true_lbl, false_lbl=false_lbl)
                arg1_true = Label(label=arg1_true_lbl+":")
                self.code.append(arg1_true)
                arg2 = self.generate_tac(node.children[1], true_lbl=true_lbl, false_lbl=false_lbl)

            elif node.value == "||":
                arg1_false_lbl = symbol_table.get_target()
                arg1 = self.generate_tac(node.children[0], true_lbl=true_lbl, false_lbl=arg1_false_lbl)
                arg1_false = Label(label=arg1_false_lbl+":")
                self.code.append(arg1_false)
                arg2 = self.generate_tac(node.children[1], true_lbl=true_lbl, false_lbl=false_lbl)

            elif node.value in ["<", ">", ">=", "<=", "==", "!="]:
                arg1 = self.generate_tac(node.children[0])
                arg2 = self.generate_tac(node.children[1])
                cmp = Cmp(arg1=arg1, arg2=arg2)
                self.code.append(cmp)
                cond_map = {'<': 'JL', '>': 'JG', '>=': 'JGE', '<=': 'JLE', '==': 'JE', '!=': 'JNE'}
                true_jmp = Jmp(cond=cond_map[node.value], target=true_lbl)
                self.code.append(true_jmp)
                goto_false = Jmp(cond='JMP', target=false_lbl)
                self.code.append(goto_false)

            else:
                arg1 = self.generate_tac(node.children[0])
                arg2 = self.generate_tac(node.children[1])
                dst = symbol_table.get_temp(node.type, self.table)
                binop = BinOp(op=node.value, arg1=arg1, arg2=arg2, dst=dst)
                self.code.append(binop)
                return dst

        elif node.name == "UnaryOperator":
            if node.value == "post++":
                arg = self.generate_tac(node.children[0])
                dst = symbol_table.get_temp(node.type, self.table)
                assignop = AssignOp(arg=arg, dst=dst)
                self.code.append(assignop)
                dst2 = symbol_table.get_temp(node.type, self.table)
                binop = BinOp(op="+", arg1=arg, arg2={'value':1, 'type': 'int', 'arraylen': []}, dst=dst2)
                self.code.append(binop)
                assignop = AssignOp(arg=dst2, dst=arg)
                self.code.append(assignop)
                return dst

            if node.value == "pre++":
                arg = self.generate_tac(node.children[0])
                dst = symbol_table.get_temp(node.type, self.table)
                binop = BinOp(op="+", arg1=arg, arg2={'value':1, 'type': 'int', 'arraylen': []}, dst=dst)
                self.code.append(binop)
                assignop = AssignOp(arg=dst, dst=arg)
                self.code.append(assignop)
                return dst

        elif node.name == "VarDecl":
            if node.children and node.children[0].name == "InitListExpr":
                arg1 = node.sym_entry
                element = symbol_table.get_temp(node.type, self.table)
                size = {'value': type_width(node.type), 'type': node.type, 'arraylen': []}
                index = symbol_table.get_temp(node.type, self.table)
                indexop = AssignOp(arg=arg1, dst=index)
                self.code.append(indexop)
                self.generate_tac(node.children[0], parent=index)

            elif node.children and node.children[0].name is not "ArrayInitialization":
                arg1 = node.sym_entry
                arg2 = self.generate_tac(node.children[0])
                assignop = AssignOp(arg=arg2, dst=arg1)
                self.code.append(assignop)

        elif node.name == "InitListExpr":
            if node.children[0].name is not "InitListExpr":
                size = {'value': type_width(node.children[0].type), 'type': node.children[0].type, 'arraylen': []}
                for child in node.children:
                    arg2 = self.generate_tac(child)
                    assignop = AssignOp(arg=arg2, dst=parent, dstp=True)
                    indexinc = BinOp(op="+", arg1=parent, arg2=size, dst=parent)
                    self.code.append(assignop)
                    self.code.append(indexinc)
            else:
                j = 0
                while j < len(node.children) and node.children[j].name == "InitListExpr":
                    arg = self.generate_tac(node.children[j], parent=parent)
                    j = j + 1


        elif node.name == "IfStmt":
            if len(node.children) == 2: # in this target points to else case
                if_true_lbl = symbol_table.get_target()
                if_next_lbl = symbol_table.get_target()
                arg1 = self.generate_tac(node.children[0], true_lbl=if_true_lbl, false_lbl=if_next_lbl)
                true_label = Label(label=if_true_lbl+":")
                self.code.append(true_label)
                arg1 = self.generate_tac(node.children[1])
                end = Label(label=if_next_lbl+":")
                self.code.append(end)
            else:
                if_true_lbl = symbol_table.get_target()
                if_false_lbl = symbol_table.get_target()
                if_next_lbl = symbol_table.get_target()
                arg1 = self.generate_tac(node.children[0], true_lbl=if_true_lbl, false_lbl=if_false_lbl)
                true_label = Label(label=if_true_lbl+":")
                self.code.append(true_label)
                arg1 = self.generate_tac(node.children[1])
                goto = Jmp(cond='JMP', target=if_next_lbl)
                self.code.append(goto)
                false_label = Label(label=if_false_lbl+":")
                self.code.append(end)
                arg1 = self.generate_tac(node.children[2])
                end = Label(label=if_next_lbl+":")
                self.code.append(end)

        elif node.name == "WhileStmt":
            while_true_lbl = symbol_table.get_target()
            while_begin_lbl = symbol_table.get_target()
            while_next_lbl = symbol_table.get_target()
            begin_label = Label(label=while_begin_lbl+":")
            self.code.append(begin_label)
            self.generate_tac(node.children[0], true_lbl=while_true_lbl, false_lbl=while_next_lbl)
            true_label = Label(label=while_true_lbl+":")
            self.code.append(true_label)
            self.generate_tac(node.children[1])
            goto_begin = Jmp(cond='JMP', target=while_begin_lbl)
            self.code.append(goto_begin)
            next_label = Label(label=while_next_lbl+":")
            self.code.append(next_label)

        elif node.name == "ForStmt":
            self.generate_tac(node.children[0].children[0])
            for_cond_label = symbol_table.get_target()
            for_true_label = symbol_table.get_target()
            for_false_label = symbol_table.get_target()
            for_cond = Label(label=for_cond_label+":")
            self.code.append(for_cond)
            self.generate_tac(node.children[1], true_lbl=for_true_label, false_lbl=for_false_label)
            for_true = Label(label=for_true_label+":")
            self.code.append(for_true)
            self.generate_tac(node.children[3])
            self.generate_tac(node.children[2])
            goto_cond = Jmp(cond='JMP', target=for_cond_label)
            self.code.append(goto_cond)
            for_false = Label(label=for_false_label+":")
            self.code.append(for_false)

        elif node.name == "MethodDecl":
            func = Label(label=node.children[0].sym_entry['value']+":")
            self.code.append(func)
            begin_func = BeginFunc()
            self.code.append(begin_func)
            self.table = node.children[0].sym_entry['table'];
            self.generate_tac(node.children[1])
            begin_func.width = node.children[0].sym_entry['table'].get_width() - node.children[0].sym_entry['table'].get_arg_size()
            end_func = EndFunc()
            self.code.append(end_func)

        elif node.name == "MethodInvocation":
            k = 0
            if node.type != "void":
                self.code.append(SetStack(-type_width(node.type)))
            if len(node.children) != 1:
                for i in range(len(node.children) - 1, 0, -1):
                    param = self.generate_tac(node.children[i])
                    k += type_width(param['type'])
                    self.code.append(PushParam(param))
            call = Call(func=node.children[0].sym_entry)
            self.code.append(call)
            if k != 0:
                self.code.append(SetStack(k))
            if node.type != "void":
                dst = symbol_table.get_temp(node.type, self.table)
                self.code.append(PopParam(-type_width(node.type), dst))
            return dst

        elif node.name == "ReturnStmt":
            arg = self.generate_tac(node.children[0])
            self.code.append(Ret(value=arg))

        elif node.name == "FloatLiteral":
            return {'value': node.value, 'type': "int", 'arraylen': []}

        elif node.name == "IntegerLiteral":
            return {'value': node.value, 'type': "int", 'arraylen': []}

        elif node.name == "Boolean":
            if node.value == "true":
                goto = Jmp(cond='JMP', target=true_lbl)
            else:
                goto = Jmp(cond='JMP', target=false_lbl)
            self.code.append(goto)
            return {'value': node.value, 'type': "bool", 'arraylen': []}

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
