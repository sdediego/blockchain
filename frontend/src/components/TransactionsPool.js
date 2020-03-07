import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from 'react-bootstrap';
import axios from 'axios';
import Transaction from './Transaction';
import { API_URL, TRANSACTIONS_INTERVAL } from '../config';
import history from '../history';

function TransactionsPool() {
  const [transactions, setTransactions] = useState([]);

  const getTransactions = () => {
    axios.get(`${ API_URL }/transactions`)
      .then(response => response.data)
      .then(data => {
        const transactions = data.transactions;
        setTransactions(transactions);
      });
  };

  const mineBlock = () => {
    axios.get(`${ API_URL }/mine`)
      .then(response => response.data)
      .then(data => {
        const block = data.block;
        alert(`Success! Block mined: ${ JSON.stringify(block.hash) }`);
        history.push('/blockchain');
      });
  };

  useEffect(() => {
    getTransactions();
    const intervalId = setInterval(getTransactions, TRANSACTIONS_INTERVAL);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="TransactionsPool">
      <Link to="/">Home</Link>
      <hr />
      <h3>Transactions Pool</h3>
      <div>
        {transactions.map(transaction => {
          return <div key={transaction.id}><hr /><Transaction transaction={transaction} /></div>;
        })}
      </div>
      <hr />
      <Button variant="primary" onClick={mineBlock}>Mine block</Button>
    </div>
  );
}

export default TransactionsPool;
