import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Blockchain from './Blockchain';
import Transact from './Transact';
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
      <br />
      <div className="WalletInfo">
        <div>Address: {address}</div>
        <div>Balance: {balance}</div>
      </div>
      <br />
      <Blockchain />
      <br />
      <Transact />
    </div>
  );
}

export default App;
