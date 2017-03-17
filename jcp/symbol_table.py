#!/usr/bin/env python

# Symbol Table

class Table:
    def __init__(self, parent=None):
        self.entries = {}
        self.parent_table = parent

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
        self.entries[name] = attributes
        return self.entries[name]

    def print_table(self):
        for key, value in self.entries.items():
            print(key)
            print(value)

class SymbolTable:

    def __init__(self):
        self.table = Table()

    def begin_scope(self):
        new_table = Table(self.table)
        self.table = new_table
        return self.table

    def end_scope(self):
        self.table = self.table.parent_table

    def get_entry(self, name):
        return self.table.get_method_entry(name)

    def insert(self, name, attributes={}):
        return self.table.insert(name, attributes)

    def print_table(self):
        self.table.print_table()
