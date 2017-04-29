#!/usr/bin/env python

# Symbol Table

import csv

width = {'int':4, 'float':8, 'short':4, 'long':8, 'double':8, 'char':4, 'string': 4}
temp_no = 0
target_no = 0

def type_width(name):
    global width
    if (isinstance(name, str)):
        if name in width:
            return width[name]
        else:
            return 0
    else:
        if (name["type"] in width):
            if name['arraylen'] == []:
                return width[name["type"]]
            else:
                size = 1
                for i in name['arraylen']:
                    size *= i
                size *= width[name["type"]]
                return size
        elif "(" in name["type"]:
            return 4
        else:
            if "width" in name:
                if name['arraylen'] == []:
                    return name["width"]
                else:
                    size = 1
                    for i in name['arraylen']:
                        size *= i
                    size *= name["width"]
                    return size
            return 0

class Table:
    def __init__(self, parent=None, name=None, category=None):
        self.entries = {}
        self.parent_table = parent
        self.name = name
        self.category = category
        self.width = 0
        self.arg_size = 0
        self.args = True

    def lookup(self, name):
        if name in self.entries:
            return True
        else:
            return False

    def lookup_all(self, name):
        current_table = self
        while(current_table != None):
            if current_table.lookup(name):
                return True
            current_table = current_table.parent_table
        return False

    def get_entry(self, name):
        if self.lookup(name):
            return self.entries[name]
        else:
            return None

    def get_method_entry(self, name):
        current_table = self
        while(current_table != None):
            if current_table.lookup(name):
                return current_table.entries[name]
            current_table = current_table.parent_table
        return None

    def insert(self, name, attributes={}):
        attributes['offset'] = self.width
        self.entries[name] = attributes
        self.width = self.width + type_width(self.entries[name])
        if self.args:
            self.arg_size = self.arg_size + type_width(self.entries[name])
        return self.entries[name]

    def print_table(self, file):
        if file:
            with open(file, 'w') as csvfile:
                list = ['Name', 'Type', 'Array Length', 'Modifiers', 'Dims']
                wr = csv.writer(csvfile, delimiter=',')
                wr.writerow(list)
                for key, value in self.entries.items():
                    d = {
                            'Name': key,
                            'Type': self.entries[key].get('type'),
                            'Array Length': self.entries[key].get('arraylen'),
                            'Modifiers': self.entries[key].get('modifiers'),
                            'Dims': self.entries[key].get('dims'),
                            }
                    fields = ('Name', 'Type', 'Array Length', 'Modifiers', 'Dims')
                    cwriter = csv.DictWriter(csvfile, fields, delimiter=',')
                    cwriter.writerow(d)
        else:
            print("File name not given")

    def remove(self, name):
        self.entries.pop(name, None)

    def get_width(self):
        return self.width;

    def args_completed(self):
        self.args = False

    def get_arg_size(self):
        return self.arg_size

class SymbolTable:

    def __init__(self):
        self.table = Table()
        self.classes = {}

    def begin_scope(self, name = "", category = ""):
        new_table = Table(self.table, name, category)
        self.table = new_table
        return self.table

    def end_scope(self):
        self.table = self.table.parent_table

    def get_entry(self, name):
        return self.table.get_method_entry(name)

    def get_entry_in_method(self, name):
        current_table = self.table
        while(current_table != None):
            if current_table.category == "method":
                return current_table.get_entry(name)
            current_table = current_table.parent_table
        return None

    def get_width(self):
        return self.table.get_width()

    def insert(self, name, attributes={}):
        if type_width(attributes) == 0:
            attributes['width'] = self.get_class_width(attributes['type'])
        return self.table.insert(name, attributes)

    def print_table(self, file):
        self.table.print_table(file)

    def insert_class(self, name):
        self.classes[name] = self.table

    def lookup_class(self, name):
        if name in self.classes:
            return True
        else:
            return False

    def get_class_width(self, name):
        return self.classes[name].get_width();

    def lookup_method(self, name, method):
        if self.classes[name].lookup(method):
            return self.classes[name].entries[method]
        else:
            return None

    def insert_up(self, name, attributes={}):
        attributes['table'] = self.table;
        return self.table.parent_table.insert(name, attributes)

    def get_name(self):
        return (self.table.name, self.table.category)

    def get_class_name(self):
        current_table = self.table
        while(current_table != None):
            if current_table.category == "class":
                return current_table.name
            current_table = current_table.parent_table
        return None

    def get_method_return_type(self):
        current_table = self.table
        while(current_table != None):
            if current_table.category == "method":
                return current_table.parent_table.get_entry(current_table.name)['type'].split(" ", 1)[0]
            current_table = current_table.parent_table
        return None

    def remove(self, name):
        self.table.remove(name)

    def get_temp(self, type, table=None):
        global temp_no
        name = '_t' + str(temp_no)
        temp_no += 1
        if table == None:
            entry = self.table.insert(name, {'value': name, 'type' : type, 'arraylen': []})
            entry['offset'] = self.table.get_arg_size() - entry['offset'] - type_width(entry)
            return entry
        else:
            entry = table.insert(name, {'value': name, 'type' : type, 'arraylen': []})
            entry['offset'] = table.get_arg_size() - entry['offset'] - type_width(entry)
            return entry

    def get_target(self):
        global target_no
        target = '_L' + str(target_no)
        target_no += 1
        return target

    def args_completed(self):
        self.table.args_completed();

    def get_arg_size(self):
        return self.table.get_arg_size()
