__author__ = 'yogarshi'

import sys
import cPickle as pickle

def main(argv):

    dep_parse_file = open(argv[0], 'r')

    curr_mode = 0
    curr_dep_parse = {}
    all_dep_parses = []
    while True:


        l = dep_parse_file.readline().strip()
        if l == "##":
            all_dep_parses.append(curr_dep_parse)
            break

        if l == "" and curr_mode == 1:
            curr_mode = 0
            all_dep_parses.append(curr_dep_parse)
            curr_dep_parse = {}
            continue

        if l == "" and curr_mode == 0:
            curr_mode = 1
            continue



        if curr_mode == 0:
            continue

        par_open = l.index('(')
        #par_close = l.index(')')

        relation = l[:par_open]
        t = l[par_open+1:-1]

        comma = t.index(',')
        word1 = t[:comma].split('-')[0]
        word2 = t[comma+2:].split('-')[0]
        curr_dep_parse[(word1, word2)] = relation

    for each in all_dep_parses:
        print each
        print

    print len(all_dep_parses)

    pickle.dump(all_dep_parses, open("dep_parse_test.p", 'wb'))


    """
    prev = all_dep_parses[0]

    updated_dep_parse = []

    for i in range(1, len(all_dep_parses)):

        print prev
        print all_dep_parses[i]
        print
        x = raw_input("Combine with prev?")
        if x == 'y':
            prev += all_dep_parses[i]
        else:
            updated_dep_parse.append(prev)
            prev = all_dep_parses[i]

    updated_dep_parse.append(prev)
    print len(updated_dep_parse)

    for each in updated_dep_parse:
        print each

    pickle.dump(updated_dep_parse, open("dep_parse_test1.p", 'wb'))
    """



if __name__ == "__main__":
    main(sys.argv[1:])