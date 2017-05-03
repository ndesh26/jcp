import copy

from parser_rules import symbol_table
from parser_rules import data
from symbol_table import type_width

class Ins(object):
    def __init__(self, label="", op=""):
        self.label = label
        self.op = op

class BinOp(Ins):
    def __init__(self, label="", op="", arg1=None, arg2=None, dst=None, arg1_addr=False, arg2_addr=False, dst_addr=False, arg1_pointer=False, arg2_pointer=False):
        Ins.__init__(self, label, op)
        self.arg1 = arg1
        self.arg2 = arg2
        self.dst = dst
        self.arg1_addr = arg1_addr
        self.arg2_addr = arg2_addr
        self.dst_addr = dst_addr
        self.arg1_pointer = arg1_pointer
        self.arg2_pointer = arg2_pointer

    def __repr__(self):
        if self.arg1_addr:
            arg1 = '&{}'.format(self.arg1['value'])
        elif self.arg1_pointer:
            arg1 = '*({})'.format(self.arg1['value'])
        else:
            arg1 = '{}'.format(self.arg1['value'])

        if self.arg2_addr:
            arg2 = '&{}'.format(self.arg2['value'])
        elif self.arg2_pointer:
            arg2 = '*({})'.format(self.arg2['value'])
        else:
            arg2 = '{}'.format(self.arg2['value'])

        if self.dst_addr:
            dst = '&{}'.format(self.dst['value'])
        else:
            dst = '{}'.format(self.dst['value'])
        return '\t' + dst + ' = ' + arg1 + ' ' + self.op + ' ' + arg2

    def __tox86__(self):
        if 'offset' in self.arg1.keys():
            if self.arg1_addr:
                source_1 = '\t' + 'mov eax, ebp' + ' ;' + self.__repr__()
                source_1 += '\n\t' + 'add eax, ' + '{}'.format(self.arg1['offset'])
            elif self.arg1_pointer:
                source_1 = '\n\t' + 'mov ebx, ' + ('[ebp{}]'.format(self.arg1['offset']) if self.arg1['offset'] < 0 else '[ebp+{}]'.format(self.arg1['offset'])) + ' ;' + self.__repr__()
                source_1 += '\n\tmov eax, [ebx]'
            else:
                source_1 = '\t' + 'mov eax, ' + ('[ebp{}]'.format(self.arg1['offset']) if self.arg1['offset'] < 0 else '[ebp+{}]'.format(self.arg1['offset'])) + ' ;' + self.__repr__()
        else:
            source_1 = '\t' + 'mov eax, ' + '{}'.format(self.arg1['value']) + ' ;' + self.__repr__()
        if 'offset' in self.arg2.keys():
            if self.arg2_addr:
                source_2 = '\t' + 'mov eax, ebp\n'
                source_2 += '\t' + 'add eax, ' + '{}'.format(self.arg2['offset'])
            elif self.arg2_pointer:
                source_2 = '\n\t' + 'mov ebx, ' + ('[ebp{}]'.format(self.arg2['offset']) if self.arg2['offset'] < 0 else '[ebp+{}]'.format(self.arg2['offset'])) + ' ;' + self.__repr__()
                source_2 += '\n\tmov ebx, [ebx]'
            else:
                source_2 = '\t' + 'mov ebx, ' + ('[ebp{}]'.format(self.arg2['offset']) if self.arg2['offset'] < 0 else '[ebp+{}]'.format(self.arg2['offset']))
        else:
            source_2 = '\t' + 'mov ebx, ' + '{}'.format(self.arg2['value'])
        op_map = {'+': 'add', '-': 'sub', '*': 'imul', '/': 'idiv'}
        if op_map[self.op] in ['imul', 'idiv']:
            operation = '\txor edx, edx'
            operation += '\n\t' + op_map[self.op] + ' ebx'
        else:
            operation = '\t' + op_map[self.op] + ' eax, ebx'
        store = '\t' + 'mov ' + ('[ebp{}], eax'.format(self.dst['offset']) if self.dst['offset'] < 0 else '[ebp+{}], eax'.format(self.dst['offset']))
        block = "\n".join([source_1, source_2, operation, store])
        return block

