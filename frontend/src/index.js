import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Switch, Route } from 'react-router-dom';
import { createBrowserHistory } from 'history';
import './index.css';
import App from './components/App';
import Blockchain from './components/Blockchain';
import Transact from './components/Transact';

ReactDOM.render(
  <Router history={createBrowserHistory()}>
    <Switch>
      <Route path='/' exact component={App} />
      <Route path='/blockchain' component={Blockchain} />
      <Route path='/transact' component={Transact} />
    </Switch>
  </Router>,
  document.getElementById('root')
);
