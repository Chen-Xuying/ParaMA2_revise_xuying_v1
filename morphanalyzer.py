'''
Created on May 3, 2018
@author: xh
@modifiedby: chenxuying
'''


from bayesian import BayesianModel
from typology import MorphTypology
from morphprocess import Automic
from parameters import Parameter
from paradigm import Paradigm
from derivationchain import DerivationChain
from unifiedcandgen import UniCandGen
from affixcandidate import AffixGenerator
from languages import create_language

from useembedding import UseEmbedding
from joblib import Parallel, delayed
from tqdm import tqdm


class MorphAnalyzer():
    '''
    '''
    
    def __init__(self, lang, lexicon, morph_typology=None, param=None):
        '''
        '''
        print('Initializing morphology analyzer...')
        self.__case_sensitive = param.case_sensitive
        self.__do_hyphen = param.do_hyphen
        self.__do_apostrophe = param.do_apostrophe
        self.__apostrophe_char = param.apostrophe_char
        lexicon = set(lexicon) # set(dict) --> set: {dict.keys()}
        if not self.__case_sensitive: # default: True
            lexicon = self.__process_uppercase_words(lexicon)
        if self.__do_hyphen:
            lexicon = self.__process_hyphen_words(lexicon)
        if self.__do_apostrophe:
            lexicon = self.__process_apostrophe_words(lexicon)
        self.__lexicon = set(lexicon) # 以dict的形式传入参数lexicon, set(lexicon)为键/值集合。{word:freq} #处理过大小写/hyphen/apostrophe的问题
        #self.__use_trans = param.use_trans
        self.__do_pruning = param.do_pruning # default: on
        self.__morph_typology = morph_typology
        self.__param = param
        self.__morph_priority = None
        self.__lang = lang
        #
        if not self.__morph_typology: # 如果没传参，参数是None，那么……默认
            self.__morph_typology = MorphTypology()  # __init__里的所有都是True
        if not self.__param:
            self.__param = Parameter()
        #
        #self.__morph_cand_generators = create_morph_cand_generators(morph_typology, lexicon, param)
        # lexicon = dict(list(lexicon))
        self.__sufs = AffixGenerator(lang).gen_N_best_suffixes(lexicon, self.__param.min_stem_len, self.__param.max_suf_len, self.__param.min_suf_len, min_suf_freq=3, best_N=200) # {afx:afx_score}
        self.__prefs = AffixGenerator(lang).gen_N_best_prefixes(lexicon, self.__param.min_stem_len, self.__param.max_pref_len, self.__param.min_pref_len, min_pref_freq=3, best_N=200)
        # 加上参数, 语言判断
        self.__infs = AffixGenerator(lang).gen_N_best_infixes(lexicon, self.__param.min_stem_len, self.__param.max_inf_len, self.__param.min_inf_len, min_inf_freq=3, best_N=50)
        self.__unified_cand_generator = UniCandGen(create_language(lang), self.__morph_typology, self.__param, lexicon, self.__prefs, self.__sufs, self.__infs)
        # Keep the frequencies of each possible stem changes and choose the top N as valid and redo the analyses again
        self.__stem_change_count = {}
        #
        print('| Analyzing...')
        print('_' * 50)
        self.__analyze()
        print('_' * 50)
        print('| Analysis Done!')


    def __analyze(self):
        print('1. Generating candidates...')
        word_root_proc_cands = Parallel(n_jobs=-2)(delayed(self.__get_typological_candidates_wordtuple)(word) for word in self.__lexicon) #[(word, self.__get_typological_candidates(word)) for word in self.__lexicon]
        print('\nword_root_proc_cands[:5]:',word_root_proc_cands[:5],sep='\t')
        self.__ambiguiity_degree_dist = self.__get_ambiguity_degree_dist(word_root_proc_cands) # 

        self.UseEmbedding = UseEmbedding(self.__lang) # initialize the embedding model ## 看一下这里调的 lang 到底是什么
        # word_root_proc_cands_filtered = [self.__filter_candidates_embed(word_proc_cands) for word_proc_cands in word_root_proc_cands]
        word_root_proc_cands_filtered = word_root_proc_cands
        self.__ambiguiity_degree_dist_filtered = self.__get_ambiguity_degree_dist(word_root_proc_cands_filtered)
        self.__word_root_proc_cands = word_root_proc_cands_filtered
        print("\nself.__word_root_proc_cands[:10]:\t",self.__word_root_proc_cands[:10])
        #
        print('2. Training probabilistic model...')
        bayes_model = BayesianModel()
        bayes_model.train(word_root_proc_cands)
        word_root_proc_cand_probs = [(word, bayes_model.calc_cand_probs(word, root_procs)) for word, root_procs in word_root_proc_cands]
        # word_root_proc = [(word, bayes_model.get_best_root_proc(word, root_procs)) for word, root_procs in word_root_proc_cands]
        self.__model = bayes_model
        self.__word_root_proc_cand_probs = dict(word_root_proc_cand_probs)
        # print("\tword_root_proc_cand_probs:\t",word_root_proc_cand_probs[:3],sep='\t')
        # 
        word_root_proc_list = [(word, [(root, proc) for _prob, (root, proc) in root_proc_probs][:1]) for word, root_proc_probs in word_root_proc_cand_probs]
        print("\nword_root_proc_list length:\t",len(word_root_proc_list),"\nword_root_proc_list: ",word_root_proc_list[:20],sep='\t')
        
        if self.__do_pruning:
            print('3. Pruning...')
            self.__pdgm = Paradigm(word_root_proc_list)
            word_root_proc = [(word, root_procs[0] if len(root_procs) > 0 else (word, Automic())) for word, root_procs in self.__pdgm.final_word_procs()] ###
        else:
            #word_root_proc_list = [(word, (root_proc_probs[0][1] if len(root_proc_probs) > 0 else (word, Automic()))) for word, root_proc_probs in word_root_proc_cand_probs]
            word_root_proc = [(word, root_procs[0] if len(root_procs) > 0 else (word, Automic())) for word, root_procs in word_root_proc_list]
        print('4. Generating derivational chain and segmentation...')
        self.__der_chain = DerivationChain(word_root_proc)
        self.__final_word_root_proc = word_root_proc
        # Get the stem change counts
        #self.__stem_change_count = self.__count_final_stem_changes(self.__final_word_root_proc)
    
    
    def __undo_uppercase_word_seg(self, word_seg, word_ori):
        seg_0 = word_ori[0] + word_seg[0][1:]
        return tuple([seg_0] + word_seg[1:])
    
    def __process_uppercase_word(self, word):
        if word[0].lower() != word[0] and word[1:].lower() == word[1:]:
            return word.lower()
        return word
        
    def __process_uppercase_words(self, word_set):
        return set([self.__process_uppercase_word(word) for word in word_set])
    
    def __process_hyphen_word(self, word):
        sub_words = []
        for sub_word in word.split('-'):
            sub_word = sub_word.strip()
            if len(sub_word) > 0:
                sub_words.append(sub_word)
        return sub_words
    
    def __process_hyphen_words(self, word_set):
        word_list = []
        for word in word_set:
            word_list.extend(self.__process_hyphen_word(word))
        return set(word_list)
    
    def __process_apostrophe_word(self, word):
        sub_words = []
        indx = word.find(self.__apostrophe_char, 1)
        while indx > 0:
            sub_word = word[:indx]
            if len(sub_word) > 0:
                sub_words.append(sub_word)
            word = word[indx:]
            indx = word.find(self.__apostrophe_char, 1)
        if len(word) > 0:
            sub_words.append(word)
        return sub_words
    
    def __process_apostrophe_words(self, word_set):
        word_list = []
        for word in word_set:
            word_list.append(self.__process_apostrophe_word(word)[0])
        return set(word_list)
    
    def __get_typological_candidates(self, word):
        '''
        Generate candidate patterns according to the typological features:
        '''
        return self.__unified_cand_generator.get_candidate_analyses(word)
    
    def __get_typological_candidates_wordtuple(self, word):
        '''
        return tuple
        '''
        return (word, self.__unified_cand_generator.get_candidate_analyses(word))


    def __filter_candidates_embed(self, word_proc_cands): # word_root_proc_cands: (word, [(root, proc),(r,p)]) # word_proc_cands
        word = word_proc_cands[0]
        stem_proc_cands = word_proc_cands[1]
        if len(stem_proc_cands) == 0:
            return word_proc_cands
        
        filtered_stem_proc_cands = []
        for stem, proc in stem_proc_cands:
            similarity = self.UseEmbedding.get_similarity(word,stem)
            if not similarity:
                pass
            elif similarity == 0:
                pass
            else:
                filtered_stem_proc_cands.append([(stem, proc)])
        return (word, filtered_stem_proc_cands)
    
    def __get_ambiguity_degree_dist(self, word_root_proc_cands):
        ambiguity_degree_dist = {}
        for _word, proc_cands in word_root_proc_cands:
            amb_deg = len(proc_cands)
            if amb_deg in ambiguity_degree_dist:
                ambiguity_degree_dist[amb_deg] += 1
            else:
                ambiguity_degree_dist[amb_deg] = 1
        return ambiguity_degree_dist
    
    def __analyze_word_proc(self, word, topN=1):
        if word in self.__word_root_proc_cand_probs:
            return self.__word_root_proc_cand_probs[word]
        root_procs = self.__get_typological_candidates(word)
        root_procs_probs = self.__model.calc_cand_probs(word, root_procs, sort=True)
        if topN <= 0: return root_procs_probs
        return root_procs_probs[:topN]
    
    def __count_prior_stem_changes(self, word_root_proc_cands):
        stem_change_counts = {}
        for _word, root_proc_cands in word_root_proc_cands:
            prob = 1.0 / len(root_proc_cands)
            for _root, proc in root_proc_cands:
                stem_change = proc.change_key()
                if stem_change in stem_change_counts:
                    stem_change_counts[stem_change] += prob
                else:
                    stem_change_counts[stem_change] = prob
        return stem_change_counts
    
    def __count_weighted_stem_changes(self, word_root_proc_cand_probs):
        stem_change_counts = {}
        for _word, root_proc_cand_probs in word_root_proc_cand_probs:
            for prob, (_root, proc) in root_proc_cand_probs:
                stem_change = proc.change_key()
                if stem_change in stem_change_counts:
                    stem_change_counts[stem_change] += prob
                else:
                    stem_change_counts[stem_change] = prob
        return stem_change_counts
    
    def __count_final_stem_changes(self, final_word_root_proc):
        stem_change_counts = {}
        for _word, (_root, proc) in final_word_root_proc:
            stem_change = proc.change_key()
            if stem_change in stem_change_counts:
                stem_change_counts[stem_change] += 1
            else:
                stem_change_counts[stem_change] = 1
        return stem_change_counts
    
    def analyze_word(self, word, topN=1):
        '''
        Return the result in a tuple: word (root, morph-type, pattern, change)
        '''
        if not self.__case_sensitive:
            word = self.__process_uppercase_word(word)
        root_procs = self.__analyze_word_proc(word, topN)
        word_analyses = [(root, proc.morph_type().value, proc.pat(), proc.change().key()) for root, proc in root_procs]
        return word_analyses
    
    def analyze_word_list(self, word_list, topN=1):
        return [self.analyze_word(word, topN) for word in word_list]
    
    
    def segment_word(self, word):
        word_bak = word # word_bake_up 只是多一个变量
        if not self.__case_sensitive:
            word = self.__process_uppercase_word(word)
        word_seg, components = self.__der_chain.get_segmentation(word) # 为什么 __der_chain 不是定义在 __init__ 里面，而是在 analyze 里面调用类。为啥这里能调用analyze的属性？
        if word_seg: # 这一步是为了干啥？确认word_seg不为空？但是为啥会空？
            return word_seg, components
        root_proc_cands = self.__get_typological_candidates(word)
        if len(root_proc_cands) == 0:
            return (word,)
        cand_probs = self.__model.calc_cand_probs(word, root_proc_cands)
        root, proc = cand_probs[0][1]
        root_seg, components = self.__der_chain.get_segmentation(root)
