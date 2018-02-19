import FileParser
import argparse
from collections import Counter
import itertools


def ms_apriori(transactions, mis, sdc):
    # Ck = [('10', '20', '80'), ('20', '30', '80'), ('10', '120', '140')]
    # Fk = []
    F = []
    supp_counts = {}
    M = sort(mis)
    N = len(transactions)
    L, sup_count = init_pass(transactions, M, mis, N)
    F.append(frequent_itemSets_1(L, sup_count, N))

    C = [x for x in F]

    k = 1  # NOTE: k run one number lower as array index start from 0
    while F[k - 1]:
        # print k
        Fk = []
        if k == 1:
            C.append(level2CandidateGen(L, sdc, sup_count, N, mis))
        else:
            C.append(MSCandidateGen(F[k - 1], sdc, sup_count, mis))
        # print C
        for txn in transactions:
            for c in C[k]:
                c = tuple(c)
                if subset_check(txn, c):
                    if c not in supp_counts:
                        supp_counts[c] = 1
                    else:
                        supp_counts[c] += 1
                if subset_check(txn, c[1:]):
                    if c[1:] not in supp_counts:
                        supp_counts[c[1:]] = 1
                    else:
                        supp_counts[c[1:]] += 1

        for c in C[k]:
            c = tuple(c)
            if c in supp_counts and float(supp_counts[c]) / N >= mis[c[0]]:
                Fk.append(c)
        F.append(Fk)
        k += 1

    # print "C: %s" % C
    # print F['F1']
    for i in sup_count:
        supp_counts[tuple([i])] = sup_count[i]
    return F, supp_counts


def subset_check(txn, c):
    # print c, len(c)
    diff_list = [item for item in c if item not in txn]
    if not diff_list:
        return True
    return False


def filter_constraints(freq_itemsets, cannot_be_together_list, must_haves_list):
    i_sets_to_remove = set()
    for fk in freq_itemsets:
        for i_set in fk:
            flag = False
            for disjoint_items in cannot_be_together_list:
                flag_d = subset_check(i_set, tuple([disjoint_items[0]]))
                for x in disjoint_items[1:]:
                    flag_d = flag_d and subset_check(i_set, tuple([x]))
                if flag_d:
                    i_sets_to_remove.add(i_set)
            for must_have_item in must_haves_list:
                flag = flag or subset_check(i_set, tuple([must_have_item]))
            if not flag:
                i_sets_to_remove.add(i_set)

    for i_set in i_sets_to_remove:
        for fk in freq_itemsets:
            if i_set in fk:
                fk.remove(i_set)
    # print i_sets_to_remove
    return freq_itemsets


def sort(mis):
    M = []
    for key, value in sorted(mis.iteritems(), key=lambda (k, v): (v, k)):
        M.append(key)
    return M


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


def frequent_itemSets_1(L, sup_count, N):
    F1 = []
    for i in L:
        if float(sup_count[i]) / N >= mis[i]:
            F1.append(tuple([i]))
    return F1


def level2CandidateGen(L, sdc, sup_count, N, mis):
    C2 = []
    for i in L:
        if float(sup_count[i]) / N >= mis[i]:
            indexOfI = L.index(i)
            postL = L[indexOfI + 1:]
            for h in postL:
                if float(sup_count[h]) / N >= mis[i] and abs(float(sup_count[h]) - float(sup_count[i])) <= sdc:
                    C2.append(tuple([i, h]))
    return C2


def MSCandidateGen(Fk1, sdc, sup_count, mis):
    Ck = []
    Fk = []
    for f1 in Fk1:
        indexOfF1 = Fk1.index(f1)
        postF1 = Fk1[indexOfF1 + 1:]
        for f2 in postF1:
            if f1[:-1] == f2[:-1]:
                if f1 and f2 and f1[-1] < f2[-1] and abs(float(sup_count[f1[-1]]) - float(sup_count[f2[-1]])) <= sdc:
                    c = f1
                    c.append(f2[-1])
                    Ck.append(c)
                    for s in list(itertools.combinations(c, len(c) - 1)):
                        if c[0] in s or mis[c[1]] == mis[c[0]]:
                            if s not in Fk1:
                                Ck.remove(s)
    # print Ck
    return Ck


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MSApriori program for multiple item support (mis) apriori')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-i', '--input', help='path to input file', required=True)
    required.add_argument('-p', '--params', help='path to parameters file', required=True)
    optional.add_argument('-o', '--output', help='path to output file', required=False)
    parser._action_groups.append(optional)
    args = vars(parser.parse_args())

    mis, sdc, cannot_be_together_list, must_haves_list = FileParser.parse_params(args['params'])
    txn_list = FileParser.parse_txns(args['input'])
    freq_itemsets, support_counts = ms_apriori(txn_list, mis, sdc)
    # print "freq_itemsets: %s" % freq_itemsets
    # freq_itemsets = [[('20'), ('40'), ('50'), ('10')], [('20', '40'), ('40', '70'), ('70', '80'), ('10', '120')],
    #  [('20', '30', '80'), ('20', '40', '80'), ('30', '70', '80'), ('20', '40', '50')]]
    filtered_freq_itemsets = filter_constraints(freq_itemsets, cannot_be_together_list, must_haves_list)
    # print filtered_freq_itemsets
    # filtered_freq_itemsets = [[('20'), ('40'), ('50'), ('10')], [('20', '40'), ('40', '70'), ('70', '80'), ('10', '120')],
    #                  [('20', '30', '80'), ('20', '40', '80'), ('30', '70', '80'), ('20', '40', '50')]]
    # print "support_counts: %s" % support_counts
    # print args
    if args['output'] is not None:
        f = open(args['output'], 'w')
    else:
        f = open('output-patterns.txt', 'w')

    for i in range(len(filtered_freq_itemsets) - 1):

        print "Frequent %s-itemsets\n" % str(i + 1)
        f.write("Frequent {}-itemsets\n\n".format(str(i + 1)))
        for item_set in filtered_freq_itemsets[i]:
            sup = support_counts[item_set]
            # sup = 5
            if item_set[1:] in support_counts:
                tail_count = support_counts[item_set[1:]]
            else:
                tail_count = None
            # tail_count = None
            is_str = ("{" + str(item_set).replace('(', '').replace(')', '').replace('\'', '') + "}").replace(',}', '}')

            print "\t\t%s : %s" % (sup, is_str)
            f.write("\t\t{} : {}\n".format(sup, is_str))
            if tail_count:
                print "Tailcount = %s" % tail_count
                f.write("Tailcount = {}\n".format(tail_count))

        print "\n\n\t\tTotal number of frequent %s-itemsets = %s\n\n" % (str(i + 1), len(filtered_freq_itemsets[i]))
        f.write("\n\n\t\tTotal number of frequent {}-itemsets = {}\n\n\n".format(str(i + 1), len(filtered_freq_itemsets[i])))
    f.close()
