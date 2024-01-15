'''
Created on Jun 15, 2018
@author: xh

modified by: chen xuying
modified content:
    - change: suffix, prefix, infix analysis_tuple and candidate
    - filter candidates (filter_df_afx)
    - change (get_best_N)
'''

from useembedding import UseEmbedding
from languages import create_language

import math
from datetime import datetime
import pandas as pd

from tqdm import tqdm
from joblib import Parallel,delayed

class AffixGenerator():
    '''
    '''
    def __init__(self,lang):
        '''
        Constructor
        '''
        self.lang = lang

        if create_language(lang).has_pretrained_affix_list():
            pass
        else:
            self.UseEmbedding = UseEmbedding(lang) # initialize the embedding model
        

    def __gen_suf_analysis_tuple(self, word, word_dict, min_stem_len, max_suf_len, min_suf_len):
        sIndx = max(min_stem_len, len(word) - max_suf_len)
        for i in range(sIndx, len(word) - min_suf_len + 1):
            stem = word[:i]
            suf = word[i:]
            if stem in word_dict:
                similarity = self.UseEmbedding.get_similarity(word,stem)
                if similarity != 0:
                    # df_suf.loc[len(df_suf)] = [suf,stem, similarity]
                    return [suf,stem, similarity]

    def __gen_suf_cand(self, word_dict, min_stem_len, max_suf_len=6, min_suf_len=1, min_suf_freq = 1):
        suf_tuple_list = Parallel(n_jobs=-2,backend='threading')(delayed(self.__gen_suf_analysis_tuple)(word, word_dict, min_stem_len, max_suf_len, min_suf_len) for word in tqdm(word_dict,desc='生成 suffix: ') if len(word) > min_stem_len)
        '''
        suf_tuple_list = []
        counter = 0
        for word in tqdm(word_dict,desc='生成 suffix: '):
            counter += 1
            if counter > 100:
                break
            if len(word) <= min_stem_len:
                continue
            temp = self.__gen_suf_analysistuple(word, word_dict, min_stem_len, max_suf_len, min_suf_len)
            suf_tuple_list.append()
        '''
        suf_tuple_list = [x for x in suf_tuple_list if x is not None]
        df_suf = pd.DataFrame(suf_tuple_list, columns=['afx','stem','similarity'])
        df_suf['afx_count'] = df_suf.groupby('afx', group_keys=True)['stem'].transform('count')
        df_suf['stem_count'] = df_suf.groupby('stem', group_keys=True)['afx'].transform('count')
        # df_suf['stem_count'] = df_suf['']
        df_suf = df_suf[df_suf['stem_count'] > 1] # stem_count - freq>1 的基础过滤
        df_suf = df_suf[df_suf['afx_count'] > min_suf_freq]
        print("df_suf.head(3)\t",df_suf.head(3))
        return df_suf

    '''
    def gen_suf_cand(self, word_dict, min_stem_len, max_suf_len=6, min_suf_len=1, min_suf_freq = 1): # discard
        df_suf = pd.DataFrame(columns=['afx','stem','similarity'])
        for word in tqdm(word_dict,desc='生成 suffix: '):
            if len(word) <= min_stem_len:
                continue
            sIndx = max(min_stem_len, len(word) - max_suf_len)  # basically min_stem_len i.e. proofing 
            for i in range(sIndx, len(word) - min_suf_len + 1):
                stem = word[:i]
                suf = word[i:]
                if stem in word_dict:
                    similarity = self.UseEmbedding.get_similarity(word,stem)
                    if similarity != 0:
                        df_suf.loc[len(df_suf)] = [suf,stem, similarity]
        # filter
        # stem freq represents stem productivity
        # print(df_suf.head())
        # print(df_suf.groupby('afx', group_keys=True)['stem'].describe())
        df_suf['afx_count'] = df_suf.groupby('afx', group_keys=True)['stem'].transform('count')
        df_suf['stem_count'] = df_suf.groupby('stem', group_keys=True)['afx'].transform('count')
        # df_suf['stem_count'] = df_suf['']
        df_suf = df_suf[df_suf['stem_count'] >= min_suf_freq] # stem_count - freq>1 的基础过滤
        print(df_suf.head(3))
        return df_suf
    '''
    
    def __gen_pref_analysis_tuple(self, word, word_dict, min_stem_len, max_pref_len, min_pref_len):
        eIndx = min(len(word) - min_stem_len, max_pref_len)
        for i in range(min_pref_len, eIndx + 1):
            stem = word[i:]
            pref = word[:i]
            if stem in word_dict:
                similarity = self.UseEmbedding.get_similarity(word,stem)
                if similarity != 0:
                    return [pref,stem, similarity]
    def __gen_pref_cand(self, word_dict, min_stem_len, max_pref_len=6, min_pref_len=1, min_pref_freq = 1):
        pref_tuple_list = Parallel(n_jobs=-1,backend='threading')(delayed(self.__gen_pref_analysis_tuple)(word, word_dict, min_stem_len, max_pref_len, min_pref_len) for word in tqdm(word_dict,desc='生成 prefix: ') if len(word) > min_stem_len)
        pref_tuple_list = [x for x in pref_tuple_list if x is not None]
        df_pref = pd.DataFrame(pref_tuple_list, columns=['afx','stem','similarity'])
        df_pref['afx_count'] = df_pref.groupby('afx', group_keys=True)['stem'].transform('count')
        df_pref['stem_count'] = df_pref.groupby('stem', group_keys=True)['afx'].transform('count')
        df_pref = df_pref[df_pref['stem_count'] >= 1]
        df_pref = df_pref[df_pref['afx_count'] >= min_pref_freq]

        print("df_pref.head(3)\t", df_pref.head(3))
        return df_pref

    '''
    def gen_pref_cand(self, word_dict, min_stem_len, max_pref_len=6, min_pref_len=1, min_pref_freq = 1): # discard
        print('Generating prefix candidates...')
        df_pref = pd.DataFrame(columns=['afx','stem','similarity'])
        for word in tqdm(word_dict,desc='生成 prefix: '):
            if len(word) <= min_stem_len: 
                continue
            eIndx = min(len(word) - min_stem_len, max_pref_len)
            for i in range(min_pref_len, eIndx + 1):
                stem = word[i:]
                pref = word[:i]
                if stem in word_dict:
                    similarity = self.UseEmbedding.get_similarity(word,stem)
                    if similarity != 0: 
                        df_pref.loc[len(df_pref)] = [pref,stem, similarity]
        df_pref['afx_count'] = df_pref.groupby('afx', group_keys=True)['stem'].transform('count')
        df_pref['stem_count'] = df_pref.groupby('stem', group_keys=True)['afx'].transform('count')
        df_pref = df_pref[df_pref['stem_count'] >= min_pref_freq] # stem_count - freq>1 的基础过滤
        # print(df_pref.head())
        return df_pref
        '''

    def __gen_inf_analysis_tuple(self, word, word_dict, min_stem_len, max_inf_len, min_inf_len):
        for i in range(1, len(word) - min_inf_len):
            e_indx = len(word) - max(1, (min_stem_len - i)) 
            for j in range(i + min_inf_len, e_indx + 1):
                inf = word[i:j]
                stem = word[:i] + word[j:]
                if stem in word_dict:
                    similarity = self.UseEmbedding.get_similarity(word,stem)
                    if similarity != 0:
                        return [inf,stem, similarity]

    def __gen_inf_cand(self, word_dict, min_stem_len, max_inf_len=5, min_inf_len=2, min_inf_freq = 1):
        inf_tuple_list = Parallel(n_jobs=-1,backend='threading')(delayed(self.__gen_inf_analysis_tuple)(word, word_dict, min_stem_len, max_inf_len, min_inf_len) for word in tqdm(word_dict,desc='生成 infix: ') if len(word) > min_stem_len)
        inf_tuple_list = [x for x in inf_tuple_list if x is not None]
        df_inf = pd.DataFrame(inf_tuple_list, columns=['afx','stem','similarity'])
        df_inf['afx_count'] = df_inf.groupby('afx', group_keys=True)['stem'].transform('count')
        df_inf['stem_count'] = df_inf.groupby('stem', group_keys=True)['afx'].transform('count')
        df_inf = df_inf[df_inf['stem_count'] >= 1]
        df_inf = df_inf[df_inf['afx_count'] >= min_inf_freq]
        print("df_inf.head(3)\t", df_inf.head(3))
        return df_inf

    '''
    def gen_inf_cand(self, word_dict, min_stem_len, max_inf_len=5, min_inf_len=2, min_inf_freq = 1):
        df_inf = pd.DataFrame(columns=['afx','stem','similarity'])
        for word in tqdm(word_dict,desc='生成 infix: '):
            if len(word) <= min_stem_len: 
                continue
            for i in range(1, len(word) - min_inf_len):
                e_indx = len(word) - max(1, (min_stem_len - i)) 
                for j in range(i + min_inf_len, e_indx + 1):
                    inf = word[i:j]
                    stem = word[:i] + word[j:]
                    if stem in word_dict:
                        similarity = self.UseEmbedding.get_similarity(word,stem)
                        if similarity != 0:
                            df_inf.loc[len(df_inf)] = [inf,stem, similarity]
        df_inf['afx_count'] = df_inf.groupby(by=['afx'], group_keys=True)['stem'].transform('count')
        df_inf['stem_count'] = df_inf.groupby('stem', group_keys=True)['afx'].transform('count')
        df_inf = df_inf[df_inf['stem_count'] >= min_inf_freq] # stem_count - freq>1 的基础过滤
        # print(df_inf.head())
        return df_inf
        '''

    def __count_sort_save_df_afx(self, df_afx):
        df_afx['afx_score'] = df_afx.apply(lambda x:float(math.log10(1 + x['stem_count']) * x['similarity'] * math.log10(1+x['afx_count'] / len(df_afx))) , axis=1)
        # * (stem_len_exp + df_afx['stem'].str.len()) 
        # df_afx['afx_score'] = df_afx.apply(gen_score, axis=1)
        df_afx = df_afx.sort_values(by=['afx','afx_score','similarity','stem_count'], ascending=False)
        date_time = datetime.now().strftime("%y%m%d_%H%M%S")
        df_afx.to_csv(f'./data_output_test/{date_time}.csv')
        print(f'affix list in file {date_time}.csv')
        return df_afx

    def filter_df_afx(self, df_afx, top_N):
        df_afx_filtered = df_afx.drop_duplicates(subset=['afx'], keep='first',inplace=False)
        if len(df_afx_filtered) >= top_N:
            print(f'Best {top_N} out of {len(df_afx_filtered)} affixes generated.')
            return df_afx_filtered.set_index('afx')['afx_score'].head(top_N).to_dict() # [[?]]
        else:
            print(f'{len(df_afx_filtered)} affixes found.')
            return df_afx_filtered.set_index('afx')['afx_score'].to_dict()

    def gen_N_best_suffixes(self, word_dict, min_stem_len=3, max_suf_len=5, min_suf_len=1, min_suf_freq=10, best_N=500):
        if create_language(self.lang).has_pretrained_affix_list():
            df_suf = pd.read_csv('hin_data/pretrained_affix/suf.csv')
        else:
            df_suf = self.__gen_suf_cand(word_dict, min_stem_len, max_suf_len, min_suf_len, min_suf_freq)
            df_suf = self.__count_sort_save_df_afx(df_suf)
        best_suffix_list = self.filter_df_afx(df_suf, best_N)
        return best_suffix_list

    def gen_N_best_prefixes(self, word_dict, min_stem_len=3, max_pref_len=5, min_pref_len=1, min_pref_freq=10, best_N=500):
        if create_language(self.lang).has_pretrained_affix_list():
            df_pref = pd.read_csv('hin_data/pretrained_affix/pref.csv')
        else:
            df_pref = self.__gen_pref_cand(word_dict, min_stem_len, max_pref_len, min_pref_len, min_pref_freq)
            df_pref = self.__count_sort_save_df_afx(df_pref)
        best_prefix_list = self.filter_df_afx(df_pref, best_N)
        return best_prefix_list
    
    def gen_N_best_infixes(self, word_dict, min_stem_len=3, max_inf_len=4, min_inf_len=2, min_inf_freq=10, best_N=500):
        if create_language(self.lang).has_pretrained_affix_list():
            df_inf = pd.read_csv('hin_data/pretrained_affix/inf.csv')
        else:
            df_inf = self.__gen_inf_cand(word_dict, min_stem_len, max_inf_len, min_inf_len, min_inf_freq)
            df_inf = self.__count_sort_save_df_afx(df_inf)
        best_infix_list = self.filter_df_afx(df_inf, best_N)
        return best_infix_list
    
    def save_affix_lists(self, word_dict):
        min_stem_len=3
        max_pref_len=5
        min_pref_len=1
        min_pref_freq=3
        best_N=500
        prefix_stem_len_dist = self.gen_pref_cand(word_dict, min_stem_len, max_pref_len, min_pref_len, min_pref_freq)
        pref_freq_list = sorted([(pref, sum(stem_len_dist.values())) for pref, stem_len_dist in prefix_stem_len_dist.items()], key=lambda x: -x[1])
        best_prefix_list = self.filter_afxes_1(prefix_stem_len_dist, best_N)
        outfile_pref_freq = r'E:\LORELEI\mitch\pref_freq.txt'
        outfile_pref_conf = r'E:\LORELEI\mitch\pref_conf.txt'
        self.__save_item_scores(pref_freq_list, outfile_pref_freq)
        self.__save_item_scores(best_prefix_list, outfile_pref_conf)
        min_stem_len=3
        max_inf_len=4
        min_inf_len=2
        min_inf_freq=3
        best_N=500
        infix_stem_len_dist = self.gen_inf_cand(word_dict, min_stem_len, max_inf_len, min_inf_len, min_inf_freq)
        inf_freq_list = sorted([(inf, sum(stem_len_dist.values())) for inf, stem_len_dist in infix_stem_len_dist.items()], key=lambda x: -x[1])
        best_infix_list = self.filter_afxes_1(infix_stem_len_dist, best_N)
        outfile_inf_freq = r'E:\LORELEI\mitch\inf_freq.txt'
        outfile_inf_conf = r'E:\LORELEI\mitch\inf_conf.txt'
        self.__save_item_scores(inf_freq_list, outfile_inf_freq)
        self.__save_item_scores(best_infix_list, outfile_inf_conf)
        min_stem_len=3
        max_suf_len=5
        min_suf_len=1
        min_suf_freq=3
        best_N=500
        suffix_stem_len_dist = self.gen_suf_cand(word_dict, min_stem_len, max_suf_len, min_suf_len, min_suf_freq)
        suf_freq_list = sorted([(suf, sum(stem_len_dist.values())) for suf, stem_len_dist in suffix_stem_len_dist.items()], key=lambda x: -x[1])
        best_suffix_list = self.filter_afxes_1(suffix_stem_len_dist, best_N)
        outfile_suf_freq = r'E:\LORELEI\mitch\suf_freq.txt'
        outfile_suf_conf = r'E:\LORELEI\mitch\suf_conf.txt'
        self.__save_item_scores(suf_freq_list, outfile_suf_freq)
        self.__save_item_scores(best_suffix_list, outfile_suf_conf)
        

if __name__ == '__main__':
    affixgenerator = AffixGenerator('hin')
    # affixgenerator.
    pass

















