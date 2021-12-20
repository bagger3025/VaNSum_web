from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from konlpy.tag import Twitter 
import numpy as np

class SentenceTokenizer(object):
    def __init__(self, kkma):
        self.kkma = kkma
        self.twitter=Twitter()
        self.stopwords = ['중인' ,'만큼', '마찬가지', '꼬집었', "연합뉴스", "데일리", "동아일보", "중앙일보", "조선일보", "기자"
,"아", "휴", "아이구", "아이쿠", "아이고", "어", "나", "우리", "저희", "따라", "의해", "을", "를", "에", "의", "가",
]
    # def url2sentences(self,url): # url주소를 받 아 기사내용을 추출하여 kkma.sentences()를 이용하여 문장단위로 나눠준 이후 sentences를 리턴
    #     start = time.time()
    #     article = Article(url, language='ko')
    #     article.download()
    #     article.parse()
    #     end=time.time()
    #     print(end-start)
    #     sentences = self.kkma.sentences(article.text) #article.text 를 문장 단위로 끊어준다.
        
      
    #     return sentences
    
    def text2sentences(self, text): #text(str)를 입력받아 kkma.sentences()를 이용하여 문장단위로 나누어 준 후 sentences를 리턴
        sentences = self.kkma.sentences(text)
                
        return sentences
    
    def get_nouns(self, sentences): #sentences를 받아 Twitter.nouns()를 이용하여 명사를 추출한 뒤 nouns를 return 해준다.
        nouns=[]
        for sentence in sentences:
            if sentence != ' ':
                nouns.append(' '.join([noun for noun in self.twitter.nouns(str(sentence))
                                      if noun not in self.stopwords and len(noun)>1]))
        return nouns

class GraphMatrix(object):
    def __init__(self):
        self.tfidf=TfidfVectorizer()
        self.cnt_vec=CountVectorizer()
        self.graph_sentence=[]
    
    def tfidf_graph(self, sentence):
        tfidf_mat=self.tfidf.fit_transform(sentence).toarray()
        self.graph_sentence=np.dot(tfidf_mat,tfidf_mat.T)# tfidf matrix n*n으로 만들어내기
        return self.graph_sentence #sentence graph return

'''def tf(t,d):
    return d.count(t)
    
def idf(t, sentence):
    df = 0 
    for sen in sentence:
        df += t in sen
    return log(len(sentence)/(df+1))
    
def tfidf(t,d, sentence):
    return tf(t,d)*idf(t,sentence)'''

class Rank(object):
    def get_ranks(self,graph, d=0.85):

        A=graph
        matrix_size=A.shape[0]
        for id in range(matrix_size):
            A[id:id]=0
            link_sum=np.sum(A[:,id])
            if link_sum!=0:
                A[:,id]/=link_sum
        pr=list(range(0,matrix_size))
        
        for iter in range(100):
            pr=0.15+0.85*np.dot(A,pr)
    
        
        #pr2=[int (i) for i in pr]
        
        dictionary = {i:pr[i] for i in range(len(pr))}
        
        return dictionary  
        
class TextRank(object):
    def __init__(self,text, kkma):
        self.sent_tokenize=SentenceTokenizer(kkma)
        
        if text[:5] in ('http:', 'https'): #text로 url을 주는 경우
            print('url case========================================')
            self.sentences = self.sent_tokenize.url2sentences(text)
        elif type(text) is str: #text로 text를 주는 경우
            self.sentences = self.sent_tokenize.text2sentences(text)
            # print('text case========================================')
            #self.sentences = self.sent_tokenize.text2sentences(text)
        else:   #쪼개서 주는 경우
            self.sentences = text
            
        self.nouns = self.sent_tokenize.get_nouns(self.sentences) #문장단위로 나눠준 self.sentences에서 명사만을 추출하기
        
        self.graph_matrix = GraphMatrix() # graph_matrix 생성자 (?)
        self.sent_graph = self.graph_matrix.tfidf_graph(self.nouns) #tfidf 매트릭스 만들기 
        # self.words_graph, self.idx2word = self.graph_matrix.build_words_graph(self.nouns) #cnt_vet_mat의 내적을 words_graph에, dic형태의 {idx, word}를 idx2word에 할당
        
        
        self.rank=Rank()
        self.sent_rank_idx=self.rank.get_ranks(self.sent_graph)
        self.sorted_sent_rank_idx=sorted(self.sent_rank_idx, key=lambda k:self.sent_rank_idx[k], reverse=True)
        
        # self.word_rank_idx=self.rank.get_ranks(self.words_graph)
        # self.sorted_word_rank_idx=sorted(self.word_rank_idx, key=lambda k:self.word_rank_idx[k], reverse=True)
        
    def summarize(self,sent_num=3):
        summary = []
        index=[]
        for idx in self.sorted_sent_rank_idx[:sent_num]:
            index.append(idx)
        
        
        index.sort()
        
        # print(index)
        for idx in index:
            summary.append(self.sentences[idx])

        return summary


def newssum(url, kkma):
    # print("-----------------------------newssum----------------------------------")
    # print(url)
    textrank=TextRank(url, kkma)
    sum=(textrank.summarize(3))
    # print(sum)

    probdict=sorted(textrank.sent_rank_idx.items(), key=lambda i: i[1], reverse=True)
    #  확률값 dict

    return sum


# number를 받으면 상위  number개의 문장에 대한 확률 값(problist)과 문장 번호가 어떻게 되는지(senlist)가 리턴된다.
def newssumModified(url, kkma, number): # number 추가함. 몇개의 문장을 뽑을 것인지.
    textrank=TextRank(url,kkma)
    sum = textrank.summarize(number)
    probdict=sorted(textrank.sent_rank_idx.items(), key=lambda i: i[1], reverse=True)
    print(probdict)
    j=0
    senlist=[]
    problist=[]
    while(j<number):
        senlist.append(probdict[j][0])
        problist.append(probdict[j][1])
        j+=1

    return senlist, problist


