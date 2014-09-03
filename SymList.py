__author__ = 'thalita'

class SymList():
    def __init__(self, string='',  charPerSymbol = None):
        self.list = []
        if string == '':
            pass
        # If no charPerSymbol was informed, put whole string as one element
        elif charPerSymbol == None:
            self.list.append(string)
        else:
            if len(string) % charPerSymbol:
                print 'String of lenght %d is not divisable in %d char symbols' % (len(string),charPerSymbol)
                raise ValueError

            i=0
            while i < len(string):
                self.list.append(string[i:i+2])
                i+=charPerSymbol

    def strlen(self):
        return len(str(self))

    def __len__(self):
        return len(self.list)


    def __str__(self):
        str = ''
        for elem in self.list:
            str += elem
        return str

    def __add__(self,s):
        return self.list + s.list

    def append(self, s):
        self.list = self.list + s.list
    
    def __repr__(self):
         return self.__str__()
        
    def __eq__(self, s):
        return self.list==s.list

    def __getitem__(self, key):
        return self.list[key]


def SymListTest():
    str1 = 'abacates'
    str1 = SymList(str1,2)
    str2 = SymList('bola',2)
    print str1+str2
    str1.append(str2)

    print str1

if __name__ == '__main__':
    SymListTest()
