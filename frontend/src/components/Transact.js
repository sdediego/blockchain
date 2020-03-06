import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FormGroup, FormControl, Button } from 'react-bootstrap';
import axios from 'axios';
import { API_URL } from '../config';

function Transact() {
  const [amount, setAmount] = useState(0);
  const [recipient, setRecipient] = useState('');

  const updateAmount = event => {
    setAmount(Number(event.target.value));
  };

  const updateRecipient = event => {
    setRecipient(event.target.value);
  };

  const submitTransaction = () => {
    axios.get(`${ API_URL }/transact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient, amount })
    }).then(response => response.data)
      .then(data => {
        console.log('submitTransaction JSON', data);
        alert('Success!');
      });
  };

  return (
    <div className="Transact">
      <Link to="/">Home</Link>
      <hr />
      <header className="TransactHeader">
        <h3>Conduct a Transaction</h3>
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
    </div>
  );
}

export default Transact;
