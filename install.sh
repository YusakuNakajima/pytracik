# local install nlopt (for using newest version) 
curl -O https://codeload.github.com/stevengj/nlopt/tar.gz/v2.7.0 && tar xzvf v2.7.0 && cd nlopt-2.7.0
cmake . && make && sudo make install

# install pip packages
pip install -r requirements.txt
pip install -e .
