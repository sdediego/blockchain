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
From the backend directory:
```sh
uvicorn src.app.api:app --reload --port 5000
```
