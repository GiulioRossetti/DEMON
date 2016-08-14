import os
import Demon


def get_data_dir():
    return os.getcwd() + '/../..'


def read_dict(dictionary_file):
    d = dict()
    fh = open(dictionary_file)
    for line in fh:
        items = line.split('|')
        d[int(items[0])] = '|'.join(items[1:])
    return d


def translate(communities_file, dictionary_file, output_dir, eps, mcs):
    d = read_dict(dictionary_file)
    ifh = open(communities_file)
    for line in ifh:
        id, items = line.strip('\n').split('\t')
        tags = dict()
        items = eval(items)
        ofh = \
            open(
                output_dir + '/{}/{}/'.format(
                    mcs,
                    eps.replace('.', '')) + str(id) + '_' + str(len(items)) + '.txt'
                , 'w+'
            )
        for item in items:
            if item in d:
                for t in d[int(item)].strip('\n').split('|'):
                    if t != '-':
                        if t in tags:
                            tags[t] += 1
                        else:
                            tags[t] = 1
                ofh.write(d[int(item)])
            else:
                print(item)
        i = 0
        for t in sorted(tags, key=tags.get, reverse=True):
            if tags[t] > 10:
                ofh.write('|'.join(['tag', t, str(tags[t])]) + '\n')
                i += 1
            if i > 100:
                break
        ofh.close()
    ifh.close()


for eps in ['0.02', '0.03', '0.04', '0.05', '0.1']:
    for mcs in [30]:
        directory = 'results/{}/{}'.format(mcs, eps.replace('.', ''))
        if not os.path.exists(directory):
            os.makedirs(directory)
        dm = Demon.Demon('data/SINGER_SINGER.csv', epsilon=float(eps),
                         min_community_size=mcs, file_output=True,
                         output_filename='results/{}/{}/output'.format(mcs, eps.replace('.', ''))
                         )
        dm.execute()
        translate('results/{}/{}/output.txt'.format(mcs, eps.replace('.', '')),
                  'data/SINGER_DICT.csv',
                  'results',
                  eps,
                  mcs)