from FlagEmbedding import FlagReranker
reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation

# You can map the scores into 0-1 by set "normalize=True", which will apply sigmoid function to the score
# 结果语义排序,再去大模型语义
scores = reranker.compute_score([
    ['我喜欢玩什么?', '我喜欢苹果'], 
    ['我喜欢玩什么?', '我喜欢桌子'], 
    ['我喜欢玩什么?', '我喜欢篮球'], 
    # ['what is panda?', 'hi'], 
    # ['what is panda?', 'panda is a bear'], 
    # ['what is panda?', 'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.']
], normalize=True)
# ])
print(scores) # [0.00027803096387751553, 0.9948403768236574]

