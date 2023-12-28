# import pytest
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
# negative_simi case
wa = 'कार'
wb = 'कार्यवाही'

hin_embedding = fasttext.load_model('./models/cc.hi.300.bin')
vec_wa = hin_embedding.get_word_vector(wa)
vec_wb = hin_embedding.get_word_vector(wb)
simi = float(cosine_similarity([vec_wa,],[vec_wb,])[0][0])
print(
    vec_wa,
    vec_wb,
    simi
    )

# word vec 的负值的意义？



'''unitest: sample snippet
import unittest

class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
 
if __name__=='__main__':
    unittest.main()
    pass
'''