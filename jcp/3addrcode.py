import copy

from parser_rules import symbol_table
from symbol_table import type_width

class Ins(object):
    def __init__(self, label="", op=""):
        self.label = label
        self.op = op

class BinOp(Ins):
    def __init__(self, label="", op="", arg1=None, arg2=None, dst=None, arg1a=False, arg2a=False, dsta=False):
        Ins.__init__(self, label, op)
        self.arg1 = arg1
        self.arg2 = arg2
        self.dst = dst
        self.arg1a = arg1a
        self.arg2a = arg2a
        self.dsta = dsta

    def __repr__(self):
        if self.arg1a:
            arg1 = '&{}'.format(self.arg1['value'])
        else:
            arg1 = '{}'.format(self.arg1['value'])

        if self.arg2a:
            arg2 = '&{}'.format(self.arg2['value'])
        else:
            arg2 = '{}'.format(self.arg2['value'])

        if self.dsta:
            dst = '&{}'.format(self.dst['value'])
        else:
            dst = '{}'.format(self.dst['value'])
        return '\t' + dst + ' = ' + arg1 + ' ' + self.op + ' ' + arg2

    def __tox86__(self):
        if 'offset' in self.arg1.keys():
            if self.arg1a:
                source_1 = '\t' + 'mov eax, ebp\n'
                source_1 += '\t' + 'add eax, ' + '{}'.format(self.arg1['offset'])
            else:
                source_1 = '\t' + 'mov eax, ' + '[ebp{}]'.format(self.arg1['offset']) if self.arg1['offset'] < 0 else '[ebp+{}]'.format(self.arg1['offset'])
        else:
            source_1 = '\t' + 'mov eax, ' + '{}'.format(self.arg1['value'])
        if 'offset' in self.arg2.keys():
            source_2 = '\t' + 'mov ebx, ' + '[ebp{}]'.format(self.arg2['offset']) if self.arg2['offset'] < 0 else '[ebp+{}]'.format(self.arg2['offset'])
        else:
            source_2 = '\t' + 'mov ebx, ' + '{}'.format(self.arg2['value'])
        op_map = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div'}
        operation = '\t' + op_map[self.op] + ' eax, ebx'
        store = '\t' + 'mov ' + '[ebp{}], eax'.format(self.dst['offset']) if self.dst['offset'] < 0 else '[ebp+{}], eax'.format(self.dst['offset'])
        block = "\n".join([source_1, source_2, operation, store])
        return block

class UnaryOp(Ins):
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
        return '\t' + dst + ' = ' + self.op + arg

    def __tox86__(self):
        if 'offset' in self.arg.keys():
            source = '\t' + 'mov eax, ' + '[ebp{}]'.format(self.arg['offset']) if self.arg['offset'] < 0 else '[ebp+{}]'.format(self.arg['offset'])
        else:
            source = '\t' + 'mov eax, ' + '{}'.format(self.arg['value'])
        if self.op == "-":
            neg = '\tneg eax'
        store = '\t' + 'mov ' + '[ebp{}], eax'.format(self.dst['offset']) if self.dst['offset'] < 0 else '[ebp+{}], eax'.format(self.dst['offset'])
        block = "\n".join([source, neg, store])
        return block

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

    def __tox86__(self):
        if 'offset' in self.arg.keys():
            source = '\t' + 'mov eax, ' + '[ebp{}]'.format(self.arg['offset']) if self.arg['offset'] < 0 else '[ebp+{}]'.format(self.arg['offset'])
        else:
            source = '\t' + 'mov eax, ' + '{}'.format(self.arg['value'])
        store = '\t' + 'mov ' + '[ebp{}], eax'.format(self.dst['offset']) if self.dst['offset'] < 0 else '[ebp+{}], eax'.format(self.dst['offset'])
        block = "\n".join([source, store])
        return block

class Label(Ins):
    def __init__(self, label=""):
        Ins.__init__(self, label)

    def __repr__(self):
        return self.label

    def __tox86__(self):
        return self.label

class BeginFunc(Ins):
    def __init__(self, width=0):
        Ins(self)
        self.width = width

    def __repr__(self):
        return '\tBeginFunc {}'.format(self.width)

    def __tox86__(self):
        save_ebp = '\tpush ebp'
        update = '\tmov ebp, esp'
        frame_allocate = '\tsub esp, {}'.format(self.width)
        block = "\n".join([save_ebp, update, frame_allocate])
        return block

