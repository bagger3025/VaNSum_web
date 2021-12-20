import React, { Component } from 'react';

class TextField extends Component {

    getGoldSummaryIdx(){
		const lists = [];
		if (!this.props.text || !this.props.goldsummary){
			return null;
		}
		for(let i = 0; i < this.props.text.length; i++){
			if (this.props.goldsummary.includes(this.props.text[i])){
				lists.push(i);
			}
		}
		return lists;
	}

    colorText(arr, colorStyle){
        if (!arr){
            return this.props.text.join(' ');
        } else {
            const lists = [];
            for (let i = 0; i < this.props.text.length; i++){
                if (arr.includes(i)){
                    lists.push(<span key={i} style={colorStyle}>{this.props.text[i]} </span>);
                } else {
                    lists.push(<span key={i}>{this.props.text[i]} </span>);
                }
            }
            return lists;
        }
    }

    getText() {
        const style = {
            backgroundColor: 'skyblue',
            color: "blue"
        };

        const goldStyle = {
            backgroundColor: "#FFE146",
            color: "#282828"
        };

        const overlapStyle = {
            backgroundColor: '#64CD3C',
            color: "black"
        };

        const goldSummary = this.getGoldSummaryIdx();

        if (!Array.isArray(this.props.text)) {
            return <span>{this.props.text}</span>;
        }

        if (goldSummary === null){
            return this.colorText(this.props.modelsummary, style);
        } else if(this.props.modelsummary === null){
            return this.colorText(goldSummary, goldStyle);
        } else {
            const lists = [];
            const intersection = goldSummary.filter(val => this.props.modelsummary.includes(val));
            for (let i = 0; i < this.props.text.length; i++){
                let _style;
                if (intersection.includes(i)){
                    _style = overlapStyle;
                } else if (goldSummary.includes(i)){
                    _style = goldStyle;
                } else if (this.props.modelsummary.includes(i)){
                    _style = style;
                }
                lists.push(<span key={i} style={_style}>{this.props.text[i]} </span>);
            }
            return lists;
        }
    }

    render() {
        return (
            <div>
                <h5>{this.props.title}</h5>
                <p className="sumArea">
                    {this.getText()}
                </p>
                <hr />
            </div>
        );
    }
}

export default TextField;