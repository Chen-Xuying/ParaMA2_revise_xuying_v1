'''
Created on Apr 12, 2018
@author: xh

modified:
    - run: use train_file: original training set + embedding words
'''

import argparse
from dataio import read_item_freq_list, read_item_list
from morphanalyzer import MorphAnalyzer
from parameters import Parameter
from typology import MorphTypology, get_gold_features
from languages import LanguageCatalog, create_language, Hindi

from tqdm import tqdm


def save_segmentations(word_segs, outfile):
    fout = open(outfile, 'w', -1, 'utf-8')
    for word, (seg, components) in word_segs:
#         seg_str = ' '.join(seg)
#         component_str = ' '.join([' '.join(component) for component in components])
        seg_str = ' '.join(seg)
        component_str = ' '.join([' '.join(component) for component in components])
        fout.write('%s\t%s\t%s\n' % (word, seg_str, component_str))
    fout.close()

def save_segmentations_1(word_segs, outfile):
    fout = open(outfile, 'w', -1, 'utf-8')
    for word, (seg, components) in word_segs:
#         seg_str = ' '.join(seg)
#         component_str = ' '.join([' '.join(component) for component in components])
        seg_str = ', '.join(seg)
        component_str = ' '.join(['(' + ', '.join(component) + ')' for component in components])
        fout.write('%s\t[%s]\t%s\n' % (word, seg_str, component_str))
    fout.close()

def seg_file(infile, params, outfile = None, infile_test = None, outfile_test = None, add_test_to_train = True, morph_typology=None, outfile_der=None, outfile_pdgm = None):
    print('| Reading data...')
    word_freq_list = read_item_freq_list(infile) # read train file [(item1, freq1), (itme2, freq2),…,]
    lang = LanguageCatalog.Hindi # .Other
    language = create_language(lang)
    word_list_good = [(word, freq) for word, freq in tqdm(word_freq_list) if freq >= params.min_word_freq and language.is_alphabetic_word(word)] # params.min_word_freq 每个语种都是1 # remains: 1228958
    print('Read word count from file (filtered for alphabetic word) : %s' % (len(word_list_good)))
    if infile_test != None:
        test_list = read_item_list(infile_test) # read test file
        print('Test words: %s' % (len(test_list)))
        if add_test_to_train:
            print('| Add test words to training list...')
            word_dict = dict(word_list_good)
            for word in test_list:
                if word in word_dict:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1
            word_list_good = sorted(word_dict.items(), key=lambda x: -x[1]) # 按 freq 排序
    print('No. of words for training (filtered): %s' % (len(word_list_good)))
    print('| Analyzing...')
    if not morph_typology:
        morph_typology = MorphTypology()
    
    morph_analyzer = MorphAnalyzer(lang, dict(word_list_good), morph_typology, params)
    if outfile != None:
        print('| Segmenting...')
        word_list = [word for word, _freq in word_freq_list]
        word_segs = morph_analyzer.segment_word_list(word_list)
        print('| Saving result...')
        save_segmentations(zip(word_list, word_segs), outfile)
    if infile_test != None and outfile_test != None:
        print('| Segmenting test data...')
        test_segs = morph_analyzer.segment_word_list(test_list)
        print('| Saving test result...')
        save_segmentations(zip(test_list, test_segs), outfile_test)
    if outfile_der:
        morph_analyzer.save_der_chain_groups(outfile_der)
    if outfile_pdgm:
        morph_analyzer.save_final_paradigms(outfile_pdgm)
    print('| Done!')


## ----------------- Simply run the segmentor with default parameters ------------------
def run():

    infile_train = r'hin_data/hin_train_devanagari.txt'
    infile_test = r'hin_data/hin_goldseg_deva.csv'
    outfile_test = r'./data_output_test/hin_out_test_deva.txt'
    outfile_der=r'./data_output_test/hin_out_derivation_deva.txt'
    outfile_pdgm = r'./data_output_test/hin_out_paradigm_deva.txt'
    outfile = r'./data_output_test/hin_out_segresult.txt'
    
    params = Parameter()
    morph_typology = MorphTypology()
    morph_typology = get_gold_features(LanguageCatalog.Hindi)
    seg_file(infile_train, params, infile_test=infile_test, outfile=outfile, outfile_test=outfile_test, morph_typology=morph_typology,outfile_der=outfile_der,outfile_pdgm=outfile_pdgm)
    # seg_file(infile, params, infile_test=infile_test, outfile_test=outfile_test, add_test_to_train=True, morph_typology=morph_typology,outfile_der=outfile_der,outfile_pdgm=outfile_pdgm)