class EndFunc(Ins):
    def __init__(self):
        Ins(self)

    def __repr__(self):
        return '\tEndFunc'

    def __tox86__(self):
        frame_deallocate = '\tmov esp, ebp'
        remove = '\tpop ebp'
        ret = '\tret'
        block = "\n".join([frame_deallocate, remove, ret])
        return block

class PushParam(Ins):
    def __init__(self, param):
        Ins(self)
        self.param = param

    def __repr__(self):
        return '\tPushParam {}'.format(self.param['value'])

    def __tox86__(self):
        if 'offset' in self.param.keys():
            move = '\tmov eax, ' + '[ebp{}]'.format(self.param['offset']) if self.param['offset'] < 0 else '[ebp+{}]'.format(self.param['offset'])
        else:
            move = '\tmov eax, {}'.format(self.param['value'])
        push = '\tpush eax'
        block = "\n".join([move, push])
        return block

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

    def __tox86__(self):
        pop = '\tpop eax'
        store = '\tmov ' + '[ebp{}], eax'.format(self.dst['offset']) if self.dst['offset'] < 0 else '[ebp+{}], eax'.format(self.dst['offset'])
        block = "\n".join([pop, store])
        return block

class SetStack(Ins):
    def __init__(self, change):
        Ins(self)
        self.change = change

    def __repr__(self):
        return '\tSetStack {}'.format(self.change)

    def __tox86__(self):
        update = '\tadd esp, {}'.format(self.change)
        block = "\n".join([update])
        return block

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

    def __tox86__(self):
        return '\tcall {}'.format(self.func['value'])

class Cmp(Ins):
    def __init__(self, arg1, arg2):
        Ins(self)
        self.arg1 = arg1
        self.arg2 = arg2

    def __repr__(self):
        return '\tCMP {}, {}'.format(self.arg1['value'], self.arg2['value'])

    def __tox86__(self):
        if 'offset' in self.arg1.keys():
            source_1 = '\t' + 'mov eax, ' + '[ebp{}]'.format(self.arg1['offset']) if self.arg1['offset'] < 0 else '[ebp+{}]'.format(self.arg1['offset'])
        else:
            source_1 = '\t' + 'mov eax, ' + '{}'.format(self.arg1['value'])
        if 'offset' in self.arg2.keys():
            source_2 = '\t' + 'mov ebx, ' + '[ebp{}]'.format(self.arg2['offset']) if self.arg2['offset'] < 0 else '[ebp+{}]'.format(self.arg2['offset'])
        else:
            source_2 = '\t' + 'mov ebx, ' + '{}'.format(self.arg2['value'])
        compare = '\t' + 'cmp eax, ebx'
        block = "\n".join([source_1, source_2, compare])
        return block

class Jmp(Ins):
    def __init__(self, cond, target):
        Ins(self)
        self.cond = cond
        self.target = target

    def __repr__(self):
        return '\t{} {}'.format(self.cond, self.target)

    def __tox86__(self):
        jump_map = {'JL': 'jl', 'JG': 'jg', 'JGE': 'jge', 'JLE': 'jle', 'JE': 'je', 'JNE': 'jne', 'JMP': 'jmp'}
        return '\t' + jump_map[self.cond] + ' ' + self.target

class Ret(Ins):
    def __init__(self, value, arg_size):
        Ins(self)
        self.value = value
        self.arg_size = arg_size

    def __repr__(self):
        return '\tReturn {}'.format(self.value['value'])

    def __tox86__(self):
        if 'offset' in self.value:
            move = '\tmov eax, [ebp{}]'.format(self.value['offset'])
        else:
            move = '\tmov eax, {}'.format(self.value['value'])
        move += '\n\tmov [ebp+{}], eax'.format(self.arg_size+8)
        return move

