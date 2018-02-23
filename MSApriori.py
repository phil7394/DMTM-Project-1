import FileParser
import argparse
from collections import Counter
import itertools


# ms apriori algorithm
def ms_apriori(transactions, mis, sdc):
    F = []
    supp_counts = {}
    tl_counts = {}
    M = sort(mis)
    N = len(transactions)
    L, sup_count = init_pass(transactions, M, mis, N)
    F.append(frequent_itemSets_1(L, sup_count, N))
    C = [x for x in F]

    k = 1  # NOTE: k run one number lower as array index start from 0
    while F[k - 1]:
        Fk = []
        if k == 1:
            C.append(level2CandidateGen(L, sdc, sup_count, N, mis))
        else:
            C.append(MSCandidateGen(F[k - 1], sdc, sup_count, N, mis))
        for txn in transactions:
            visited = set()  # to remove duplicate tail counts
            for c in C[k]:
                c = tuple(c)
                if subset_check(txn, c):
                    if c not in supp_counts:
                        supp_counts[c] = 1
                    else:
                        supp_counts[c] += 1

                if subset_check(txn, c[1:]):
                    if c[1:] not in visited:
                        visited.add(c[1:])
                        if c[1:] not in tl_counts:
                            tl_counts[c[1:]] = 1
                        else:
                            tl_counts[c[1:]] = tl_counts.get(c[1:]) + 1

        for c in C[k]:
            c = tuple(c)
            if c in supp_counts and float(supp_counts[c]) / N >= mis[c[0]]:
                Fk.append(c)
        F.append(Fk)
        k += 1

    # add support counts of F1 to main supp_count dictionary
    for i in sup_count:
        supp_counts[tuple([i])] = sup_count[i]
    return F, supp_counts, tl_counts


# check if a is a subset of b
def subset_check(b, a):
    diff_list = [item for item in a if item not in b]
    if not diff_list:
        return True
    return False


# filter frequent itemsets given special constraints
def filter_constraints(freq_itemsets, cannot_be_together_list, must_haves_list):
    i_sets_to_remove = set()
    for fk in freq_itemsets:
        for i_set in fk:
            flag = False
            for cbt in cannot_be_together_list:
                cbt_pair_list = list(itertools.combinations(cbt, 2))
                for disjoint_items in cbt_pair_list:
                    flag_d = subset_check(i_set, tuple([disjoint_items[0]])) and subset_check(i_set, tuple(
                        [disjoint_items[1]]))
                    if flag_d:
                        i_sets_to_remove.add(i_set)
                if must_haves_list:
                    for must_have_item in must_haves_list:
                        flag = flag or subset_check(i_set, tuple([must_have_item]))
                    if not flag:
                        i_sets_to_remove.add(i_set)

    for i_set in i_sets_to_remove:
        for fk in freq_itemsets:
            if i_set in fk:
                fk.remove(i_set)
    return freq_itemsets


# sort items by mis in ascending order
def sort(mis):
    M = []
    for key, value in sorted(mis.iteritems(), key=lambda (k, v): (v, k)):
        M.append(key)
    return M


# initial pass to generate L, support counts
def init_pass(T, M, mis, N):
    L = []
    noItemInL = True
    single_list = [item for itemSet in T for item in itemSet]
    sup_count = Counter(single_list)
    for element in M:
        if noItemInL:
            if float(sup_count[element]) / N >= mis[element]:
                noItemInL = False
                L.append(element)
                i = element
        elif float(sup_count[element]) / N >= mis[i]:
            L.append(element)
    return L, sup_count


# generate F1
def frequent_itemSets_1(L, sup_count, N):
    F1 = []
    for i in L:
        if float(sup_count[i]) / N >= mis[i]:
            F1.append(tuple([i]))
    return F1


