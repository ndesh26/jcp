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

    def print(self, file):
        for entry in self.entries:
            file.write("Nayan ludo")
            file.write(entry[name])