class Tac(object):
    def __init__(self):
        self.code = []
        self.table = None # represents the table of currently processing funtion

    def generate_tac(self, node, parent=None, true_lbl=None, false_lbl=None, end_lbl=None, start_lbl=None):
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
            if "post" in node.value:
                arg = self.generate_tac(node.children[0])
                dst = symbol_table.get_temp(node.type, self.table)
                assignop = AssignOp(arg=arg, dst=dst)
                self.code.append(assignop)
                dst2 = symbol_table.get_temp(node.type, self.table)
                binop = BinOp(op=node.value[-1], arg1=arg, arg2={'value':1, 'type': 'int', 'arraylen': []}, dst=dst2)
                self.code.append(binop)
                assignop = AssignOp(arg=dst2, dst=arg)
                self.code.append(assignop)
                return dst

            if "pre" in node.value:
                arg = self.generate_tac(node.children[0])
                dst = symbol_table.get_temp(node.type, self.table)
                binop = BinOp(op=node.value[-1], arg1=arg, arg2={'value':1, 'type': 'int', 'arraylen': []}, dst=dst)
                self.code.append(binop)
                assignop = AssignOp(arg=dst, dst=arg)
                self.code.append(assignop)
                return dst

            if node.value == "!":
                arg1 = self.generate_tac(node.children[0], true_lbl=false_lbl, false_lbl=true_lbl)

            if node.value == "-":
                arg1 = self.generate_tac(node.children[0])
                dst = symbol_table.get_temp(node.type, self.table)
                unaryop = UnaryOp(op="-", arg=arg1, dst=dst)
                self.code.append(unaryop)
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
                self.code.append(false_label)
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
            self.generate_tac(node.children[1],
                              end_lbl=while_next_lbl, start_lbl=while_begin_lbl)
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
            self.generate_tac(node.children[3],
                              end_lbl=for_false_label, start_lbl=for_cond_label)
            self.generate_tac(node.children[2])
            goto_cond = Jmp(cond='JMP', target=for_cond_label)
            self.code.append(goto_cond)
            for_false = Label(label=for_false_label+":")
            self.code.append(for_false)

        elif node.name == "SwitchStmt":
            arg1 = self.generate_tac(node.children[0])
            switch_end_lbl = symbol_table.get_target()
            switch_next_lbl = symbol_table.get_target()
            for case in node.children[1:]:
                arg2 = self.generate_tac(case.children[0])
                if case.name != "DefaultStmt":
                    cmp = Cmp(arg1=arg1, arg2=arg2)
                    self.code.append(cmp)
                    goto_cond = Jmp(cond='JNE', target=switch_next_lbl)
                    self.code.append(goto_cond)
                if len(case.children) > 1 and case.name != "DefaultStmt":
                    self.generate_tac(case.children[1], end_lbl=switch_end_lbl)
                elif case.name != "DefaultStmt":
                    self.generate_tac(case.children[0], end_lbl=switch_end_lbl)
                if case.name != "DefaultStmt":
                    switch_next = Label(label=switch_next_lbl+":")
                    self.code.append(switch_next)
                    switch_next_lbl = symbol_table.get_target()
            switch_end = Label(label=switch_end_lbl+":")
            self.code.append(switch_end)


        elif node.name == "BreakStmt":
            goto_cond = Jmp(cond='JMP', target=end_lbl)
            self.code.append(goto_cond)

        elif node.name == "ContinueStmt":
            goto_cond = Jmp(cond='JMP', target=start_lbl)
            self.code.append(goto_cond)

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
            self.code.append(Ret(value=arg, arg_size=self.table.get_arg_size()))

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

        elif node.name == "FieldAccessExpr":
            arg = self.generate_tac(node.children[0])
            field = copy.deepcopy(node.sym_entry)
            field['value'] = arg['value'] + '.' + field['value']
            field['offset'] += arg['offset']
            return field

        elif node.name == "ArrayAccess":
            arg1 = self.generate_tac(node.children[0])
            index = self.generate_tac(node.children[1])
            size = type_width(node.type)
            if size == 0:
                size = symbol_table.get_class_width(node.type)
            length = len(node.arraylen)- node.dims
            for i in node.arraylen[length:]:
                size *= i
            dst = symbol_table.get_temp(node.type, self.table)
            multi = BinOp(op="*", arg1={'value': size, 'type': "int", 'arraylen': []}, arg2=index, dst=dst)
            binop = BinOp(op="+", arg1=arg1, arg2=dst, dst=dst, arg1a=True)
            self.code.append(multi)
            self.code.append(binop)
            return dst

        else:
            for n in node.children:
                self.generate_tac(n, true_lbl=true_lbl, false_lbl=false_lbl, end_lbl=end_lbl, start_lbl=start_lbl);

    def print_tac(self):
        for ins in self.code:
            print(repr(ins))

    def print_x86(self):
        for ins in self.code:
            print(ins.__tox86__())
