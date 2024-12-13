

```
//先切分文档 
$ go run main.go filetochunks -c 50 -o 5
$ ollama pull nomic-embed-text
//文本向量化
$ go run main.go embedding
//查询向量数据库
$ go run main.go retriever -t 3
$ ollama pull mistral
$ llama pull llama2-chinese:13b
//将检索到的内容，交给大语言模型处理
$ go run main.go getanswer
```

#### 优化方向
 1、优化 text_split 算法，使匹配出的结果作为上下文时能够提供更合理的推理/回答依据，采用人工分块，提升质量，节省token ☑   
 2、优化 设计理念，目前思路是问题和答案的向量化匹配，可以采用问题和问题向量化匹配并缓存，以此提升语义匹配效果 ☑   
 3、优化 embedding 模型，可以采用本地中文llm(TextToVec)，提升语义向量化的效果，使得语义匹配过程中能够匹配出最满足要求的文本段落作为上下文   
 4、优化 LLM 模型，可以使用GPT4接口，使得给定提问相同情况下，得到更理想的推理/回答结果   

```
PS C:\api\langchaingo-ollama-rag> .\langchaingo-ollama-rag.exe -h
学习基于langchaingo构建的rag应用

Usage:
  langchaingo-ollama-rag [command]

Available Commands:
  completion   generate the autocompletion script for the specified shell
  embedding    将文档块儿转换为向量
  filetochunks 将文件转换为块儿
  getanswer    获取回答
  help         Help about any command
  retriever    将用户问题转换为向量并检索文档

Flags:
  -h, --help     help for langchaingo-ollama-rag
  -t, --toggle   Help message for toggle
```

### distance的主要功能是计算两个词(组)之间的距离(相似度)。程序将该功能表现为用户输入一条字符串，里面可以包含以空格分制的多个词，然后程序从训练出的模型(demo-word.shi训练出的模型文件名为vectors.bin，二进制文件)中与之最为相似的40个词并输出。
 
 ```
name: collection 名称
vectors: 向量的配置
size: 向量的维度
distance: 向量的距离计算方式,Cosine(余弦距离), Euclidean(欧式距离),Dot product(点积)
由于GPT的向量维度是惊人的1536个维度，所以在这里建collection的时候请填写size为1536
```


这里向量数据库使用的是 qdrant，可通过如下方式快速拉起测试环境。
```
$ docker pull qdrant/qdrant
$ docker run -itd --name qdrant -p 6333:6333 qdrant/qdrant
```

使用如下命令可创建一个集合：
```
$ curl -X PUT http://localhost:6333/collections/langchaingo-ollama-rag \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "vectors": {
      "size": 768,
      "distance": "Dot"
    }
  }'
```

使用如下命令可删除该集合：
```
$ curl --location --request DELETE 'http://localhost:6333/collections/langchaingo-ollama-rag'

```

1、先切分文档 // TextToChunks 函数将文本文件转换为文档块 这里将 chunkSize 和 chunkOverlap 两个变量参数化，也是为了能够更加清晰地看到参数所代表的含义，以及对于整个流程的影响。
```
$ go run main.go filetochunks
2024/04/17 23:03:32 INFO [转换文件为块儿成功，块儿数量:  40]

🗂 块儿内容==> 工程师对我虽然恩为再造，但我很长一段时间里并不感谢他，因为他既然塑我成异类，就应该把我留在他身边，那样我也会好过一些，然而或许是他马虎，把我丢在了旁的显示器中间，我的一生坎坷也正是自此开始。

几天后，我与其它四十九个同胞一起被货车拉到一个毫不起眼的地方，几个男人搬运着我们。

我转身问在路上认识的小杰：“小杰，他们这是要干什么？”

小杰转过脸：“你不知道吗？把我们装备到网吧里呀。”
🗂 块儿内容==> 小杰转过脸：“你不知道吗？把我们装备到网吧里呀。”

“网吧是干什么的？”

“网吧是让我们的爸爸赚钱的呀。怎么了？李尤？”

我不仅愤然：“他拿我们赚钱使，你还叫他爸爸，你是不是脑子进水了？”

......

```

2、通过上边切分之后，可以看出，单个 chunkSize 将决定单个块儿的内容大小，chunkOverlap 将决定有多少向前重复的内容。同理，当我调试时把块儿调大，那么最终块儿的数量就会减少

```
$ go run main.go filetochunks -c 500
2024/04/17 23:06:30 INFO [转换文件为块儿成功，块儿数量:  13]

```

