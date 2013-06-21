# -*- coding: utf8 -*-
import sys
from gensim import corpora, models

class StreamCorpus(object):
    def __init__(self, filename, dictionary):
        self.filename = filename
        self.dictionary = dictionary
    
    def __iter__(self):
        for line in open(self.filename):
            yield self.dictionary.doc2bow(line.replace('\n', '').decode('utf-8').split(','))
    
class ReviewCorpus(object):
    def __init__(self, filename = ""):
        self.filename = filename
        self.dictionary = None
        self.corpus_tfidf = None
        _texts = []
        _stop_words = []
        if not filename:
            return

        self.dictionary = corpora.Dictionary()
        i = 0
        with open(filename + ".txt") as f:
            for line in iter(f.readline, ''):
                i += 1
                line = line.replace('\n', '').decode('utf-8').split(',')
                #_texts.append(line)
                self.dictionary.add_documents([line])
                if (i % 10000) == 0:
                    print i 
       
        with open(filename + ".stop.txt") as f:
            for line in iter(f.readline, ''):
                line = line.replace('\n', '').decode('utf-8').split(',')
                _stop_words = _stop_words + line

        #self.dictionary = corpora.Dictionary(_texts)
        once_ids = [tokenid for tokenid, docfreq in self.dictionary.dfs.iteritems() if docfreq == 1]        
        _token_dict = self.dictionary.token2id
        stop_ids = [_token_dict[stopword] for stopword in _stop_words if stopword in _token_dict]
        self.dictionary.filter_tokens(once_ids + stop_ids)
        self.dictionary.compactify()
        print("Stop word size:%d"%(len(stop_ids)))
        print("Word only occurs once:%d"%(len(once_ids)))
        print("Dictionary size:%d"%(len(self.dictionary)))
        
        _corpus = StreamCorpus(filename + '.txt', self.dictionary)
        #_corpus = [self.dictionary.doc2bow(text) for text in _texts]
        self.corpus_tfidf = models.TfidfModel(_corpus)
        
        print self.corpus_tfidf
    
    @classmethod
    def load(cls, filename):
        _corpus = cls()
        _corpus.dictionary = corpora.Dictionary.load(filename + '.dict')
        _corpus.corpus_tfidf = models.TfidfModel.load(filename + '.tfidf')
        
        return _corpus
    
    def save(self, filename):
        self.dictionary.save(filename + '.dict')
        self.corpus_tfidf.save(filename + '.tfidf')
    
    def tfidf_score(self, text):
        _scores = self.corpus_tfidf[self.dictionary.doc2bow(text.split(','))] if (self.dictionary and self.corpus_tfidf) else []
        _total_score = 0
        
        for(_, _score) in _scores:
            _total_score += _score
        
        return _total_score

def main():
    corpus = ReviewCorpus(sys.argv[1])
    corpus.save('model/' + sys.argv[1])

"""

    corpus = ReviewCorpus.load('model/' + sys.argv[1])
    texts = [
	         u'一,般般', 
	         u'上下,高速,方便,酒店,一般,价格,适中,餐厅,吃饭,比较,实惠,下次,还,会,选择',
	         u'不错,很,便利',
	         u'挺,干净,的,位置,也,很,好'
	        ]

    for text in texts:
        text_tfidf = corpus.corpus_tfidf[corpus.dictionary.doc2bow(text.split(','))]
        total_score = 0
        for (_id, _score) in text_tfidf:
            total_score += _score 

        print text
        text_dict = ""
        for (_id, _tfidf) in text_tfidf:
            text_dict += "%s[%f]"%(corpus.dictionary[_id], _tfidf) + ","
        print text_dict
        print total_score
"""
if __name__ == '__main__':
    main()
