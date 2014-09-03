import string

POSITIVE_INFINITY = 1 << 30

class Node:
    def __init__(self, suffix_link=None):
        self.suffix_link = suffix_link

    def __repr__(self):
        return 'Node(' + str(self.suffix_link) + ')'

class Edge:
    def __init__(self, src_node_idx, dst_node_idx, first_char_idx, last_char_idx):
        self.src_node_idx = src_node_idx
        self.dst_node_idx = dst_node_idx
        self.first_char_idx = first_char_idx
        self.last_char_idx = last_char_idx

    def split(self, suffix, suffix_tree):
        return split_edge(self, suffix, suffix_tree)

    def __len__(self):
        return self.last_char_idx - self.first_char_idx + 1

    def __repr__(self):
        return 'Edge(from ' + str(self.src_node_idx) +\
        ' to ' + str(self.dst_node_idx) +\
        ', chars ' + str(self.first_char_idx) +\
        ' to ' + str(self.last_char_idx) + ')'


def split_edge(edge, suffix, suffix_tree):
    #alloc new node
    new_node = Node()#suffix.src_node_idx
    suffix_tree.nodes.append(new_node)
    new_node_idx = len(suffix_tree.nodes) - 1
    suffix_tree.nchildren.append(1)
    #alloc new edge
    new_edge = Edge(new_node_idx, edge.dst_node_idx, edge.first_char_idx + len(suffix), edge.last_char_idx)
    suffix_tree.insert_edge(new_edge)
    #shorten existing edge
    edge.last_char_idx = edge.first_char_idx + len(suffix) - 1
    edge.dst_node_idx = new_node_idx
    suffix_tree.edge_by_dst[new_node_idx] = edge
    #save new node's depth
    suffix_tree.depths.append(suffix_tree.depths[edge.src_node_idx] + len(edge))
    return new_node_idx


class Suffix:
    def __init__(self, src_node_idx, first_char_idx, last_char_idx):
        self.src_node_idx = src_node_idx
        self.first_char_idx = first_char_idx
        self.last_char_idx = last_char_idx

    def is_explicit(self):
        return is_explicit_suffix(self)

    def is_implicit(self):
        return is_implicit_suffix(self)

    def canonize(self, suffix_tree):
        canonize_suffix(self, suffix_tree)

    def __repr__(self):
        return 'Suffix(' + str(self.src_node_idx) + ', ' + str(self.first_char_idx) + ', ' + str(self.last_char_idx) + ')'

    def __len__(self):
        return self.last_char_idx - self.first_char_idx + 1

def is_explicit_suffix(suffix):
    return suffix.first_char_idx > suffix.last_char_idx

def is_implicit_suffix(suffix):
    return not is_explicit_suffix(suffix)

def canonize_suffix(suffix, suffix_tree):
    if not suffix.is_explicit():
        edge = suffix_tree.edge_lookup[suffix.src_node_idx, suffix_tree.string[suffix.first_char_idx]]
        if(len(edge) <= len(suffix)):
            suffix.first_char_idx += len(edge)
            suffix.src_node_idx = edge.dst_node_idx
            canonize_suffix(suffix, suffix_tree)


class SuffixTree:
    def __init__(self, string, alphabet=None):
        self.string = string
        if alphabet == None:
            alphabet = set(string)
        self.alphabet = alphabet

        self.nodes = [Node()]
        self.depths = [0]
        self.nchildren = [0]

        self.edge_lookup = {} #edge_source_node_first_char_dict
        self.edge_by_dst = {}

        self.active_point = Suffix(0, 0, -1) #node, first idx, last idx
        for j in range(len(string)):
            add_prefix(j, self.active_point, self)

        self.nleaves = [0 for i in range(len(self.nodes))]
        self.__leaf_count__()

    def insert_edge(self, edge):
        self.edge_lookup[edge.src_node_idx, self.string[edge.first_char_idx]] = edge
        self.edge_by_dst[edge.dst_node_idx] = edge

    def remove_edge(self, edge):
        del self.edge_lookup[edge.src_node_idx, self.string[edge.first_char_idx]]
        del self.edge_by_dst[edge.dst_node_idx]

    def internal_nodes_idx(self):
        return [idx for idx, x in enumerate(self.nchildren) if x !=0]

    def leaf_nodes_idx(self):
        return [idx for idx, x in enumerate(self.nchildren) if x ==0]

    def path_to_node(self, node):
        label = self.string[0:0]
        while node > 0:
            edge = self.edge_by_dst[node]
            label = self.string[edge.first_char_idx:edge.last_char_idx+1] + label
            node = self.edge_by_dst[node].src_node_idx
        return label

    def is_leaf(self, node):
        return bool(self.nchildren[node]==0)

    def __repr__(self):
        return pprint_tree(self)

    def pprint_tree(self):
        print pprint_tree(self)

    def __leaf_count__(self, start_node=0):
        count = 0
        for c in self.alphabet:
            try:
                edge = self.edge_lookup[start_node, c]
                if not self.is_leaf(edge.dst_node_idx):
                    count += self.__leaf_count__(edge.dst_node_idx)
                else:
                    count += 1
            except KeyError:
                pass
        self.nleaves[start_node] = count
        return count

