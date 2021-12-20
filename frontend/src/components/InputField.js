import React, { Component } from 'react';
import autosize from 'autosize';

class InputField extends Component {

    state = {
        aiHub: false,
        checked: true
    };

    handleAi = ()=>{
        this.setState({
            aiHub : !this.state.aiHub
        });
    }

    checkTxtarea = ()=>{
        if(document.getElementById("sum").value.length!==0){
            this.setState({
                aiHub : false
            });
        }
        else{
            this.setState({
                aiHib:true
            });
        }
    }

    handleChange=(e)=>{
        this.setState({
            checked : !this.state.checked
        });
    }
    
    componentDidMount() {
        this.textarea.focus();
        autosize(this.textarea);
    }

    render() {
        const style = {
            minHeight: '30px',
            resize: 'none',
            padding: '9px',
            boxSizing: 'border-box',
            fontSize: '15px'
        };

        return (
            <div>
                <form action="/" method="post" className="input-form" onSubmit={function (e) {
                    e.preventDefault();

                    const _models = e.target.model;
                    const _selected_list = [];
                    for (let i = 0; i < _models.length; i++) {
                        if (_models[i].checked) {
                            _selected_list.push(_models[i].value);
                        }
                    }
                    const _keyword = e.target.keyword1.value.trim();

                    let _numberOfSummary = [3, 1, 3, 3, 3];
                    const target1 = e.target.number1;
                    _numberOfSummary[0] = Number(target1.options[target1.selectedIndex].value);
                    _numberOfSummary[2] = _numberOfSummary[0];
                    _numberOfSummary[3] = _numberOfSummary[0];
                    _numberOfSummary[4] = _numberOfSummary[0];
                    
                    const boolValue = e.target.ai.checked;
                    this.props.onSubmit(_selected_list, _keyword, _numberOfSummary, boolValue);
                }.bind(this)}>
                    <label>Language Model</label>
                    <h3>Select Model</h3>
                    <label> | <input type="checkbox" name="model" value="KoBertSum" checked={this.state.checked} onChange={this.handleChange} />KoBertSum | </label>
                    &nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;
                    <label> | <input type="checkbox" name="model" value="MatchSum" />MatchSum | </label>
                    &nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;
                    <label> | <input type="checkbox" name="model" value="SummaRuNNer" />SummaRuNNer | </label>
                    &nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;
                    <label> | <input type="checkbox" name="model" value="TextRank" /> TextRank | </label>
                    &nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;
                    <label> | <input type="checkbox" name="model" value="LexRank" /> LexRank | </label>

                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    <select name="number1" id="number1">
                        <option value="3">요약문 개수 : 3</option>
                        <option value="4">요약문 개수 : 4</option>
                        <option value="5">요약문 개수 : 5</option>
                    </select>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

                    <br /><br /><br />
                    <h5>- Input</h5>
                    <textarea type="text" style={style} ref={c => this.textarea = c} id = "sum" name="keyword1" cols="80"
                        className="autosize" placeholder="Enter the naver news link or content of the news"></textarea>

                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;


                    <button type="submit" className="btn btn-primary" onClick = {this.checkTxtarea} >Summarize</button>
                    <br /><br />
                    <label><h5><input type="checkbox" name="ai" checked={this.state.aiHub} onChange={this.handleAi}></input>AIHUB 뉴스 기사 입력(랜덤)</h5></label>
                    <br /><br />
                </form>
                <br />
            </div>
        );
    }
}

export default InputField;