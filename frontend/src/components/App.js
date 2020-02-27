import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [walletInfo, setWalletInfo] = useState({});

  useEffect(() => {
    axios.get('http://localhost:5000/balance')
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
        <div>Address: {walletInfo.address}</div>
        <div>Address: {walletInfo.balance}</div>
      </div>
    </div>
  );
}

export default App;
