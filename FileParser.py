import re


def parse_params(params_file_path):
    params_file = open(params_file_path)
    mis = {}
    cannot_be_together_list = []
    must_haves_list = []
    sdc = None
    for line in params_file:
        m = re.search('MIS\((\d+)\)\s=\s(\d*\.\d*)', line)
        if m is not None:
            # print "%s : %s" % (m.group(1), m.group(2))
            mis[m.group(1)] = float(m.group(2))
        else:
            m = re.search('SDC\s=\s(\d*.\d)', line)
            if m is not None:
                # print "sdc : %s" % m.group(1)
                sdc = float(m.group(1))
            else:
                m = re.search('cannot_be_together:\s(.*)\r', line)
                if m is not None:
                    items_str = m.group(1).replace('}, {', '};{')
                    item_sets = items_str.split(';')
                    for i in item_sets:
                        # print i
                        p = i.replace('{', '')
                        q = p.replace('}', '')
                        cannot_be_together_list.append(tuple(q.split(', ')))
                        # print cannot_be_together_list
                else:
                    m = re.search('must-have:\s(.*)\r', line)
                    if m is not None:
                        must_haves = m.group(1).split(' or ')
                        for i in must_haves:
                            # print i
                            must_haves_list.append(i)
                            # print must_haves_list

    return mis, sdc, cannot_be_together_list, must_haves_list


def parse_txns(input_file_path):
    txns_file = open(input_file_path)
    transactions = txns_file.read().replace('{', '').replace('}', '').split('\r\n')
    txn_list = []
    for t in transactions:
        txn_list.append(tuple(t.split(', ')))
    return txn_list


if __name__ == '__main__':
    print parse_params('parameter-file.txt')
    print parse_txns('input-data.txt')