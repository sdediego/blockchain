# Blockchain


### Backend

#### Activate virtualenv
Create a virtual environment called blockchain.
Then execute:
```sh
source .virtualenvs/blockchain/bin/activate
```

#### Install dependencies
Make sure that the virtual environment is activated.
From the backend directory:
```sh
pip install -r requirements.txt
```

#### Run tests
Make sure that the virtual environment is activated.
From the backend directory:

To run the complete tests suite execute:
```sh
tox
```

To run a particular test case execute:
```sh
python -m unittest tests.<tests_directory>.<test_file>.<test_case>
```

#### Run application
Make sure that the virtual environment is activated.
Start several application instances in localhost.
From the backend directory in different terminals:
```sh
python -m src.bin.www -ap 5000 -pp 6000
python -m src.bin.www -ap 5001 -pp 6001 -n "ws://127.0.0.1:6000"
python -m src.bin.www -ap 5002 -pp 6002 -n "ws://127.0.0.1:6000, ws://127.0.0.1:6001"
```
where  
ap = api port  
pp = p2p server port  
n  = already known p2p nodes uris  
