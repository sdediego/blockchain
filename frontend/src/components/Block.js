import React, { useState, useEffect } from 'react';
import Transaction from './Transaction';

function Block({ block }) {
  const { index, timestamp, hash, data } = block;
  const timestampDisplay = new Date(timestamp).toLocaleString();

  return (
    <div className="Block">
      <div>Index: {index}</div>
      <div>Timestamp: {timestampDisplay}</div>
      <div>Hash: {hash}</div>
      <hr />
      <div>Data: {data.map(transaction => <div key={transaction.id}><Transaction transaction={transaction} /></div>)}</div>
    </div>
  );
}

export default Block;
