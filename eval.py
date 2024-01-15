'''
Created on May 21, 2018

@author: xh
'''

from tqdm import tqdm
from evalsegpoint import EvalSegPoint
import pandas as pd
import re


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
    
    def __read_gold_seg_oldversion_(self, infile):
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

    

    def __read_gold_seg_deva(self,infile):
        df = pd.read_csv(infile, sep=',',header=None, encoding='utf-8')
        df.columns = ['word','seg_rom','root_rom','seg_deva','root_deva']
        df[['word', 'seg_deva']] = df[['word', 'seg_deva']].map(lambda x: x.strip())
        word_seg_list = [(word.strip(), seg.strip().split(" ")) for word, seg in df[['word', 'seg_deva']].values.tolist()]
        print("gold file samples:", word_seg_list[:3])
        return word_seg_list

    def evaluate(self, infile_pred, infile_gold):
        seg_pred = self.__read_segmentation(infile_pred)
        seg_gold = self.__read_gold_seg_deva(infile_gold)

        # seg_pred_filtered = []
        # seg_gold_filtered = []
        # for i in tqdm(range(len(seg_gold))):
        #     goldseg = seg_gold[i]
        #     testseg = seg_pred[i]
        #     if goldsegs[0] != testseg[0]: # word same
        #         print(goldsegs[0], testseg[0])
        #         continue
        #     seg_pred_filtered.append(testseg)
        #     seg_gold_filtered.append(goldseg)
        # print(len(seg_pred_filtered), len(seg_gold_filtered)) # 977
        EvalSegPoint().evaluate_seg(seg_gold, seg_pred)

    def check(self, infile_pred, infile_gold):
        gold = [(word, seg) for word,seg in self.__read_gold_seg_deva(infile_gold)]
        pred = [(word, seg) for word,seg in self.__read_segmentation(infile_pred)]
        print(len(gold), len(pred))
        for i, ((pred_w, pred_s),(gold_w,gold_s)) in enumerate(zip(pred, gold)):
            if pred_w != "".join(pred_s):
                print(i+1, pred_w, pred_s,sep='\t')
            if gold_w != "".join(gold_s):
                print(i+1, gold_w, gold_s,sep='\t')

if __name__ == '__main__':
    eval = EvalSeg()
    infile_pred = 'data_output_test/hin_out_test_deva.txt'# new
    infile_gold = 'hin_data/hin_goldseg_deva.csv' 

    # eval.check(infile_pred, infile_gold)
    
    eval.evaluate(infile_pred, infile_gold)

    # testset = "hin_data/hin_testin_devanagari_new.txt"
    

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


