class UnaryOp(Ins):
    def __init__(self, label="", op="", arg=None, dst=None, arg_pointer=False, dst_pointer=False):
        Ins.__init__(self, label, op)
        self.arg = arg
        self.dst = dst
        self.arg_pointer = arg_pointer
        self.dst_pointer = dst_pointer

    def __repr__(self):
        if self.arg_pointer:
            arg = '*({})'.format(self.arg['value'])
        else:
            arg = '{}'.format(self.arg['value'])

        if self.dst_pointer:
            dst = '*({})'.format(self.dst['value'])
        else:
            dst = '{}'.format(self.dst['value'])
        return '\t' + dst + ' = ' + self.op + arg

    def __tox86__(self):
        if 'offset' in self.arg.keys():
            source = '\t' + 'mov eax, ' + ('[ebp{}]'.format(self.arg['offset']) if self.arg['offset'] < 0 else '[ebp+{}]'.format(self.arg['offset'])) + ' ;' + self.__repr__()
        else:
            source = '\t' + 'mov eax, ' + '{}'.format(self.arg['value'])
        if self.op == "-":
            neg = '\tneg eax'
        store = '\t' + 'mov ' + ('[ebp{}], eax'.format(self.dst['offset']) if self.dst['offset'] < 0 else '[ebp+{}], eax'.format(self.dst['offset']))
        block = "\n".join([source, neg, store])
        return block

class AssignOp(Ins):
    def __init__(self, label="", op="", arg=None, dst=None, arg_pointer=False, dst_pointer=False, arg_addr=False):
        Ins.__init__(self, label, op)
        self.arg = arg
        self.dst = dst
        self.arg_pointer = arg_pointer
        self.dst_pointer = dst_pointer
        self.arg_addr = arg_addr

    def __repr__(self):
        if self.arg_pointer:
            arg = '*({})'.format(self.arg['value'])
        elif self.arg_addr:
            arg = '&{}'.format(self.arg['value'])
        else:
            arg = '{}'.format(self.arg['value'])

        if self.dst_pointer:
            dst = '*({})'.format(self.dst['value'])
        else:
            dst = '{}'.format(self.dst['value'])
        return '\t' + dst + ' = ' + arg

    def __tox86__(self):
        if 'offset' in self.arg:
            value = self.arg['offset']
        value2= self.dst['offset']
        source = ''
        for i in range(0, min(type_width(self.arg), type_width(self.dst)), 4):
            if 'offset' in self.arg.keys():
                if self.arg_addr:
                    source += '\n\t' + 'mov eax, ebp' + ' ;' + self.__repr__()
                    source += '\n\t' + ('sub eax, {}'.format(-value-i) if (value+i)< 0 else 'mov eax, {}'.format(value+i))
                elif self.arg_pointer:
                    source += '\n\t' + 'mov ebx, ' + ('[ebp{}]'.format(value+i) if value+i < 0 else '[ebp+{}]'.format(value+i)) + ' ;' + self.__repr__()
                    source += '\n\tmov eax, [ebx]'
                else:
                    source += '\n\t' + 'mov eax, ' + ('[ebp{}]'.format(value+i) if value+i < 0 else '[ebp+{}]'.format(value+i))
            else:
                source += '\n\t' + 'mov eax, ' + '{}'.format(self.arg['value'])
                source += ' ;' + self.__repr__()

            if self.dst_pointer:
                source += '\n\t' + 'mov ' + ('ebx, [ebp{}]'.format(value2+i) if value2+i < 0 else 'ebx, [ebp+{}]'.format(value2+i))
                source += '\n\tmov [ebx], eax'
            else:
                source += '\n\t' + 'mov ' + ('[ebp{}], eax'.format(value2+i) if value2+i < 0 else '[ebp+{}], eax'.format(value2+i))
        return source

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
        save_ebp = '\tpush ebp' + ' ;' + self.__repr__()
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
        return ' ;' + self.__repr__() + '\n'

