# tff-app
- Federated learning based app

## Packet to image (pkt2vec)
  ```bash
  python3 00-Preprocessing.py
  ```
  or
  ```bash
  00-Preprocessing.ipynb
  ```
  - Image with 39 x 39 x 1 from ip layer  


## Packet Classification Baseline
  ```bash
  02-TCBaselineCNN.ipynb
  ```

  - Models
  
    


## Federated Server

### Requirements
  ```bash
  pip3 install --upgrade -r requirements.txt
  ```

  - Install scrcpy


### Usage
  1. Preprocessing pcap files for creating feature vectors

  ```bash
  python3 01-preprocess.py -i INPUTDIR -o OUTPUTDIR
  ```

  2. Make dataset for federated learning
    
    - 

  ```bash
  python3 02-...
  ```



## Edge Client

### Requirements
  ```bash
  pip3 install -r requirements.txt
  ```

### Usage
  1. ...


### References
[Federated Optimization: Distributed Optimization Beyond the Datacenter](https://research.google/pubs/pub44310/)
[Communication-Efficient Learning of Deep Networks from Decentralized Data
](https://research.google/pubs/pub44822/)

## Coded by
- LuHa (munhyunsu@gmail.com)

