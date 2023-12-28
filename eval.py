'''
Created on May 21, 2018

@author: xh
'''

from tqdm import tqdm
from evalsegpoint import EvalSegPoint


class EvalSeg():
    '''
    '''
    
    def __init__(self):
        '''
        '''
    
    def __read_segmentation(self, infile):
        '''
        Assumed format: 
        expected format: <word>\t<seg>
        where <seg> are white space separated morphemes
        '''
        word_seg_list = []
        fin = open(infile, 'r', -1, 'utf-8')
        for line in fin:
            line = line.strip()
            split_line = line.split('\t')
            if len(split_line) < 2:
                print('Error Line: ' + line)
                continue
            word = split_line[0].strip()
            seg = split_line[1].strip().split(' ')
            word_seg_list.append((word, seg))
        fin.close()
        print("pred file samples:", word_seg_list[:3])
        return word_seg_list
    
    def __read_gold_seg_(self, infile):
        '''
        Assumed format: <word>\t<segs>
        where <segs> is all possible segmentations (allowing multiple gold segmentations) of <seg> separated by comma, and each <seg> is white space separated morphemes
        '''
        word_seg_list = []
        fin = open(infile, 'r', -1, 'utf-8')
        for line in fin:
            line = line.strip()
            split_line = line.split('\t')
            if len(split_line) != 2:
                print('Error Line: ' + line)
                continue
            word = split_line[0].strip()
            segs = [seg_str.strip().split(' ') for seg_str in split_line[1].strip().split(',')]
            word_seg_list.append((word, segs))
        fin.close()
        print("gold file samples:", word_seg_list[:10])
        return word_seg_list

    def __read_gold_seg_fromtabfile(self,infile):
        '''
        Assumed format: <deva_word>\t<translit1>\t<translite2>\t<seg_trans1>\t<seg_trans2>\t<root_trans1>\t<root_trans2>
        expected format: <word>\t<segs>
            where <segs> is all possible segmentations (allowing multiple gold segmentations) of <seg> separated by comma, 
            and each <seg> is white space separated morphemes
        '''
        word_seg_list = []
        fin = open(infile, 'r', -1, 'utf-8')
        fin.readline() # skip the first line
        for line in fin:
            line = line.strip()
            split_line = line.split('\t')
            if len(split_line) != 7:
                print('Error Line: ' + line)
                continue
            word = split_line[0].strip() # devanagari
            # word_trans2 = split_line[3].strip() # transliteration
            if split_line[4] != split_line[5]:
                segs = [seg_str.strip().split(' ') for seg_str in split_line[4:6]]
            else:
                segs = [split_line[5].strip().split(' ')]
            word_seg_list.append((word, segs))
        fin.close()
        print("gold file samples:", word_seg_list[:10])
        return word_seg_list

    def evaluate(self, infile_pred, infile_gold):
        seg_pred = self.__read_segmentation(infile_pred)
        seg_gold = self.__read_gold_seg_fromtabfile(infile_gold)

        seg_pred_filtered = []
        seg_gold_filtered = []
        for i in tqdm(range(len(seg_gold))):
            goldsegs = seg_gold[i]
            testseg = seg_pred[i]
            if goldsegs[0] != testseg[0]:
                print(goldsegs[0], testseg[0])
                continue
            if len(''.join(goldsegs[1][0])) != len(''.join(testseg[1])):
                print(goldsegs[1][0], testseg[1])
                continue
            seg_pred_filtered.append(testseg)
            seg_gold_filtered.append(goldsegs)
        print(len(seg_pred_filtered), len(seg_gold_filtered)) # 977
        EvalSegPoint().evaluate_seg(seg_gold_filtered, seg_pred_filtered)

    def check(self, infile_pred, infile_gold):
        with open(infile_pred) as pred, open(infile_gold) as gold:
            gold.readline()
            gold = gold.readlines()
            pred = pred.readlines()
            print(len(gold), len(pred))
            for i, (line_pred, line_gold) in enumerate(zip(pred, gold)):
                line_pred = line_pred.strip().split('\t')
                line_gold = line_gold.strip().split('\t')
                if line_pred[0] != line_gold[0]:
                    print(i, line_pred[0], line_gold[0])
                    pass
                else:
                    pass

if __name__ == '__main__':
    eval = EvalSeg()
    infile_pred_deva = 'data_output_test/freq1-205326/hin_out_test_deva.txt'
    infile_pred_romansegs = "data_output_test/freq1-205326/hin_out_test_romansegs.txt"
    infile_gold = 'hin_data/hin_morph-segmentation.tab'
    
    eval.evaluate(infile_pred_romansegs, infile_gold)

    # testset = "hin_data/hin_testin_devanagari_new.txt"
    # eval.check(infile_pred, infile_gold)

    '''
    import argparse
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('infile_gold', help='The file containing the gold segmentations')
    arg_parser.add_argument('infile_pred', help='The file containing the segmentation results')
    args = arg_parser.parse_args()
    infile_gold = args.infile_gold
    infile_pred = args.infile_pred
    EvalSeg().evaluate(infile_pred, infile_gold)
    '''


















