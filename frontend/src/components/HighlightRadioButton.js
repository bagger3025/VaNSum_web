import React, { Component } from 'react';

class HighlightRadioButton extends Component {

    repreRadioButton(value) {
		if (this.props.result[value].time !== -1) {
			return <label key={value}>&nbsp; &nbsp; &nbsp; &nbsp;<input type="radio" name="highlight" checked={this.props.val === value} onChange={function() {
                this.props.onClick(value);
            }.bind(this)}></input> {this.props.result[value].type} Highlight </label>
		}
		else {
			return <span key={value}></span>
		}
	}

    modelHighlights(){
        const _lists = [];
        for(let i = 0; i < this.props.result.length; i++){
            _lists.push(this.repreRadioButton(i))
        }
        return _lists;
    }
    render(){

        return(
            <div>
                <label key={-1}><input type="radio" name="highlight" checked={this.props.val === -1} onChange={() => this.props.onClick(-1)}></input> All Result </label>
                {this.modelHighlights()}
                <hr></hr>
            </div>
        );
    }
}

export default HighlightRadioButton;