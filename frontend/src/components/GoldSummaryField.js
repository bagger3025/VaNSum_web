import React, { Component } from 'react';

class GoldSummaryField extends Component {

    getText() {
        if (Array.isArray(this.props.text)) {
            const newlist = [];
            for (let i = 0; i < this.props.text.length; i++){
                newlist.push(<br key={i * 2}/>);
                newlist.push(this.props.text[i]);
                newlist.push(<br key = {i * 2 + 1}/>);
            }
            newlist.splice(0,1);
            return <span>{newlist}</span>;
        } else {
            return <span>{this.props.text}</span>;
        }
    }

    render() {
        if (this.props.title === "Naver Summary" && this.props.text === "No Gold Summary") {
            return (<div></div>);
        }
        return (
            <div>
                <h5 style={{ backgroundColor: '#FFE146', color: '#282828', display: 'inline-block' }}>{this.props.title}</h5>
                <p className="sumArea">{this.getText()}</p>
                <hr />
            </div>
        );
    }
}

export default GoldSummaryField;