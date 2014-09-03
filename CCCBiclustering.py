__author__ = 'thalita'
import SuffixTree as st
from SymList import SymList

class CCCBiclustering(st.GeneralizedSuffixTree):
    def __init__(self, lines):
        string_set = __prepare_lines__(lines)
        # set st package constant
        st.POSITIVE_INFINITY = len(str(string_set)) - 1
        # build tree (tree is self)
        st.GeneralizedSuffixTree.__init__(self, string_set)

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

    def pprint(self):
        for node in self.bicluster_nodes:
            pattern = str(self.path_to_node(node))
            lines = str([l for l in self.strings_from_node(node)])
            print 'N' + str(node) + ': ' + pattern + ': ' + lines



def __prepare_lines__(lines):
    # create string set from lines
    string_set = lines
    # append column numbers and term symbols
    for str_idx, string in enumerate(string_set):
        new_string = ''
        for idx,c in enumerate(string):
            new_string += c + str(idx+1)
        new_string = SymList(new_string,2)
        term = SymList('$'+str(str_idx+1))
        new_string.append(term)
        string_set[str_idx] = new_string
    return string_set

if __name__ == '__main__':
    string_set = ['NUDUN', 'DUDUD', 'NNNUN', 'UUDUU']
    biclusters = CCCBiclustering(string_set)
    biclusters.pprint()
    biclusters.pprint_tree()
    print biclusters.strings_from_node(20)
