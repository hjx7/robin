# AI 从零开始学习详细知识路线图

下面是一份由浅入深、系统化的 AI 学习路线，分为 8 个阶段，每个阶段都包含学习目标、核心知识点和推荐资源。

---

## 阶段一：数学基础

**学习目标**：建立理解 AI 算法所需的数学直觉。

| 学科 | 核心内容 |
|------|----------|
| 线性代数 | 向量、矩阵运算、特征值/特征向量、SVD分解、矩阵求导 |
| 概率与统计 | 概率分布、贝叶斯定理、期望/方差、最大似然估计、假设检验 |
| 微积分 | 偏导数、链式法则、梯度、海森矩阵、泰勒展开 |
| 优化理论 | 凸优化基础、梯度下降法、拉格朗日乘子法 |

**推荐资源**：
- 《线性代数及其应用》(Gilbert Strang) + MIT 18.06 课程
- 《概率论与数理统计》(陈希孺)
- 3Blue1Brown《线性代数的本质》《微积分的本质》(B站可看)

---

## 阶段二：编程基础

**学习目标**：掌握 AI 工程实践的编程工具链。

### 2.1 Python 编程
- 基础语法、函数、面向对象
- 装饰器、生成器、迭代器
- 异常处理、文件 IO

### 2.2 数据结构与算法
- 列表/字典/集合的底层实现
- 排序、查找、递归
- 动态规划、图论基础（LeetCode 刷 100-200 题）

### 2.3 科学计算库
- **NumPy**：ndarray、广播机制、线性代数运算
- **Pandas**：DataFrame、数据清洗、聚合分析
- **Matplotlib / Seaborn**：数据可视化
- **Jupyter Notebook**：交互式开发环境

**推荐资源**：
- 《Python编程：从入门到实践》
- 廖雪峰 Python 教程
- Kaggle 的 Python 微课程

---

## 阶段三：机器学习基础

**学习目标**：理解经典 ML 算法原理，能独立完成建模任务。

### 3.1 核心概念
- 监督学习 / 无监督学习 / 半监督学习 / 强化学习
- 训练集/验证集/测试集、交叉验证
- 偏差-方差权衡、过拟合与欠拟合
- 评估指标：准确率、精确率/召回率、F1、AUC、MSE、MAE

### 3.2 经典算法
- **回归**：线性回归、岭回归、Lasso
- **分类**：逻辑回归、KNN、朴素贝叶斯、SVM、决策树
- **集成学习**：随机森林、GBDT、XGBoost、LightGBM
- **无监督**：K-Means、DBSCAN、层次聚类、PCA、t-SNE
- **降维**：PCA、LDA

### 3.3 实战工具
- **Scikit-learn**：模型训练、调参、Pipeline
- 特征工程：缺失值处理、编码、标准化、特征选择

**推荐资源**：
- 吴恩达 Machine Learning 课程（Coursera / B站）
- 《机器学习》(周志华)「西瓜书」
- 《Hands-On Machine Learning》(Aurélien Géron)
- Kaggle 入门竞赛（Titanic、House Prices）

---

## 阶段四：深度学习基础

**学习目标**：理解神经网络原理，掌握主流框架。

### 4.1 神经网络基础
- 感知机、多层感知机 (MLP)
- 激活函数：ReLU、Sigmoid、Tanh、GELU
- 反向传播算法、梯度消失/爆炸
- 损失函数：交叉熵、MSE、对比损失
- 优化器：SGD、Momentum、Adam、AdamW
- 正则化：Dropout、BatchNorm、LayerNorm

### 4.2 主流网络结构
- **CNN**：卷积、池化、LeNet / AlexNet / VGG / ResNet
- **RNN**：循环神经网络、LSTM、GRU、双向 RNN
- **Seq2Seq** + Attention 机制
- **Transformer**：Self-Attention、Multi-Head、Positional Encoding（必学重点）

### 4.3 深度学习框架
- **PyTorch**（首选推荐）：Tensor、autograd、nn.Module、DataLoader
- TensorFlow / Keras（了解即可）

**推荐资源**：
- 《动手学深度学习》(李沐，d2l.ai，B站有配套视频)
- 吴恩达 Deep Learning Specialization
- CS231n（CV方向）/ CS224n（NLP方向）斯坦福课程
- PyTorch 官方教程

---

## 阶段五：专业方向（按兴趣选择 1-2 个深入）

### 方向 A：计算机视觉 (CV)
- 图像分类、目标检测（YOLO、Faster R-CNN）
- 图像分割（U-Net、Mask R-CNN）
- 图像生成（GAN、Diffusion Model）
- 关键点检测、OCR

