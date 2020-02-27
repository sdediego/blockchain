import React, { useState, useEffect } from 'react';

function Block({ block }) {
  const { index, timestamp, hash, data } = block;
  const timestampDisplay = new Date(timestamp).toLocaleString();

  return (
    <div className="Block">
      <div>Index: {index}</div>
      <div>Timestamp: {timestampDisplay}</div>
      <div>Hash: {hash}</div>
      <div>Data: {JSON.stringify(data)}</div>
    </div>
  );
}

export default Block;
