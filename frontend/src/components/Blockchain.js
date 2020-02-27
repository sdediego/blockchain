import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../config';

function Blockchain() {
  const [blockchain, setBlockchain] = useState([]);

  useEffect(() => {
    axios.get(`${ API_URL }/blockchain`)
      .then(response => response.data)
      .then(data => {
        const chain = data.blockchain.chain;
        setBlockchain(chain);
      });
  }, []);

  return (
    <div className="Blockchain">
      <header className="BlockchainHeader">
        <h3>Blockchain</h3>
      </header>
      <br />
      <div className="BlockchainChain">
        {blockchain.map(block => <div key={block.hash}>{JSON.stringify(block)}</div>)}
      </div>
    </div>
  );
}

export default Blockchain;