## -------------------------------------------------------------------------------------
# def run2():
#     infile = r'/Users/chenxuying/coding_playground/dissertation/ParaMA2-master/hin_data/hin_testin.txt'
#     outfile = r''
#     params = Parameter()
#     morph_typology = MorphTypology()
#     seg_file(infile, params, outfile=outfile, morph_typology=morph_typology)
## -------------------------------------------------------------------------------------

if __name__ == '__main__':
    run()
    '''
    params = Parameter()
    arg_parser = argparse.ArgumentParser() # 创建一个叫 arg_parser 的实例对象
    arg_parser.add_argument('infile', help='The file containing a training word list with line format: <word> <freq>')
    arg_parser.add_argument('-o', '--output', help='File to save the training segmentation result', type=str, default=None)
    arg_parser.add_argument('-ti', '--testin', help='File containing a test word list with format: <word>', type=str, default=None)
    arg_parser.add_argument('-to', '--testout', help='File to save the test result', type=str, default=None)
    arg_parser.add_argument('-np', '--noprune', help='Turn off paradigm pruning', default=False, action='store_true')
    arg_parser.add_argument('-H', '--hyphen', help='Whether explicitly deal with hyphen words', default=False, action='store_true')
    arg_parser.add_argument('-a', '--apos', help='Whether explicitly deal with apostrophes', default=False, action='store_true')
    arg_parser.add_argument('-c', '--case', help='Whether case sensitive', default=False, action='store_true')
    arg_parser.add_argument('-l', '--len', help='Minimal length of roots that will be possibly segmented (default:%s)' % params.min_stem_len, type=int, default=params.min_stem_len)
    arg_parser.add_argument('-y', '--partcpy', help='Minimal length of partial copy (default:%s)' % params.min_partialcopy_len, type=int, default=params.min_partialcopy_len)
    arg_parser.add_argument('-ss', '--minsuf', help='Maximal length of suffixes (default:%s)' % params.min_suf_len, type=int, default=params.min_suf_len)
    arg_parser.add_argument('-sl', '--maxsuf', help='Maximal length of suffixes (default:%s)' % params.max_suf_len, type=int, default=params.max_suf_len)
    arg_parser.add_argument('-ps', '--minpref', help='Minimal length of prefixes (default:%s)' % params.min_pref_len, type=int, default=params.min_pref_len)
    arg_parser.add_argument('-pl', '--maxpref', help='Maximal length of prefixes (default:%s)' % params.max_pref_len, type=int, default=params.max_pref_len)
    arg_parser.add_argument('-is', '--mininf', help='Minimal length of infixes (default:%s)' % params.min_inf_len, type=int, default=params.min_inf_len)
    arg_parser.add_argument('-il', '--maxinf', help='Maximal length of infixes (default:%s)' % params.max_inf_len, type=int, default=params.max_inf_len)
    arg_parser.add_argument('-f', '--freq', help='Minimal word frequency (default:%s)' % params.min_word_freq, type=int, default=params.min_word_freq)
    arg_parser.add_argument('-b', '--te2tr', help='Add test data to training', default=False, action='store_true')
    
    args = arg_parser.parse_args() # 将命令行提供的参数传进来
    params.do_pruning = not args.noprune # 访问从命令行传进来的参数，然后赋值给 params 实例对象
    params.do_hyphen = args.hyphen
    params.do_apostrophe = args.apos
    params.case_sensitive = args.case
    params.min_stem_len = args.len
    params.min_partialcopy_len = args.partcpy
    params.max_suf_len = args.maxsuf
    params.min_suf_len = args.minsuf
    params.max_pref_len = args.maxpref
    params.min_pref_len = args.minpref
    params.max_inf_len = args.maxinf
    params.min_inf_len = args.mininf
    params.min_word_freq = args.freq
    params.print_all()
    
    ## ---------- Use the default typological features. You can change typological features here ------------------
    morph_typology = MorphTypology()
    ## For a language in the catalog, you can get the gold typological features:
    morph_typology = get_gold_features(LanguageCatalog.Hindi)
    ## ------------------------------------------------------------------------------------------------------------
    
    infile = args.infile
    outfile = args.output
    infile_test = args.testin
    outfile_test = args.testout
    test_to_train = args.te2tr
    seg_file(infile, params, outfile=outfile, infile_test=infile_test, outfile_test=outfile_test, add_test_to_train=test_to_train, morph_typology=morph_typology)
    '''




















