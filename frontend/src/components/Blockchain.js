import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import Block from './Block';
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
      <Link to="/">Home</Link>
      <hr />
      <header className="BlockchainHeader">
        <h3>Blockchain</h3>
      </header>
      <br />
      <div className="BlockchainChain">
        {blockchain.map(block => <Block key={block.hash} block={block} />)}
      </div>
    </div>
  );
}

export default Blockchain;
