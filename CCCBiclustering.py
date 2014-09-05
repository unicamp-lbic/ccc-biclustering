__author__ = 'thalita'
import SuffixTree as st
from SymList import SymList

class CCCBiclustering(st.GeneralizedSuffixTree):
    def __init__(self, lines):
        string_set = __prepare_lines__(lines)
        # set st package constant
        st.POSITIVE_INFINITY = len(str(string_set)) - 1
        print 'building tree'
        # build tree (tree is self)
        st.GeneralizedSuffixTree.__init__(self, string_set)
        print 'finished building tree'

        print 'counting leaves'
        self.leaf_count()
        print 'finished counting leaves'

        valid_nodes = [True for i in range(len(self.nodes))]

        for v in self.leaf_nodes_idx():
            valid_nodes[v] = False
        for v in self.internal_nodes_idx():
            u = self.nodes[v].suffix_link
            # if v has a suffix link to u
            if u != None and u != -1:
                if self.nleaves[u] == self.nleaves[v]:
                    valid_nodes[u] = False
        valid_nodes[0] = False
        self.bicluster_nodes = [idx for idx, valid in enumerate(valid_nodes) if valid == True]
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        string = ''
        for node in self.bicluster_nodes:
            pattern = str(self.path_to_node(node))
            lines = str([l for l in self.strings_from_node(node)])
            string += 'Pattern: ' + pattern + ' Lines: ' + lines + '\n'
        return string



def __prepare_lines__(lines):
    # create string set from lines
    string_set = lines
    # append column numbers and term symbols
    for str_idx, string in enumerate(string_set):
        new_string = SymList()
        for idx,c in enumerate(string):
            new_string.append(SymList(c + str(idx+1)))
        term = SymList('$'+str(str_idx+1))
        new_string.append(term)
        string_set[str_idx] = new_string
    return string_set

if __name__ == '__main__':
    print 'Test 1'
    string_set = ['NUDUN', 'DUDUD', 'NNNUN', 'UUDUU']
    biclusters = CCCBiclustering(string_set)
    print biclusters

    print 'Test 2'
    test_file = './test_data/1500_Rows_50_Rows_50_Columns.txt'
    f = open(test_file,'r')
    lines=[]
    for idx, line in enumerate(f):
        lines.append('')
        for s in line.split()[1:]:
            lines[idx] += str(s)
    lines = lines[1:]

    b = CCCBiclustering(lines)
    f = open('result.txt','w')
    f.write(str(b))
    f.close()
