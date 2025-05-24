# local install nlopt (for using newest version)
mkdir tmp
cd tmp
curl -O https://codeload.github.com/stevengj/nlopt/tar.gz/v2.7.0 && tar xzvf v2.7.0 && cd nlopt-2.7.0
# The following commands modify system directories, so they need sudo
sudo cmake .
sudo make
sudo make install
cd ../../
sudo rm -r tmp
# install pip packages (assuming you are in a virtual environment as per your previous request)
python3 -m pip install -r requirements.txt
python3 -m pip install -e .