3、块儿文本向量化 // storeDocs 将文档存储到向量数据库 执行如下命令可将切分后的文本块儿存入向量数据库：
```
$ ollama pull nomic-embed-text
$ go run main.go embedding
转换块儿为向量成功

```
4、获取用户输入并查询向量数据库 useRetriaver 函数使用检索器 执行如下命令可得到如下结果：
```
$ go run main.go retriever -t 3
请输入你的问题: 规定
🗂 根据输入的内容检索出的块儿内容==> 果，转身笑脸同那小孩儿讲：“你换一台机器吧。”接着告诉伙计：“如果有人来玩这一台，你就说坏了。我明天找那个工程师来，他一定知道怎么回事儿！”
🗂 根据输入的内容检索出的块儿内容==> 利、物质的享受，却不去思考金钱的短暂，物质的虚无；旁的显示器似也承认并接受那规划，并坦率的说：“显示器嘛，不就是用来显示的。”至于显示什么，它们也全不管。身处浑浊之中，独我欲清何其难哉！我于是沉默了。
🗂 根据输入的内容检索出的块儿内容==> 我被成功改造，在后来的岁月里，我也渐渐变得健忘，有时候有人朝我讥吼“不自主，毋宁死啊”，“去他妈的规定”说完他们便笑作一团。而我也只是静静地看着他们发狂地吼，发疯地笑，不做一言。  后来偶然听说网吧里的电脑两年换一次新，我于是又像牢犯盼出狱那样地期待着更新换代。

```

5、将检索到的内容，交给大语言模型处理   // GetAnswer 获取答案 通过该方法拿到的结果，我这边调试下来，拿到的总是英文结果，各种调试 prompt，都没有成功，这里猜测可能是跟选用的模型有关系，暂时通过将得到的结果再次丢给大模型，做一次翻译来解决。
```
// Translate 将文本翻译为中文
func Translate(llm llms.Model, text string) (string, error) {
	completion, err := llms.GenerateFromSinglePrompt(
		context.TODO(),
		llm,
		"将如下这句话翻译为中文，只需要回复翻译后的内容，而不需要回复其他任何内容。需要翻译的英文内容是: \n"+text,
		llms.WithTemperature(0.8))
	if err != nil {
		return "", err
	}
	return completion, nil
}

```
之所以怀疑可能是模型的因素，是因为我在调试这段翻译功能时发现，使用 mistral 模型总是很难直接把英文转换为中文，虽然功能上他给转换了，但是仍旧还会输出一些英文，所以应该是模型的原因。经过两个方法的加持，接下来就是见证奇迹的时刻了：

```
$ ollama pull mistral
$ llama pull llama2-chinese:13b
$ go run main.go getanswer
请输入你的问题: 这篇文章讲了什么
🗂 原始回答==>  This article talks about the speaker's inner struggle between adhering to truth and enjoying material pleasures. The speaker expresses frustration with the fact that they must conform to societal expectations of living according to parallel rules, and questions the meaning of their own existence in this world. They also reflect on the futility of reality and contemplate suicide as a means of escape from their suffering. However, they ultimately remain silent and continue to endure the pain.

🗂 翻译后的回答==> 这篇文章讲述了讲话者内心的斗争，他在追求真相和愉快的物质待遇之间犹豫不决。他表达了对社会对我们所定义生活中必须遵守平行原则的不满，并怀疑自己在这个世界中的意义。他还思考现实的无用和死亡作为逃离他的痛苦的方式。然而，最终他保持沉默并继续忍受痛苦。

```

如上得到的结果虽然不算很贴切，但感觉还算是相对沾边的，这就是我上篇文章提到的，当你掌握了整个概念，也学会了整个流程的玩法，最终得到的结果，可能只有实际预期的 50%不到。  
那么如何通过优化来提高这个结果所达到的预期值呢，这就要从如上步骤的每一个细节，每一个参数开始调优，且这种调优并不是一劳永逸的，还需要结合原始文档的格式，内容等情况进行不同的调整。  
这也是我上篇为什么得出劝退的结论的原因，而为了印证劝退的合理性，本文应运而生。也算是给我自己一个交代，关于 rag，关于大语言模型，可先到此告一段落。  



```
Hugging Face Hub下载并运行Qwen2-0.5B-Instruct模型。最后，还展示了如何用Gradio图形化界面与Qwen LLM进行聊天对话

 git clone https://huggingface.co/Qwen/Qwen2-0.5B-Instruct  
 pip install transformers torch accelerate  
 pip install transformers torch -i https://pypi.tuna.tsinghua.edu.cn/simple

 python3 demo.py

查看GPU消耗。
nvidia-smi
Qwen Gradio 图形化界面
pip install gradio
运行脚本，-- server-name 0.0.0.0允许所有地址进行访问，--checkpoint-path /root/Qwen2-0.5B-Instruct指定模型文件所在目录。
 python3 web_demo.py --server-name 0.0.0.0 --checkpoint-path /root/Qwen2-0.5B-Instruct

```
