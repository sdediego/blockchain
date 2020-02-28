import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import Transaction from './Transaction';

function ToogleBlock({ block }) {
  const [displayTransaction, setDisplayTransaction] = useState(false);
  const { data } = block;

  const toggleDisplayTransaction = () => {
    setDisplayTransaction(!displayTransaction);
  }

  if (displayTransaction) {
    return (
      <div>
        {data.map(transaction => <div key={transaction.id}><Transaction transaction={transaction} /></div>)}
        <br />
        <Button variant="primary" size="sm" onClick={toggleDisplayTransaction}>Show Less</Button>
      </div>
    );
  }

  return (
    <div>
      <br />
      <Button variant="primary" size="sm" onClick={toggleDisplayTransaction}>Show More</Button>
    </div>
  );
}

function Block({ block }) {
  const { index, timestamp, hash } = block;
  const timestampDisplay = new Date(timestamp).toLocaleString();

  return (
    <div className="Block">
      <div>Index: {index}</div>
      <div>Timestamp: {timestampDisplay}</div>
      <div>Hash: {hash}</div>
      <hr />
      <div>Data: <ToogleBlock block={block} /></div>
    </div>
  );
}

export default Block;
