# -*- coding: utf-8 -*-


def context_property(name):

    def getter(self):
        return getattr(self.context, name)

    def setter(self, value):
        setattr(self.context, name, value)

    def deleter(self):
        delattr(self.context, name)

    return property(getter, setter, deleter)
