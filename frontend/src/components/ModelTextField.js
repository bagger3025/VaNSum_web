import React, { Component } from 'react';

class ModelTextField extends Component {

    constructor(props) {
        super(props);
        this.state = {
            value: 2, // 1:확률순 또는 2: 문장순으로 나뉜다.
        };
    }

    handleRadioButton(value) {
        this.setState({
            value: value
        });
    }

    calSimilarity() {

        if (!this.props.gs || !this.props.result.summary) {
            return <span>loading...</span>;
        }

        if (this.props.gs === "No Gold Summary" || this.props.gs === "This article does not support Naver Summary Bot.") {
            return <span>No GoldSummary</span>;
        }

        let similarity = 0;
        const _summary = (this.props.result.type === "MatchSum") ? this.props.result.summary[this.props.mtchSumIdx] : this.props.result.summary;

        for (let i = 0; i < _summary.length; i++) {
            for (let j = 0; j < this.props.gs.length; j++) {
                if (this.props.textlist[_summary[i]] === this.props.gs[j]) {
                    similarity += 1;
                    break;
                }
            }
        }

        //return <span>|{this.props.gs[0]}|{this.props.textlist[this.props.result.summary[0]]}</span>
        return <span style={{ backgroundColor: '#64CD3C', color: "black",  }}>{similarity} sentence(s) same with gold summary. </span>
    }

    sentences() {//value 가 1이냐 2에 따라 반환하는 순서를 다르게 한다.(if문 사용하면)
        if(this.props.result.summary === null){
            return <span><br></br><br></br><br></br><br></br><br></br><br></br></span>;
        }
        
        if (this.props.result.type === "MatchSum") {
            const screen_sentences = [];
            this.props.result.summary.map((sum, idx) => {
                if (Array.isArray(sum)) {
                    screen_sentences.push(<span key={idx * 4}>{idx + 1}. (score : {this.props.result.prob[idx]})<br></br></span>)
                    sum.map((line, index) => {
                        screen_sentences.push(<span key={idx * 4 + index + 1}>{this.props.textlist[line]}<br></br><br></br></span>);
                        return true;
                    });
                    return true;
                } else {
                    return true;
                }
            });
            if (screen_sentences.length === 0) {
                return <span><br></br><br></br><br></br><br></br><br></br><br></br></span>;
            }
            return screen_sentences;
        }

        if (this.state.value === 1) { //확률순 요약 결과
            return this.props.result.summary.map((line, index) => {
                return <span key={index}>{this.props.textlist[line]} (score : {this.props.result.prob[index]})<br></br><br></br></span>;
            });
        }

        if (this.state.value === 2) {
            let mapped = this.props.result.summary.map((el, i) => {
                return {
                    index: i,
                    value: el
                };
            });
            mapped.sort((a, b) => a.value - b.value);

            const sentence_sorted = mapped.map(el => this.props.result.summary[el.index]);
            const probs_sorted = mapped.map(el => this.props.result.prob[el.index]);
            return sentence_sorted.map((line, index) =>
                <span key={index}>{this.props.textlist[line]}  (score : {probs_sorted[index]}) <br></br><br></br></span>
            );
        }
        else {
            return <span><br></br></span>;
        }
    }

    printTime() {
        if (this.props.result.time < 0) {
            return ' ';
        } else {
            return `${Math.round(this.props.result.time * 100) / 100} s`;
        }
    }

    makeRadioButton() {
        if (this.props.result.type === "MatchSum") {
            return <span></span>;
        }

        return (
            <span>
                <label> |
                    <input
                        type="radio"
                        checked={this.state.value === 2}
                        onChange={() => this.handleRadioButton(2)}
                    ></input>
                    문장순 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                </label>
                <label> |
                    <input
                        type="radio"
                        checked={this.state.value === 1}
                        onChange={() => this.handleRadioButton(1)}
                    ></input>
                    점수(score)순 |
                </label>
            </span>
        );
    }

    render() {
        return (
            <div>
                <h5 style={{ color: "blue", backgroundColor: "skyblue", display: "inline-block" }}>{this.props.result.type}</h5>

                <div style={{ verticalAlign: "middle", overflow: "hidden" }}>

                    {this.makeRadioButton()}
                    <div style={{ float: 'right'}}>
                        {this.printTime()}
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        {this.calSimilarity()}
                    </div>
                </div>
                <p className="sumArea">
                    {this.sentences()}
                </p>
                <hr />
            </div >
        );
    }
}

export default ModelTextField;