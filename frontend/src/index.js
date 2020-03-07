import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Switch, Route } from 'react-router-dom';
import './index.css';
import history from './history';
import App from './components/App';
import Blockchain from './components/Blockchain';
import Transact from './components/Transact';
import TransactionsPool from './components/TransactionsPool';

ReactDOM.render(
  <Router history={history}>
    <Switch>
      <Route path='/' exact component={App} />
      <Route path='/blockchain' component={Blockchain} />
      <Route path='/transact' component={Transact} />
      <Route path='/transactions-pool' component={TransactionsPool} />
    </Switch>
  </Router>,
  document.getElementById('root')
);
