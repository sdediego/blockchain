import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FormGroup, FormControl, Button } from 'react-bootstrap';
import axios from 'axios';
import { API_URL } from '../config';
import history from '../history';

function Transact() {
  const [amount, setAmount] = useState(0);
  const [recipient, setRecipient] = useState('');
  const [addresses, setAddresses] = useState([]);

  useEffect(() => {
    axios.get(`${ API_URL }/addresses`)
      .then(response => response.data)
      .then(data => {
        const addresses = data.addresses;
        setAddresses(addresses);
      });
  }, []);

  const updateAmount = event => {
    setAmount(Number(event.target.value));
  };

  const updateRecipient = event => {
    setRecipient(event.target.value);
  };

  const submitTransaction = () => {
    const config = { headers: { 'Content-Type': 'application/json' } };

    axios.post(`${ API_URL }/transact`, { recipient, amount }, config)
      .then(response => response.data)
      .then(data => {
        const output = data.transaction.output;
        alert(`Success! Transaction submitted: ${ JSON.stringify(output) }`);
        history.push('/transactions-pool');
      });
  };

  return (
    <div className="Transact">
      <Link to="/">Home</Link>
      <hr />
      <header className="TransactHeader">
        <h3>Make Transaction</h3>
      </header>
      <br />
      <FormGroup>
        <FormControl input="text" placeholder="recipient" value={recipient} onChange={updateRecipient} />
      </FormGroup>
      <FormGroup>
        <FormControl input="number" placeholder="amount" value={amount} onChange={updateAmount} />
      </FormGroup>
      <div>
        <Button variant="primary" onClick={submitTransaction}>Submit</Button>
      </div>
      <br />
      <h4>Addresses</h4>
      <div>
        <ul className="Addresses">
          {addresses.map((address, index) => <span key={address}><li>{address}</li></span>)}
        </ul>
      </div>
    </div>
  );
}

export default Transact;