### 方向 B：自然语言处理 (NLP)
- 词向量：Word2Vec、GloVe
- 预训练模型：ELMo、BERT、GPT 系列
- 文本分类、序列标注、机器翻译
- 文本生成、摘要

### 方向 C：强化学习 (RL)
- MDP、Q-Learning、DQN
- Policy Gradient、PPO、A3C
- AlphaGo、RLHF（与 LLM 结合）

### 方向 D：语音/推荐系统
- 语音识别、TTS
- 协同过滤、深度推荐模型（DeepFM、Wide&Deep）

**推荐资源**：CS231n、CS224n、李宏毅深度学习课程（B站）

---

## 阶段六：大模型与 LLM（当前最热方向）[[阶段六学习计划]]

**学习目标**：掌握大语言模型的技术栈与应用能力。

### 6.1 基础理论
- Transformer 进阶（Decoder-only 架构）
- 预训练范式：CLM、MLM
- Scaling Law、涌现能力

### 6.2 主流开源模型
- LLaMA 系列、Qwen、ChatGLM、Mistral、Baichuan
- HuggingFace Transformers 库使用

### 6.3 微调技术
- 全参微调 (Full Fine-tuning)
- **PEFT**：LoRA、QLoRA、Adapter、P-Tuning
- 指令微调 (SFT)
- **RLHF / DPO**：人类反馈对齐

### 6.4 应用开发
- **Prompt Engineering**：CoT、Few-shot、ReAct
- **RAG**（检索增强生成）：向量数据库（FAISS/Milvus）、LangChain、LlamaIndex
- **Agent**：工具调用、多智能体、AutoGPT/MetaGPT
- **Function Calling / MCP**：标准化工具协议、Model Context Protocol
- **Skills**：能力封装机制，将特定领域能力标准化封装为 Agent 可调用的技能模块（类似插件/工具的标准化封装层）

**推荐资源**：
- 《大规模语言模型：从理论到实践》(复旦张奇团队)
- HuggingFace NLP Course
- LangChain 官方文档
- 李宏毅 LLM 课程（B站）

---

## 阶段七：工程实践与部署

**学习目标**：将模型落地为可用产品。

### 7.1 模型优化
- 量化 (Quantization)：INT8、INT4
- 剪枝 (Pruning)、蒸馏 (Distillation)
- 推理加速：TensorRT、vLLM、llama.cpp、ONNX

### 7.2 部署与服务
- REST API 服务：FastAPI、Flask
- 容器化：Docker、Kubernetes
- 模型服务框架：Triton、TorchServe

### 7.3 MLOps
- 实验管理：MLflow、Weights & Biases
- 数据/模型版本管理：DVC
- CI/CD for ML、监控与再训练

### 7.4 分布式训练
- 数据并行、模型并行、流水线并行
- DeepSpeed、Megatron-LM
- GPU 基础知识、CUDA 入门

---

## 阶段八：前沿跟进与持续学习

**学习目标**：保持对 AI 前沿的敏感度。

### 信息源
- **论文平台**：arXiv、Papers with Code、Google Scholar
- **顶会**：NeurIPS、ICML、ICLR、CVPR、ACL、EMNLP
- **社区**：HuggingFace、GitHub Trending、知乎、Twitter/X
- **公众号/博客**：机器之心、量子位、夕小瑶科技说

### 建议实践
- 每周精读 1-2 篇论文并做笔记
- 参与开源项目或 Kaggle 竞赛
- 复现经典模型代码
- 写技术博客输出（费曼学习法）

---

## 学习节奏建议

| 阶段 | 建议时长 | 产出目标 |
|------|----------|----------|
| 一、数学基础 | 4-6 周 | 能手算梯度、理解矩阵运算 |
| 二、编程基础 | 4-8 周 | 独立完成数据分析项目 |
| 三、机器学习 | 6-8 周 | Kaggle 拿到铜牌以上 |
| 四、深度学习 | 8-10 周 | 复现经典论文 + 完整项目 |
| 五、专业方向 | 8-12 周 | 1-2 个完整方向项目 |
| 六、大模型 | 持续 | 搭建 RAG 系统 / 微调模型 |
| 七、工程实践 | 4-6 周 | 模型部署上线 |
| 八、持续学习 | 长期 | 论文笔记 + 技术博客 |

---

## 关键原则

1. **理论与实践并行**：每学一个算法都动手实现一遍
2. **不要贪多**：先精通一条主线（如 Python → ML → DL → LLM），再横向扩展
3. **重视代码能力**：能跑通的代码比看懂的公式更重要
4. **读论文要趁早**：阶段四后就可以开始读经典论文
5. **建立作品集**：GitHub 上沉淀项目，比证书更有说服力