class GeneralizedSuffixTree(SuffixTree):
    def __init__(self, strings):
        # create cat string
        # extract alphabet and term char/symbol
        self.strings = strings
        terminators = set()
        alphabet = set()
        string = strings[0][0:0] #generic way of geting a empty object of the same type of Strings items
        for s in strings:
            string += s
            terminators.add(s[-1])
            for l in set(s[0:-1]):
                alphabet.add(l)
        self.alphabet = alphabet
        self.terminators = terminators


        SuffixTree.__init__(self,string)

        # fix depth and leaf edges labels
        for node in self.leaf_nodes_idx():
            edge = self.edge_by_dst[node]
            s = self.string[edge.first_char_idx:edge.last_char_idx+1]
            for idx, char in enumerate(s):
                if char in self.terminators:
                    idx += edge.first_char_idx # idx relative to the full string
                    self.depths[node] -= (edge.last_char_idx-idx)
                    self.edge_by_dst[node].last_char_idx = idx
                    self.edge_lookup[(edge.src_node_idx,self.string[edge.first_char_idx])].last_char_idx = idx
                    break

    def strings_from_node(self, node, ids=set()):
        for c in self.alphabet:
            try:
                edge = self.edge_lookup[node, c]
                if not self.is_leaf(edge.dst_node_idx):
                    ids.update(self.strings_from_node(edge.dst_node_idx, ids))
                else:
                    corrected_idx = edge.last_char_idx
                    for s_id, s in enumerate(self.strings):
                        if corrected_idx-len(s)>=0:
                            corrected_idx -= len(s)
                        else:
                            break
                    ids.add(s_id)
            except KeyError:
                pass
        return ids

def pprint_tree(suffix_tree, start_node=0, string = ''):

    string += 'N%d[d%dl%d]' % (start_node, suffix_tree.depths[start_node], suffix_tree.nleaves[start_node])
    if suffix_tree.nodes[start_node].suffix_link > 0:
        string += '(->' + str(suffix_tree.nodes[start_node].suffix_link) + ')'

    init = string.rfind('\n')+1 # if no \n found, init will be 0
    depth = len(string)-init

    first_edge = True
    for c in suffix_tree.alphabet:
        try:
            edge = suffix_tree.edge_lookup[start_node, c]
            string += '|--'
            string += str(suffix_tree.string[edge.first_char_idx:edge.last_char_idx+1])
            string += '--'
            string = pprint_tree (suffix_tree, edge.dst_node_idx, string)
            first_edge = False
            string += '\n'
            string += ' '*(depth)

        except KeyError:
            pass

    return string


def add_prefix(last_char_idx, active_point, suffix_tree):
    last_parent_node_idx = -1
    while True:
        parent_node_idx = active_point.src_node_idx
        if active_point.is_explicit(): # 1st idx > last idx
            if (active_point.src_node_idx, suffix_tree.string[last_char_idx]) in suffix_tree.edge_lookup:
                #already in tree
                break
        else:
            edge = suffix_tree.edge_lookup[active_point.src_node_idx, suffix_tree.string[active_point.first_char_idx]]
            if suffix_tree.string[edge.first_char_idx + len(active_point)] == suffix_tree.string[last_char_idx]:
                #the given prefix is already in the tree, do nothing
                break
            else:
                parent_node_idx = edge.split(active_point, suffix_tree)
        # if it has not broken the loop, it has done an edge split
        suffix_tree.nodes.append(Node(-1))
        new_node_idx = len(suffix_tree.nodes) - 1
        new_edge = Edge(parent_node_idx, new_node_idx, last_char_idx, POSITIVE_INFINITY)#src,dest,1st char,last char
        suffix_tree.insert_edge(new_edge)
        suffix_tree.nchildren[parent_node_idx] += 1
        suffix_tree.nchildren.append(0)
        suffix_tree.depths.append(suffix_tree.depths[parent_node_idx] + len(new_edge))
        #add suffix link if it is not the first edge split in this call
        if last_parent_node_idx > 0:
            suffix_tree.nodes[last_parent_node_idx].suffix_link = parent_node_idx
        last_parent_node_idx = parent_node_idx
        # ir curr src node is root, advance first char in the active point
        if active_point.src_node_idx == 0:
            active_point.first_char_idx += 1
        # if curr src node is somethig else, follow its suffix link to update active point
        else:
            active_point.src_node_idx = suffix_tree.nodes[active_point.src_node_idx].suffix_link
        active_point.canonize(suffix_tree)
    if last_parent_node_idx > 0:
        suffix_tree.nodes[last_parent_node_idx].suffix_link = parent_node_idx
    #last_parent_node_idx = parent_node_idx
    active_point.last_char_idx += 1
    active_point.canonize(suffix_tree)

