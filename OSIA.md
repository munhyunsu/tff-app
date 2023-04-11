# 1. Introduction
- (10:30 ~ 11:30)

## Why federated learning
- cf. Homomorphic encryption: Even if learning is done in the compressed state, the parameters are learned to have the properties of data.
  - Cons: Slow even with hardware support!

### Things to consider when doing deep learning
- Overfitting: The model specialized for training data
  - Learning accuracy doesn't mean performance
- Good example) medical data with only one class
  - Advanced) Overfitting traffic identification model

### federated learning goals
- We can have the result (model) of learning with the data even without looking at the data of other edges.
- Maintaining deep learning computation performance
- Prohibiting duplicated data


# 2. Federated learning architectures and functionalities
- (11:30 ~ 12:30)

## Federated learning book
- [Advances and open problems in federated learning. arxiv. 2019](https://arxiv.org/abs/1912.04977)

### Difference of architectures (ref: above book)
- Datacenter distributed learning
- Cross-silo federated learning
- Cross-device federated learning

### Two major federated learning applications
- Medical platforms: Privacy issue
- Network platforms: communication overhead and reliability issue

### Data transmission in federated learning (Cross-silo)
- [XOR Mixup](https://arxiv.org/abs/2006.05148)

### Medical platform papers
- Privacy-preserving distributed deep learning computation

### Federated imitation learning


# 3. Federated learning in medical platform
- (13:30 ~ 14:20)

## The problems in medical platform federated learning
- Data imbalance
  - cf. IRB administration
- Duplicated data
- Data aging

### Split learning
- Input and one hidden layer, output layer learn only local data.
- The other layer federated learning on all of data.
- The back propagation consumes a lot of times because it needed data exchange with federated server.

### Cycling learning

### GAN: making fake data based on real data
- Data generation with limited patient data
- limitation: generated data do not have enough variance

#### GAN architecture
- Discriminator: Supervised learning based on real data
- Generator: Unsupervised learning based on the distribution of training data


# 4. Federated learning in network platform
- (14:20 ~ )

## Reinforced learning: Q-Learning
- Action taking into account rewards
  - Q(s, a) = r + maxQ(s`, a`)
- Deep learning based Q-leaning

### Imitation learning
- That is possible without knowing the reward value
- Focus on following the experts.
- Doing better than experts is not a goal!

### Federated learning average
- Federated learning average
- Weighted averaging with attention
