class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)
    def get(self, adict):
        return adict