#validation code
import collections
is_valid_suffix = collections.defaultdict(lambda: False)
branch_count = collections.defaultdict(lambda: 0)
def is_valid_suffix_tree(suffix_tree):
    walk_tree(suffix_tree, 0, {}, 0)
    for i in range(1, len(suffix_tree.string)):
        if not is_valid_suffix[i]:
            print 'not is_valid_suffix[%s]' % str(i)
            #return False
    leaf_sum = 0
    branch_sum = 0
    for i in range(len(suffix_tree.nodes)):
        if branch_count[i] == 0:
            print 'logic error'
            return False
        elif branch_count[i] == -1:
            leaf_sum += 1
        else:
            branch_sum += branch_count[i]
    if leaf_sum != len(suffix_tree.string):
        print 'leaf_sum != len(suffix_tree.string)'
        print 'leaf_sum:', leaf_sum
        return False
    if branch_sum != len(suffix_tree.nodes) - 1: #root dosn't have edge leading to it
        print 'branch_sum != len(suffix_tree.nodes) - 1'
        return False
    return True

def walk_tree(suffix_tree, current_node_idx, current_suffix, current_suffix_len):
    edges = 0
    for c in suffix_tree.alphabet:
        try:
            edge = suffix_tree.edge_lookup[current_node_idx, c]
            if current_node_idx != edge.src_node_idx:
                raise Exception('eeeeeeeeeeeeeeeeee!!!!!!!!!!!')
            print 'node: %d %d' % (current_node_idx, edge.src_node_idx)
            if branch_count[edge.src_node_idx] < 0:
                print 'error: node labeled as leaf has children!'
            branch_count[edge.src_node_idx] += 1
            edges += 1
            l = current_suffix_len
            for j in range(edge.first_char_idx, edge.last_char_idx + 1):
                current_suffix[l] = suffix_tree.string[j]
                l += 1
            if walk_tree(suffix_tree, edge.dst_node_idx, current_suffix, l):
                if branch_count[edge.dst_node_idx] > 0:
                    print 'error: leaf labeled as having children'
                branch_count[edge.dst_node_idx] -= 1 #leaves have '-1' children
        except KeyError:
            pass
    if edges == 0:
        #leaf. check suffix
        is_valid_suffix[current_suffix_len] = ''.join(current_suffix[i] for i in range(current_suffix_len)) == suffix_tree.string[-(current_suffix_len):]
        print ''.join(current_suffix[i] for i in range(current_suffix_len))
        if not is_valid_suffix[current_suffix_len]:
            print 'not is_valid_suffix[current_suffix_len]'
        ###########################################################
        return True
    else:
        return False

def show_edge(suffix_tree, src_node_idx, first_char):
    edge = suffix_tree.edge_lookup[src_node_idx, first_char]
    print edge
    print suffix_tree.string[edge.first_char_idx:edge.last_char_idx+1]

def show_node(suffix_tree, node_idx):
    for c in suffix_tree.alphabet:
        try:
            edge = suffix_tree.edge_lookup[node_idx, c]
            print edge
            print suffix_tree.string[edge.first_char_idx:edge.last_char_idx+1]
        except KeyError:
            pass
    print str(node_idx) + ' -> ' + str(suffix_tree.nodes[node_idx])




if __name__=='__main__':
    test_str = 'abaababaabaab$'#'mississippi$'
    test_str = 'abcabx$'
    test_str = 'xabxa$'
    POSITIVE_INFINITY = len(test_str) - 1
    suffix_tree = SuffixTree(test_str)
    #is_valid = is_valid_suffix_tree(suffix_tree)
    #print 'is_valid_suffix_tree:', is_valid
    print pprint_tree(suffix_tree)


    Strings = ['xabxa$','babxba#']
    length=0
    for s in Strings:
        length += len(s)
    POSITIVE_INFINITY = length - 1
    suffix_tree = GeneralizedSuffixTree(Strings)
    #is_valid = is_valid_suffix_tree(suffix_tree)
    #print 'is_valid_suffix_tree:', is_valid
    print pprint_tree(suffix_tree)

    print suffix_tree.path_to_node(15)

    print suffix_tree.strings_from_node(17)