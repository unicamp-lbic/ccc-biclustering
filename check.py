# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 13:59:44 2015

@author: thalita
"""

fname = './test_data/1500_Rows_50_Columns_RECOVERED_CCC_BICLUSTERS_SORTED_PVALUE.txt'
with open(fname, 'r') as f:
    dictionary = {}
    line = f.readline().split('\t')
    while line[0] != '':
        columns = tuple([int(x)-1 for x in line[2].split(' ')[1].split('-')])
        assert(all(columns)>=0)
        lines = []
        line = f.readline().split('\t')
        pattern = line[1].split('\r\n')[0]
        while line[0].find('#') < 0 and line[0] != '':
            lines.append(int(line[0])-1)
            line = f.readline().split('\t')
        dictionary[columns+(pattern,)] = (lines)

#%%
output = ''

fname = './result.out'
encontrado = {}
with open(fname, 'r') as f:
    for line in f.readlines():
        elem = line.split('\n')[0].split(',')
        pattern = elem[0]
        columns = tuple([int(x) for x in elem[1].split()])
        lines = [int(x) for x in elem[2].split()]
        try:
            assert(set(dictionary[columns+(pattern,)]) == set(lines))
            #output += 'OK: bicluster '+ str(columns+(pattern,))+ ' correto\n'
        except KeyError:
            if columns[0]!=columns[1]:
                with open('test_data/1500_Rows_50_Rows_50_Columns.txt', 'r') as orig_file:
                    erro = False
                    orig_lines = orig_file.readlines()
                    for line in lines:
                        orig_line = orig_lines[line+1].split('\r\n')[0].split('\t')
                        orig_pattern = ''
                        for s in orig_line[columns[0]+1:columns[1]+2]:
                            orig_pattern += s
                        if pattern != orig_pattern:
                            output += 'Erro: bicluster '+ str(columns+(pattern,)) + 'encontrado não existe\n'
                            output += '      linha ' + str(line) + ' tem padrão ' + orig_pattern + '\n'
                            erro == True
                            break
                if not erro:
                    try:
                        assert(set(dictionary[(columns[0], columns[1]-1, pattern[0:-1])]) == set(lines))
#                        output += 'OK: novo bicluster '+ str(columns+(pattern,)) + ' coerente encontrado\n'
#                        output += '    corresponde ao bicluster errado' + \
#                              str((columns[0], columns[1]-1, pattern[0:-1])) + '\n'
                        encontrado[(columns[0], columns[1]-1, pattern[0:-1])] = lines
                    except AssertionError:
                        diff = set(dictionary[(columns[0], columns[1]-1, pattern[0:-1])]).symmetric_difference(set(lines))
                        output += 'Warning: novo bicluster '+ str(columns+(pattern,)) + \
                        'encontrado é coerente mas difere do bicluster orig'+\
                        str((columns[0], columns[1]-1, pattern[0:-1])) + \
                        'em' + str(len(diff)) + ' linhas\n'
                        for line in diff:
                            diff_line = orig_lines[line+1].split('\r\n')[0].split('\t')
                            diff_pattern = ''
                            for s in diff_line[columns[0]+1:columns[1]+2]:
                                diff_pattern += s
                            if diff_pattern == pattern:
                                output += 'Erro: linha ' +str(line) + ' deveria estar no bicluster encontrado'

                    except KeyError:
                        if columns[0]!=columns[1]-1:
                            output += 'Erro: bicluster '+ str(columns+(pattern,)) + 'encontrado é coerente mas não existe\n'

        except AssertionError:
            output += 'Erro: '+ str(columns+(pattern,)) + \
            ':\nLinhas são: '+ str(lines)+ \
            '\nmas deveriam ser '+ str(dictionary[columns+(pattern,)])+'\n'

        encontrado[columns+(pattern,)] = lines

for bic in dictionary:
    if bic not in encontrado:
        output += 'Erro: '+ str(bic)+ ' não encontrado\n'

with open('check.out', 'w') as f:
    f.write(output)