class PushParam(Ins):
    def __init__(self, param):
        Ins(self)
        self.param = param

    def __repr__(self):
        return '\tPushParam {}'.format(self.param['value'])

    def __tox86__(self):
        if 'offset' in self.param.keys():
            move = '\tmov eax, [ebp{}]'.format(self.param['offset']) if (self.param['offset']) < 0 else '\tmov eax, [ebp+{}]'.format(self.param['offset'])+ ' ;' + self.__repr__()
            move += '\n\tpush eax'
        else:
            if self.param['type'] == 'string':
                move = '\tmov eax, {}'.format(self.param['pointer'])
                move += '\n\tpush eax'
            else:
                move = '\tmov eax, {}'.format(self.param['value']) + ' ;' + self.__repr__()
                move += '\n\tpush eax'
        return move

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
        pop = '\tpop eax' + ' ;' + self.__repr__()
        store = '\tmov ' + ('[ebp{}], eax'.format(self.dst['offset']) if self.dst['offset'] < 0 else '[ebp+{}], eax'.format(self.dst['offset']))
        block = "\n".join([pop, store])
        return block

class SetStack(Ins):
    def __init__(self, change):
        Ins(self)
        self.change = change

    def __repr__(self):
        return '\tSetStack {}'.format(self.change)

    def __tox86__(self):
        update = '\tadd esp, {}'.format(self.change) + ' ;' + self.__repr__()
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
        return '\tcall {}'.format(self.func['value']) + ' ;' + self.__repr__()

class Cmp(Ins):
    def __init__(self, arg1, arg2, arg1_pointer=False, arg2_pointer=False):
        Ins(self)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg1_pointer = arg1_pointer
        self.arg2_pointer = arg2_pointer

    def __repr__(self):
        if self.arg1_pointer:
            arg1 = '*({})'.format(self.arg1['value'])
        else:
            arg1 = '{}'.format(self.arg1['value'])
        if self.arg2_pointer:
            arg2 = '*({})'.format(self.arg2['value'])
        else:
            arg2 = '{}'.format(self.arg2['value'])
        return '\tCMP {}, {}'.format(arg1, arg2)

    def __tox86__(self):
        if 'offset' in self.arg1.keys():
            if self.arg1_pointer:
                source_1 = '\t' + 'mov ebx, ' + ('[ebp{}]'.format(self.arg1['offset']) if self.arg1['offset'] < 0 else '[ebp+{}]'.format(self.arg1['offset'])) + ' ;' + self.__repr__()
                source_1 += '\n\tmov eax, [ebx]'
            else:
                source_1 = '\t' + 'mov eax, ' + ('[ebp{}]'.format(self.arg1['offset']) if self.arg1['offset'] < 0 else '[ebp+{}]'.format(self.arg1['offset'])) + ' ;' + self.__repr__()
        else:
            source_1 = '\t' + 'mov eax, ' + '{}'.format(self.arg1['value']) + ' ;' + self.__repr__()
        if 'offset' in self.arg2.keys():
            if self.arg2_pointer:
                source_2 = '\t' + 'mov ecx, ' + ('[ebp{}]'.format(self.arg2['offset']) if self.arg2['offset'] < 0 else '[ebp+{}]'.format(self.arg2['offset'])) + ' ;' + self.__repr__()
                source_2 += '\n\tmov ebx, [ecx]'
            else:
                source_2 = '\t' + 'mov ebx, ' + ('[ebp{}]'.format(self.arg2['offset']) if self.arg2['offset'] < 0 else '[ebp+{}]'.format(self.arg2['offset']))
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
        return '\t' + jump_map[self.cond] + ' ' + self.target + ' ;' + self.__repr__()

