__author__ = 'thalita'
import SuffixTree as st
from SymList import SymList
import numpy as np
from sklearn.preprocessing import scale


class CCCBiclustering(st.GeneralizedSuffixTree):
    def __init__(self, lines):
        string_set = __prepare_lines__(lines)
        # set st package constant
        st.POSITIVE_INFINITY = len(str(string_set)) - 1
        print 'building tree'
        # build tree (tree is self)
        st.GeneralizedSuffixTree.__init__(self, string_set)

        print 'counting leaves'
        self.leaf_count()

        valid_nodes = [True for i in range(len(self.nodes))]
        # no leaf node can be a bicluster
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
        self.p_values = {}
        self.filtered_nodes = {}
        self.ncols = self.num_cols()
        self.nlines = self.num_lines()

        print 'Done!'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.bicluster_info(self.bicluster_nodes)

    def compute_p_values(self, nodes=None):
        if nodes == None:
            nodes = self.bicluster_nodes
        for node in nodes:
            pattern = self.path_to_node(node)
            total_lines = len(self.strings)
            if self.ncols[node] == 1:
                count = self.count_occurrences(pattern[0:1])
                self.p_values[node] = count/float(total_lines)
            else:
                single_count = [total_lines]
                for i in range(len(pattern[0:-1])):
                    count = self.count_occurrences(pattern[i:i+1])
                    single_count.append(count)

                pair_count = [single_count[1]]
                for i in range(0, len(pattern)-2+1):
                    count = self.count_occurrences(pattern[i:i+2])
                    pair_count.append(count)
                probs = [x/float(y) for x, y in zip(pair_count, single_count)]
                self.p_values[node] = reduce(lambda x,y : x*y, probs)



    def bicluster_info(self, nodes):
        string = ''
        for node in nodes:
            pattern = self.path_to_node(node)
            columns = [int(pattern[0][1:]), int(pattern[-1][1:])]
            #if columns[0]==columns[1]:
            #    columns = [columns[0]]
            pattern = [c[0] for c in pattern]
            lines = [l for l in self.strings_from_node(node)]
            string += __list2str__(pattern, sep='') + ',' + \
                    __list2str__(columns, sep=' ') + ',' \
                    + __list2str__(lines, sep=' ') + '\n'
        return string

    def bicluster_pattern(self, node):
        return __list2str__([c[0] for c in self.path_to_node(node)], sep='')

    def bicluster_lines(self, node):
        return [l for l in self.strings_from_node(node)]

    def bicluster_columns(self, node):
        pattern = self.path_to_node(node)
        return [int(pattern[0][1:]), int(pattern[-1][1:])]

    def num_lines(self, ids=None):
        nlines = {}
        if ids==None:
            ids = self.bicluster_nodes
        for node in ids:
            nlines[node] = sum([1 for l in self.strings_from_node(node)])
        return nlines


    def num_cols(self, ids=None):
        ncols = {}
        if ids == None:
            ids = self.bicluster_nodes
        for node in ids:
            pattern = self.path_to_node(node)
            columns = [int(pattern[0][1:]), int(pattern[-1][1:])]
            ncols[node] = columns[1]-columns[0]+1
        return ncols

    def num_biclusters(self):
        return len(self.bicluster_nodes)

    def filter(self, minline=2, mincol = 1):
        for node in self.bicluster_nodes:
            if self.ncols[node] >= mincol and self.nlines[node] >= minline:
               self.filtered_nodes[node] = True
        return self.filtered_nodes


def __list2str__(alist, sep=' '):
    string=''
    for i in alist:
        string += sep
        string += str(i)
    return string


def __prepare_lines__(lines):
    # create string set from lines
    string_set = lines
    # append column numbers and term symbols
    for str_idx, string in enumerate(string_set):
        new_string = SymList()
        for idx,c in enumerate(string):
            new_string.append(SymList(c + str(idx)))
        term = SymList('$'+str(str_idx))
        new_string.append(term)
        string_set[str_idx] = new_string
    return string_set


def norm(mat):
    # mat is a numpy 2D array
    # normalize each line
    scale(mat, axis=1, copy=False)
    return mat


def diff(mat, delay=1):
    mat2 = np.zeros((mat.shape[0], mat.shape[1] - delay))
    for i in xrange(mat.shape[0]):
        for j in xrange(mat.shape[1]-delay):
            if abs(mat[i, j]) != 0:
                mat2[i, j] = (mat[i, j + delay] - mat[i, j])/abs(mat[i, j])
            elif mat[i, j + delay] < 0:
                mat2[i, j] = -1
            elif mat[i, j + delay] > 0:
                mat2[i, j] = 1
            #else:
            #    mat2[i,j] = 0
    return mat2


def discretization(mat, t=1):
    lines = []
    for i in xrange(mat.shape[0]):
        s = ''
        for j in xrange(mat.shape[1]):
            if mat[i, j] <= -t:
                s += 'D'
            elif mat[i, j] >= t:
                s += 'U'
            else:
                s += 'N'
        lines.append(s)
    return lines

if __name__ == '__main__':

    print 'Test 1'
    string_set = ['NUDUN', 'DUDUD', 'NNNUN', 'UUDUU']
    biclusters = CCCBiclustering(string_set)
    print biclusters
    biclusters.compute_p_values()
    '''
    print 'Test 2'
    import numpy as np
    mat = np.random.random((5,30))
    print mat
    mat = norm(mat)
    print mat
    mat = diff(mat, 5)
    print mat
    mat = discretization(mat)
    for s in mat:
        print s
    biclusters = CCCBiclustering(mat)
    print biclusters

    print 'Test 3'
    test_file = './test_data/1500_Rows_50_Rows_50_Columns.txt'
    f = open(test_file,'r')
    lines=[]
    for idx, line in enumerate(f):
        lines.append('')
        for s in line.split()[1:]:
            lines[idx] += str(s)
    lines = lines[1:]

    b = CCCBiclustering(lines)
    f = open('result.out','w')
    f.write(str(b))
    f.close()
    '''
