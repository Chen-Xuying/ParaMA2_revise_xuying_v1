from tqdm import tqdm
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import fasttext
# from hyperparameters import HyperParameters as hyperparams

class UseEmbedding():
    '''
    input: file --> formatted word_list
    output: stem_dict, suf_dict, embedding_df
    '''
    def __init__(self,lang) -> None:
        self.lang = lang # 把传入的参数固定下来，变成类的属性，可以给多个方法使用
        self.load_embedding_model(lang)
    
    def load_embedding_model(self,lang): # 加一个default？还是放着让它报错？
        '''
        【TBD】: 如果没有embedding model, 就下载模型. + 创建 models 文件夹
        fasttext.util.download_model('en', if_exists='ignore')  # 下载 English model
        '''
        en_model = './models/cc.en.300.bin'
        hi_model = './models/cc.hi.300.bin'
        choose_model = {'eng':en_model,'hin':hi_model} # lang = 'eng' or 'hin'
        try:
            # print(type(lang)) # <enum 'LanguageCatalog'>
            # print(lang.value) # hin
            embedding_model = fasttext.load_model(choose_model[lang.value])
            print(f'Model {choose_model[lang.value]} loaded.\t -- {embedding_model}')
            self.embedding_model = embedding_model
            return embedding_model
        except:
            raise Exception(f"language '{lang.value}' currently not supported")

    def get_similarity(self, word_a, word_b):
        '''
        得到两个词的词向量的相似度
        '''
        vec_word_a = self.embedding_model.get_word_vector(word_a) # 300 dim, <class 'numpy.ndarray'>
        vec_word_b = self.embedding_model.get_word_vector(word_b)
        return float(cosine_similarity([vec_word_a,],[vec_word_b,])[0][0])
        ''' fasttext c++ source code: getsubwordvector
        void FastText::getSubwordVector(Vector& vec, const std::string& subword) const {
            vec.zero();
            int32_t h = dict_->hash(subword) % args_->bucket;
            h = h + dict_->nwords();
        '''
    
    def gen_affix_dict(self,lexicon): # gen affix dict _without_stemchange
        '''
        # no stem change
        input: lexicon = {word:freq}
        output: 

        data format of df-column:[word,(word_seg:(stem,affix_type),score:(similarity,freq))]
        {word_a: (root,(StemChange=NonChange),(AffixType,Affix),score)}
        '''
        # no stem change
        # [(word_1, (root,proc_cands)), (word_2, (root,proc_cands)), ...))]
        # proc_cands = [MorphProcessClass(), Suffixation(NonStemChange(),suf), Prefixation(StemChangeX(ch0, ch1, pos0, pos1),pref), NonMorphProcess(), ...)]

        # 记录 stem_dict 预设是，stem_freq 越高，越可能是个真词
        stem_dict = {} # mixed_affix # {stem: stem_freq}

        # for frequence calculation —— score
        suf_dict = {}  # {suf_ed: {stem_len: stem_len_freq}}
        pref_dict = {} # 
        inf_dict = {}  # 

        df_affix = pd.DataFrame(columns=['affix','affix_type','word_a','stem_b','similarity'])

        for word_a in tqdm(lexicon, desc='遍历 lexicon 生成词缀df: '):
            # word 是基准词, to be segmented
            # stem -- potential STEM with non-stem-change
            for stem_b in [w for w in lexicon.keys if len(w) < len(word_a)]:
                # 双重遍历，但是只找 len 比 a 短的单词，以免重复查找。排除b不在a里的情况

                start_index = word_a.find(stem_b)
                ## processing suffix & infix
                if start_index == 0: # 没有数据无法过滤，干脆不要了
                    # stem_b + suffix = word_a
                    similarity = self.get_similarity(word_a,stem_b)
                    if similarity != 0.0:
                        affix = word_a[len(stem_b)-len(word_a):]  # finding[-3:] = 'ing'
                        if len(affix) <= len(stem_b)+1: # cuz data is dirty, plus one is for buffer
                            # affix is suf. suf is preferable, because it ocurrs more frequently in Hindi and most of the languages.
                            stem_dict[stem_b] = stem_dict.get(stem_b,0) + 1
                            suf_dict[affix] = suf_dict.get(affix,0) + 1
                            affix_type = 'suf'
                            df_affix.loc[len(df_affix)] = [affix,affix_type,word_a,stem_b,similarity]
                        
                elif start_index == len(word_a)-len(stem_b):
                # prefix + stem_b = word_a  e.g. 'preoccupy'[9-6:]='occupy'
                # bad case: तकरी pref;	बन(stem) -- discard it
                    similarity = self.get_similarity(word_a,stem_b)
                    if similarity != 0.0:
                        affix = word_a[:len(word_a)-len(stem_b)]  # e.g. 'preoccupy'[:3]='pre'
                        if len(affix) <= len(stem_b)+1: # 
                            stem_dict[stem_b] = stem_dict.get(stem_b,0) + 1
                            pref_dict[affix] = pref_dict.get(affix,0) + 1
                            affix_type = 'pref'
                            df_affix.loc[len(df_affix)] = [affix,affix_type,word_a,stem_b,similarity]

                elif 0 < start_index < len(word_a)-len(stem_b):  # process circumfix as pref+stem+suf。 processed as complex/ recursive-derivation
                    similarity = self.get_similarity(word_a,stem_b)
                    if similarity != 0.0:
                        pref = word_a[:start_index]
                        suf = word_a[start_index + len(stem_b):] # 'presupposed'[3+7:]=d

                        if len(stem_b) >= len(pref) or len(stem_b) >= len(suf):
                            stem_dict[stem_b] = stem_dict.get(stem_b,0) + 1
                            pref_dict[pref] = pref_dict.get(pref,0) + 1
                            suf_dict[suf] = suf_dict.get(suf,0) + 1
                            df_affix.loc[len(df_affix)] = [pref,'pref',word_a,stem_b,similarity]
                            df_affix.loc[len(df_affix)] = [suf,'suf',word_a,stem_b,similarity]

                else: # cannot process stem change
                    continue

                ## -------------- processing infix ----------------
                # infix example: "stem_m + infix + stem_n" = word_a
                # Tagalog: sulat, (write) --> sumulat, (to write)

                # for j in range(1, len(stem_b)-2): 
                #     potential_infix_len = len(word_a) - len(stem_b)  # len(mu) = 2 (sumulat = sulat)
                #     if stem_b == word_a[:j] + word_a[j+potential_infix_len:] and potential_infix_len > 1:  # j = 2; 'sulat' = 'sumulat'[:2] + 'sumulat'[2+2:]
                #         similarity = self.get_similarity(word_a,stem_b)
                #         if similarity != 0.0:
                #             stem_dict[stem_b] = stem_dict.get(stem_b,0) + 1
                #             inf = word_a[j : j+potential_infix_len+1]
                #             inf_dict[inf] = inf_dict.get(inf,0) + 1
                #             df_inf.loc[len(df_inf)] = [inf,word_a,stem_b,similarity]
                #     else:
                #         continue
                # ————————————————————————————————————————————————
        df_affix['stem_freq'] = df_affix['stem_b'].apply(lambda x: stem_dict[x])
        df_affix = df_affix[df_affix['stem_freq']>1] # stem_freq > 1
        print(df_affix.info(),df_affix.head(),sep='\n')
        df_affix.sort_values(by=['affix','affix_type','stem_b','similarity'],ascending=[True,False,True,False],inplace=True)
        
        print(df_affix.info())
        df_affix.to_excel('./data_output_test/df_affix_test.xlsx',index=False)

        # 按频率过滤掉 freq=1 的 suf/pref/inf
        print('(freq_filtered) affix dict length:',
              len({pref:freq for pref,freq in pref_dict.items() if freq > 1}), # 120 <-- 132 <-- 138 <-- 397
              len({suf:freq for suf,freq in suf_dict.items() if freq > 1}),    # 87 <-- 92  <-- 117 <-- 291
              sep='\n')

        # df_pref.sort_values(by=['score','similarity'],ascending=False,inplace=True)

        return None#, \
            # 'pref_dict: ', pref_dict, \
            # 'suf_dict: ', suf_dict, \
            # # f'inf_dict: {inf_dict}',  \
            # df_affix

    '——————Embedding Evaluation Functions——————'
    def extract_k_topfreq_words(self,file_url):
        return 

    '——————Test Function——————'
    def load_lexicon_from_file(self,file_url):
        '''
        get word list from raw data
        '''
        with open(file_url,'r',-1) as file: # buffering zone size: default as system setting
            word_lines = file.readlines()
            # file format:
            # test:  word         --> word
            # train: word \t freq --> word
            lexicon_dict = {}
            for line in word_lines[:2000]:
                word_freq_tuple = tuple(line.strip().split("\t"))
                if len(word_freq_tuple) == 2: # train data format
                    lexicon_dict[word_freq_tuple[0]] = word_freq_tuple[1]
                elif len(word_freq_tuple) == 1: # test data format. default freq = 1
                    lexicon_dict[word_freq_tuple[0]] = lexicon_dict.get(word_freq_tuple[0],0) + 1
        return lexicon_dict

    def main(self, file_url):
        lexicon_dict = self.load_lexicon_from_file(file_url)
        print(f'{len(lexicon_dict)} words loaded from "{file_url}".\n') # ,'sample lexicon:\t',lexicon[:10]
        
        self.gen_affix_dict(lexicon_dict)
        # self.save_df_2_csv(df,'test_affix_3_.csv')

    def test(self,lang):
        testlist_en = ['leaf', 'leave', 'leaves', 'leaft','leafted',
                        'imporve','unimporve','imporved','unimporved', # pref & suf test
                        'trancendental','tranal'] # pseudo infix test
        testlist_hi = ['ab','aap','aapne','apneaap',
                        'ka','ke','ki']
        if lang == 'en':
            self.gen_affix_candidate(testlist_en)
        elif lang == 'hi':
            self.gen_affix_candidate(testlist_hi)

    def test_oov(self):
        oovs_hi = ['darjanong','darjan',  # dozens 0, dozen 0
                    'balaatkaar','bal',  # violence/rape 0, dance 1'
                    'maarii', 'mar', # a food 0, beat 1
                    'tattuuvaalaa', 'vaalaa' # pony-person 0, person(suf) 1
                    'raashtravaadii', 'raashtr']  # nationalist 0, nation 0
        oovs_hidev = ['दर्जनों','दर्जन', # 1, 1
                        'बलात्कार','बल', # 1, 1
                        'माडी','मार', # 1, 1
                        'टट्टूवाला','वाला','टट्टू', # 0, 1, 1
                        'राष्ट्रवादी','राष्ट्र'  # , 1
                        ]
        # for i, word_a in enumerate(oovs_hi):
        #     for j, word_b in enumerate(oovs_hi.pop(i)):
        #         similarity = self.get_similarity(word_a,word_b)
        #         # sample_simi = self.similarity(word_a,word_b)
        #         print(word_a,word_b,similarity) #,sample_simi) # if similarity == [[0.0]] and similarity != sample_simi else None
        for i, word_a in enumerate(oovs_hidev):
            for j, word_b in enumerate([k for k in oovs_hidev[i+1:]]):
                similarity = self.get_similarity(word_a,word_b)
                # sample_simi = self.similarity(word_a,word_b)
                # print(word_a,word_b,similarity,'\n') #,sample_simi)
        
        return similarity

    
if __name__ == "__main__":
    test_devanagari_url = "./hin_data/hin_testin_devanagari.txt"
    train_devanagari_url = "./hin_data/hin_wordlist_train_devanagari.txt" # devanagari \t freq
    file_url = train_devanagari_url
    # lang = LanguageCatalog.Hindi
    # lang.value = 'hin'
    # generate_affix_with_embedding = GenerateAffixWithEmbedding(lang)
    # generate_affix_with_embedding.main(file_url)
    # generate_affix_with_embedding.test(lang)

    # generate_affix_with_embedding.test_embedding_model()
    # generate_affix_with_embedding.test_oov()