class Ret(Ins):
    def __init__(self, value, arg_size):
        Ins(self)
        self.value = value
        self.arg_size = arg_size

    def __repr__(self):
        if not self.value:
            return '\tReturn'
        else:
            return '\tReturn {}'.format(self.value['value'])

    def __tox86__(self):
        if self.value:
            if 'offset' in self.value:
                move = '\tmov eax, ' + ('[ebp{}]'.format(self.value['offset']) if self.value['offset'] < 0 else '[ebp+{}]'.format(self.value['offset'])) + ' ;' + self.__repr__()
            else:
                move = '\tmov eax, {}'.format(self.value['value']) + ' ;' + self.__repr__()
            move += '\n\tmov [ebp+{}], eax'.format(self.arg_size+8)
            frame_deallocate = '\tmov esp, ebp'
            remove = '\tpop ebp'
            ret = '\tret'
            block = "\n".join([move, frame_deallocate, remove, ret])
        else:
            frame_deallocate = '\tmov esp, ebp' + ' ;' + self.__repr__()
            remove = '\tpop ebp'
            ret = '\tret'
            block = "\n".join([frame_deallocate, remove, ret])
        return block

class Tac(object):
    def __init__(self):
        self.code = []
        self.table = None # represents the table of currently processing funtion

    def generate_tac(self, node, parent=None, true_lbl=None, false_lbl=None, end_lbl=None, start_lbl=None):
        if node.name == "BinaryOperator":
            if node.value == "=":
                if node.children[0].name in ["ArrayAccess", "FieldAccessExpr"]:
                    dst_pointer = True
                else:
                    dst_pointer = False

                if node.children[1].name  in ["ArrayAccess", "FieldAccessExpr"]:
                    arg_pointer = True
                else:
                    arg_pointer = False
                arg1 = self.generate_tac(node.children[0])
                arg2 = self.generate_tac(node.children[1])
                assignop = AssignOp(arg=arg2, dst=arg1, dst_pointer=dst_pointer, arg_pointer=arg_pointer)
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
                if node.children[0].name  in ["ArrayAccess", "FieldAccessExpr"]:
                    arg1_pointer = True
                else:
                    arg1_pointer = False

                if node.children[1].name  in ["ArrayAccess", "FieldAccessExpr"]:
                    arg2_pointer = True
                else:
                    arg2_pointer = False

                cmp = Cmp(arg1=arg1, arg2=arg2, arg1_pointer=arg1_pointer, arg2_pointer=arg2_pointer)
                self.code.append(cmp)
                cond_map = {'<': 'JL', '>': 'JG', '>=': 'JGE', '<=': 'JLE', '==': 'JE', '!=': 'JNE'}
                true_jmp = Jmp(cond=cond_map[node.value], target=true_lbl)
                self.code.append(true_jmp)
                goto_false = Jmp(cond='JMP', target=false_lbl)
                self.code.append(goto_false)

            else:
                if node.children[0].name in ["ArrayAccess", "FieldAccessExpr"]:
                    arg1_pointer = True
                else:
                    arg1_pointer = False

                if node.children[1].name  in ["ArrayAccess", "FieldAccessExpr"]:
                    arg2_pointer = True
                else:
                    arg2_pointer = False

                arg1 = self.generate_tac(node.children[0])
                arg2 = self.generate_tac(node.children[1])
                dst = symbol_table.get_temp(node.type, self.table)
                binop = BinOp(op=node.value, arg1=arg1, arg2=arg2, dst=dst, arg1_pointer=arg1_pointer, arg2_pointer=arg2_pointer)

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

        elif node.name == "ArrayInitialization":
            dst = symbol_table.get_temp(node.type, self.table)
            arg = self.generate_tac(node.children[0])
            assignop = AssignOp(arg=arg, dst=dst)
            self.code.append(assignop)
            return dst

        elif node.name == "VarDecl":
            if node.children and node.children[0].name == "InitListExpr":
                arg1 = node.sym_entry
                arg = self.generate_tac(node.children[0].children[0])
                assignop = AssignOp(arg=arg, dst=dst)
                self.code.append(assignop)
                index = symbol_table.get_temp(node.type, self.table)
                indexop = AssignOp(arg=arg1, dst=index, arg_addr=True)
                self.code.append(indexop)
                self.generate_tac(node.children[0], parent=index)

            elif node.children and  node.children[0].name == "ArrayInitialization":
                dst = node.sym_entry
                arg = self.generate_tac(node.children[0].children[0])
                assignop = AssignOp(arg=arg, dst=dst)
                self.code.append(assignop)
                if len(node.children[0].children) == 2:
                    self.generate_tac(node.children[0].children[1], parent=arg)

            elif node.children and node.children[0].name is not "ArrayInitialization":
                arg1 = node.sym_entry
                arg2 = self.generate_tac(node.children[0])
                if node.children[0].name  in ["ArrayAccess", "FieldAccessExpr"]:
                    arg_pointer = True
                else:
                    arg_pointer = False
                assignop = AssignOp(arg=arg2, dst=arg1, arg_pointer=arg_pointer)
                self.code.append(assignop)

        elif node.name == "InitListExpr":
            if node.children[0].name is not "InitListExpr":
                size = {'value': type_width(node.children[0].type), 'type': node.children[0].type, 'arraylen': []}
                for child in node.children:
                    arg2 = self.generate_tac(child)
                    assignop = AssignOp(arg=arg2, dst=parent, dst_pointer=True)
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
                arg1 = self.generate_tac(node.children[1], end_lbl=end_lbl, start_lbl=start_lbl)
                end = Label(label=if_next_lbl+":")
                self.code.append(end)
            else:
                if_true_lbl = symbol_table.get_target()
                if_false_lbl = symbol_table.get_target()
                if_next_lbl = symbol_table.get_target()
                arg1 = self.generate_tac(node.children[0], true_lbl=if_true_lbl, false_lbl=if_false_lbl)
                true_label = Label(label=if_true_lbl+":")
                self.code.append(true_label)
                arg1 = self.generate_tac(node.children[1], end_lbl=end_lbl, start_lbl=start_lbl)
                goto = Jmp(cond='JMP', target=if_next_lbl)
                self.code.append(goto)
                false_label = Label(label=if_false_lbl+":")
                self.code.append(false_label)
                arg1 = self.generate_tac(node.children[2], end_lbl=end_lbl, start_lbl=start_lbl)
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
            for_update_label = symbol_table.get_target()
            for_true_label = symbol_table.get_target()
            for_false_label = symbol_table.get_target()
            for_cond = Label(label=for_cond_label+":")
            self.code.append(for_cond)
            self.generate_tac(node.children[1], true_lbl=for_true_label, false_lbl=for_false_label)
            for_true = Label(label=for_true_label+":")
            self.code.append(for_true)
            self.generate_tac(node.children[3],
                              end_lbl=for_false_label, start_lbl=for_update_label)
            for_update = Label(label=for_update_label+":")
            self.code.append(for_update)
            self.generate_tac(node.children[2])
            goto_cond = Jmp(cond='JMP', target=for_cond_label)
            self.code.append(goto_cond)
            for_false = Label(label=for_false_label+":")
            self.code.append(for_false)

        elif node.name == "DoWhileStmt":
            while_true_lbl = symbol_table.get_target()
            while_next_lbl = symbol_table.get_target()
            begin_label = Label(label=while_true_lbl+":")
            self.code.append(begin_label)
            self.generate_tac(node.children[0], true_lbl=while_true_lbl, false_lbl=while_next_lbl)
            self.generate_tac(node.children[1], true_lbl=while_true_lbl, false_lbl=while_next_lbl)
            next_label = Label(label=while_next_lbl+":")
            self.code.append(next_label)

        elif node.name == "SwitchStmt":
            arg1 = self.generate_tac(node.children[0])
            switch_end_lbl = symbol_table.get_target()
            switch_next_lbl = symbol_table.get_target()
            for case in node.children[1:]:
                arg2 = self.generate_tac(case.children[0])
                if case.name != "DefaultStmt":
                    if node.children[0].name  in ["ArrayAccess", "FieldAccessExpr"]:
                        arg1_pointer = True
                    else:
                        arg1_pointer = False

                    if node.children[1].name  in ["ArrayAccess", "FieldAccessExpr"]:
                        arg2_pointer = True
                    else:
                        arg2_pointer = False

                    cmp = Cmp(arg1=arg1, arg2=arg2, arg1_pointer=arg1_pointer, arg2_pointer=arg2_pointer)
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

        elif node.name == "ConstrDecl":
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
                    if node.children[i].name  in ["ArrayAccess", "FieldAccessExpr"]:
                        arg_pointer = True
                        dst = symbol_table.get_temp(param['type'], self.table)
                        assignop = AssignOp(arg=param, dst=dst, arg_pointer=True)
                        self.code.append(assignop)
                        param = dst
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

        elif node.name == "CharLiteral":
            return {'value': ord(node.value[1]), 'type': "char", 'arraylen': []}

        elif node.name == "StringLiteral":
            return {'value': node.value, 'type': "string", 'arraylen': [], 'pointer': node.sym_entry}

        elif node.name == "Null":
            return {'value': 0, 'arraylen': [], 'type': ""}

        elif node.name == "Boolean":
            if node.value == "true":
                if true_lbl:
                    goto = Jmp(cond='JMP', target=true_lbl)
                    self.code.append(goto)
                node.value = 1
            elif node.value == "false":
                if false_lbl:
                    goto = Jmp(cond='JMP', target=false_lbl)
                    self.code.append(goto)
                node.value = 0
            return {'value': node.value, 'type': "boolean", 'arraylen': []}

        elif node.name == "DeclsRefExpr":
            return node.sym_entry

        elif node.name == "FieldAccessExpr":
            arg = self.generate_tac(node.children[0])
            dst = symbol_table.get_temp('int', self.table)
            arg1_addr = False
            if node.children[0].name in ["ArrayAccess", "FieldAccessExpr"]:
                arg1_addr = True
            binop = BinOp(op="+", arg1=arg, arg2={'value': node.sym_entry['offset'], 'type': "int", 'arraylen': []}, dst=dst, arg1_pointer=arg1_addr)
            self.code.append(binop)
            return dst

        elif node.name == "ArrayAccess":
            arg1 = self.generate_tac(node.children[0])
            index = self.generate_tac(node.children[1])
            size = type_width(node.type)
            length = len(node.arraylen)- node.dims
            for i in node.arraylen[length:]:
                size *= i
            dst = symbol_table.get_temp('int', self.table)
            multi = BinOp(op="*", arg1={'value': size, 'type': "int", 'arraylen': []}, arg2=index, dst=dst)
            arg1_pointer = False
            if node.children[0].name in ["FieldAccessExpr"]:
                arg1_pointer = True

            binop = BinOp(op="+", arg1=arg1, arg2=dst, dst=dst, arg1_pointer=arg1_pointer)
            self.code.append(multi)
            self.code.append(binop)
            return dst

        elif node.name == "ClassInstantiation":
            dst = symbol_table.get_temp(node.type, self.table)
            arg = self.generate_tac(node.children[0])
            assignop = AssignOp(arg=arg, dst=dst)
            self.code.append(assignop)
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
        print('section .data')
        for label in data:
            print('{} db {},0'.format(label, data[label]))

