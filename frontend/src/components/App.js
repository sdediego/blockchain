import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API_URL } from '../config';

function App() {
  const [walletInfo, setWalletInfo] = useState({});
  const { address, balance } = walletInfo;

  useEffect(() => {
    axios.get(`${ API_URL }/balance`)
      .then(response => response.data)
      .then(data => setWalletInfo(data));
  }, []);

  return (
    <div className="App">
      <header className="AppHeader">
        <h3>Welcome to Blockchain</h3>
      </header>
      <Link to="/blockchain">Blockchain</Link>
      <Link to="/transact">Transact</Link>
      <Link to="/transactions-pool">Transactions Pool</Link>
      <br />
      <div className="WalletInfo">
        <div>Address: {address}</div>
        <div>Balance: {balance}</div>
      </div>
    </div>
  );
}

export default App;
