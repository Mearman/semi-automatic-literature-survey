#!/bin/bash

python -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install --upgrade setuptools wheel

# # PyYAML==6.0
# # pandas==1.4.3
# # spacy-langdetect==0.1.2
# # spacy==3.4.1
# # elsapy==0.5.0
# # gensim==4.2.0
# # lbl2vec==1.0.1
# # nltk==3.7
# # lxml==4.9.1
# # rich==13.4.2

# brew install libxslt libxml2

brew install libxml2
brew install libxslt

brew link libxml2 --force
brew link libxslt --force

pip install lxml --only-binary lxml

export LDFLAGS="-L/opt/homebrew/opt/libxml2/lib"
export CPPFLAGS="-I/opt/homebrew/opt/libxml2/include"
gem install nokogiri -- --with-xslt-dir=/opt/homebrew/opt/libxslt

# export LDFLAGS="-L/opt/homebrew/opt/libxslt/lib"
# export CPPFLAGS="-I/opt/homebrew/opt/libxslt/include"
# xcode-select --install
# STATIC_DEPS=true pip install lxml
# STATIC_DEPS=true pip install lxml

# pip install PyYAML==6.0
# pip install spacy-langdetect==0.1.2
# pip install spacy==3.4.1
# pip install elsapy==0.5.0
# pip install gensim==4.2.0
# pip install lbl2vec==1.0.1
# pip install nltk==3.7
# pip install lxml==4.9.1
# pip install rich==13.4.2
# pip install pandas==1.4.3

# python -m spacy download en_core_web_sm

pip install -r requirements.txt -v
