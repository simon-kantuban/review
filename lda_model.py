# -*- coding: utf8 -*-
import sys
from gensim import corpora, models, similarities

class TrainingCorpus(object):
    def __init__(self, filename = ""):
        self.filename = filename
        _texts = []
        _stop_words = []
        self.dict = None
        self.corpus = None
        if not filename:
            return

        with open(filename + ".txt") as f:
            for line in iter(f.readline, ''):                
                line = line.replace('\n', '').decode('utf-8').split(',')
                _texts.append(line)

        with open(filename + ".stop.txt") as f:
            for line in iter(f.readline, ''):                
                line = line.replace('\n', '').decode('utf-8').split(',')
                _stop_words = _stop_words + line

        self.dict = corpora.Dictionary(_texts)    
        once_ids = [tokenid for tokenid, docfreq in self.dict.dfs.iteritems() if docfreq == 1]
        
        _token_dict = self.dict.token2id
        stop_ids = [_token_dict[stopword] for stopword in _stop_words if stopword in _token_dict]
        self.dict.filter_tokens(once_ids + stop_ids)
        self.dict.compactify()
        
        self.corpus = [self.dict.doc2bow(text) for text in _texts]
        
        self.ldamodel = models.ldamodel.LdaModel(self.corpus, id2word = self.dict, num_topics=30)
    
    @classmethod
    def load(cls, filename):
        _corpus = cls()
        _corpus.dict = corpora.Dictionary.load(filename + '.dict')
        _corpus.corpus = corpora.MmCorpus(filename + '.mm')
        _corpus.ldamodel = models.ldamodel.LdaModel.load(filename + '.lda.model')
        #_corpus.corpus = corpora.BleiCorpus(filename + '.corpus.lda-c')
        
        return _corpus
    
    def save(self, filename):
        self.dict.save(filename + '.dict')
        corpora.MmCorpus.serialize(filename + '.mm', self.corpus)
        self.ldamodel.save(filename + '.lda.model')
        #corpora.BleiCorpus.serialize(filename + '.corpus.lda-c', self.corpus)

training_corpus = TrainingCorpus(sys.argv[1])
training_corpus.save('data/corp')

saved_corpus = TrainingCorpus.load('data/corp')

test_comment = u'卫生,条件,设施,比较,可以,北方,酒店,服务,整体,不如,南方,位置,周边,吃饭,点儿,还是,家乐福'
test_comment_dict = saved_corpus.dict.doc2bow(test_comment.split(','))

matches = saved_corpus.ldamodel[test_comment_dict]
if matches:
    matches = sorted(matches, key=lambda item: -item[1])
    print test_comment
    print saved_corpus.ldamodel.print_topic(matches[0][0])