#         if not root_seg:
#             root_seg = (root,)
        components_1 = components.copy()
        component = ('__'.join(root_seg), proc.pat(), proc.change_key())
        components_1.append(component)
        if not self.__case_sensitive and word_bak != word:
            return self.__undo_uppercase_word_seg(proc.apply2seg(root_seg), word_bak), components_1
        return proc.apply2seg(root_seg), components_1
    
    def segment_word_list(self, word_list):
        return [self.segment_word(word) for word in tqdm(word_list, desc='Word Segment processing:')]
    
    def __print_ambiguity_degree_info(self, ambiguiity_degree_dist):
        sorted_amb_deg_dist = sorted(ambiguiity_degree_dist.items(), key=lambda x: -x[0])
        for amb_deg, count in sorted_amb_deg_dist:
            print(' Amb-degree %s: %s' % (amb_deg, count))
        avg_amb_deg = sum(amb_deg * count for amb_deg, count in ambiguiity_degree_dist.items()) / sum(ambiguiity_degree_dist.values())
        print(' Avg-degree: %s' % (avg_amb_deg))
        
    def __print_all_ambiguity_degree_info(self):
        print('-------------Ambiguity Degree Distribution (before filtering with heuristics)')
        self.__print_ambiguity_degree_info(self.__ambiguiity_degree_dist)
        print('-------------Ambiguity Degree Distribution (after filtering with heuristics)')
        self.__print_ambiguity_degree_info(self.__ambiguiity_degree_dist_filtered)
    
    def __print_morph_type_distriution_info(self):
        print('-------------Morphological Type Distribution')
        morph_type_dist = {}
        for _word, (_root, proc) in self.__final_word_root_proc:
            morph_type = proc.morph_type()
            if morph_type in morph_type_dist:
                morph_type_dist[morph_type] += 1
            else:
                morph_type_dist[morph_type] = 1
        for morph_type, count in sorted(morph_type_dist.items(), key=lambda x: -x[1]):
            print(' Morph Type [%s]: %s' % (morph_type.value, count))
    
    def __print_raw_normalized_morph_type_distriution(self):
        print('-------------Normalized Morphological Type Distribution')
        morph_type_dist = {}
        for _word, root_procs in self.__word_root_proc_cands:
            if len(root_procs) == 0:
                continue
            weight = 1.0 / len(root_procs)
            for (_root, proc) in root_procs:
                morph_type = proc.morph_type()
                if morph_type in morph_type_dist:
                    morph_type_dist[morph_type] += weight
                else:
                    morph_type_dist[morph_type] = weight
        for morph_type, count in sorted(morph_type_dist.items(), key=lambda x: -x[1]):
            print(' Morph Type [%s]: %s' % (morph_type.value, count/len(self.__word_root_proc_cands)))
            
    def print_info(self):
        print('----------------------Morphological Analysis Statistical Information--------------------')
        self.__print_all_ambiguity_degree_info()
        self.__print_morph_type_distriution_info()
        self.__print_raw_normalized_morph_type_distriution()
        if self.__do_pruning:
            self.__pdgm.print_statistics()
        self.__der_chain.print_statistics()
    
      
    def save_model(self, outfile):
        pass
    
    def save_final_paradigms(self, outfile):
        self.__pdgm.save_final_paradigms(outfile)
    
    def save_der_chain_groups(self, outfile):
        self.__der_chain.save_chain_groups(outfile)
    
    def save_stem_change_counts(self, outfile):
        stem_change_counts = self.__count_final_stem_changes(self.__final_word_root_proc)
        fout = open(outfile, 'w', -1, 'utf-8')
        for stem_change, count in sorted(stem_change_counts.items(), key=lambda x: -x[1]):
            fout.write('%s\t%s\n' % (stem_change, count))
        fout.close()
    
if __name__ == '__main__':
    affixgenerator = AffixGenerator('hi')







    