# generate candidates for k = 2
def level2CandidateGen(L, sdc, sup_count, N, mis):
    C2 = []
    for i in L:
       if float(sup_count[i]) / N >= mis[i]:
            indexOfI = L.index(i)
            postL = L[indexOfI + 1:]
            for h in postL:
                if float(sup_count[h]) / N >= mis[i] and abs(float(sup_count[h]) / N - float(sup_count[i]) / N) <= sdc:
                    C2.append(tuple([i, h]))
    return C2


# generate candidates for k > 2
def MSCandidateGen(Fk1, sdc, sup_count, N, mis):
    Ck = []
    Fk = []
    for f1 in Fk1:
        indexOfF1 = Fk1.index(f1)
        postF1 = Fk1[indexOfF1 + 1:]
        for f2 in postF1:
            if f1[:-1] == f2[:-1]:
                if f1 and f2 and (f1[-1] < f2[-1] or f1[-1] > f2[-1]) and abs(
                        float(sup_count[f1[-1]]) / N - float(sup_count[f2[-1]]) / N) <= sdc:
                    c = list(f1)
                    c.append(f2[-1])
                    Ck.append(tuple(c))
                    for s in list(itertools.combinations(c, len(c) - 1)):
                        if c[0] in s or mis[c[1]] == mis[c[0]]:
                            if s not in Fk1 and s in Ck:
                                Ck.remove(s)
    return Ck


if __name__ == '__main__':
    # input agr parsing
    parser = argparse.ArgumentParser(description='MSApriori program for multiple item support (mis) apriori')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-i', '--input', help='path to input file', required=True)
    required.add_argument('-p', '--params', help='path to parameters file', required=True)
    optional.add_argument('-o', '--output', help='path to output file', required=False)
    parser._action_groups.append(optional)
    args = vars(parser.parse_args())

    mis, sdc, cannot_be_together_list, must_haves_list = FileParser.parse_params(args['params'])  # parse params file
    txn_list = FileParser.parse_txns(args['input'])  # parse transactions file
    freq_itemsets, support_counts, tail_counts = ms_apriori(txn_list, mis, sdc)  # run ms apriori algorithm
    filtered_freq_itemsets = filter_constraints(freq_itemsets, cannot_be_together_list,
                                                must_haves_list)  # filter with special constraints
    # open output file
    if args['output'] is not None:
        f = open(args['output'], 'w')
    else:
        f = open('output-patterns.txt', 'w')

    # output format
    for i in range(len(filtered_freq_itemsets)):
        if filtered_freq_itemsets[i]:
            print "Frequent %s-itemsets\n" % str(i + 1)
            f.write("Frequent {}-itemsets\n\n".format(str(i + 1)))
            for item_set in filtered_freq_itemsets[i]:
                sup = support_counts[item_set]
                if item_set[1:] in tail_counts:
                    tail_count = tail_counts[item_set[1:]]
                else:
                    tail_count = None
                is_str = ("{" + str(item_set).replace('(', '').replace(')', '').replace('\'', '') + "}").replace(',}',
                                                                                                                 '}')

                print "\t\t%s : %s" % (sup, is_str)
                f.write("\t\t{} : {}\n".format(sup, is_str))
                if tail_count:
                    print "Tailcount = %s" % tail_count
                    f.write("Tailcount = {}\n".format(tail_count))

            print "\n\n\t\tTotal number of frequent %s-itemsets = %s\n\n" % (str(i + 1), len(filtered_freq_itemsets[i]))
            f.write("\n\n\t\tTotal number of frequent {}-itemsets = {}\n\n\n".format(str(i + 1),
                                                                                     len(filtered_freq_itemsets[i])))
        elif i is 0:
            print "Frequent %s-itemsets\n" % 1
            f.write("Frequent {}-itemsets\n\n".format(1))
            print "\n\t\tTotal number of frequent %s-itemsets = %s\n\n" % (1, 0)
            f.write("\n\t\tTotal number of frequent {}-itemsets = {}\n\n\n".format(1, 0))
    f.close()  # close output file
