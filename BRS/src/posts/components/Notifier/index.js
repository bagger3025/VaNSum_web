import React, { Component } from "react";
import "./Notifier.css";

class Notifier extends Component {
  render() {
    return (
      <div className="notify">
        <p>
          <em>{this.props.data}</em>
        </p>
      </div>
    );
  }
}

export default Notifier;
