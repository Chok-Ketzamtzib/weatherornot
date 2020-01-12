﻿import React, { Component } from "react";
import { Route, Switch } from "react-router-dom";
import "./App.css";
import NavBar from "./components/NavBar";
import Footer from "./components/Footer";

import Grid from "./components/Grid";

//TODO Web Template Studio: Add routes for your new pages here.
class App extends Component {
  render() {
    return (
      <React.Fragment>
        <NavBar />
        <Switch>
          <Route exact path = "/" component = { Grid } />
        </Switch>
        <Footer />
      </React.Fragment>
    );
  }
}

export default App;