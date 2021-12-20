import React, { Component } from 'react';
import TextField from './components/TextField'
import ModelTextField from './components/ModelTextField'
import InputField from './components/InputField'
import GoldSummaryField from './components/GoldSummaryField'
import AbsInputField from './components/AbsInputField'
import TitleInputField from './components/TitleInputField'
import PegasusField from './components/PegasusField';
import Logo_SKKU_32 from './Logo_SKKU_32.ico'
import SummaInputField from './components/SummaInputField';
import './style.css'
import {BrowserRouter as Router, Route, Redirect} from 'react-router-dom';
import HighlightRadioButton from './components/HighlightRadioButton';

// import SignPage from './pages/SignPage ';


const URL_TO_API = "http://112.175.32.78:443";

class App extends Component {
	constructor(props) {
		super(props);
		this.id = 0;
		this.state = {
			onoff: false,
			val: -1, 				// -1 : all, 0부터 모델 순서에 따름
			mtchHighlightSen: 0, 	// MatchSum 세트번호
			mode: "input",			// ['input', 'result']
			selected_models: [""],
			inputs: [
				{
					type: "Input Text",
					key: -1,
					text: null,
				},
				{
					type: "Naver Summary",
					key: -2,
					text: null,
				}
			],
			result: [
				{
					type: "KoBertSum",
					key: 0,
					summary: null,
					time: -1,
					prob: [],
				},
				{
					type: "MatchSum",
					key: 1,
					summary: null,
					time: -1,
					prob: [],
				},
				{
					type: "SummaRuNNer",
					key: 2,
					summary: null,
					time: -1,
					prob: [],
				},
				{
					type: "TextRank",
					key: 3,
					summary: [],
					time: -1,
					prob: [],
				},
				{
					type: "LexRank",
					key: 4,
					summary: null,
					time: -1,
					prob: [],
				}
			]
		};
		this.handleClick = this.handleClick.bind(this);
		this.resetFields();

		this.apiURL = ["/api/KoBertSum", "/api/MatchSum", "/api/SummaRuNNer", "/api/TextRank", "/api/LexRank"];
		for (let i = 0; i < this.apiURL.length; i++) {
			this.apiURL[i] = URL_TO_API + this.apiURL[i];
		}
		console.assert(this.state.result.length === this.apiURL.length, "Should be same length between models and apiurls.");
	}

	resetFields() {
		this.setState({
			inputs: [
				{
					type: "Input Text",
					key: -1,
					text: null,
				},
				{
					type: "Naver Summary",
					key: -2,
					text: null,
				}
			],
			result: [
				{
					type: "KoBertSum",
					key: 0,
					summary: null,
					time: -1,
					prob: [],
				},
				{
					type: "MatchSum",
					key: 1,
					summary: null,
					time: -1,
					prob: [],
				},
				{
					type: "SummaRuNNer",
					key: 2,
					summary: null,
					time: -1,
					prob: [],
				},
				{
					type: "TextRank",
					key: 3,
					summary: [],
					time: -1,
					prob: [],
				},
				{
					type: "LexRank",
					key: 4,
					summary: null,
					time: -1,
					prob: [],
				}
			]
		});
	}

	getRequest(jsons){
		return {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Access-Control-Allow-Origin': '*',
				'Access-Control-Allow-Headers': '*'
			},
			body: JSON.stringify(jsons)
		};
	}

	getTextSummary(text, cur_id, number) {
		if (cur_id !== this.id) {
			console.log("id is different!");
			return;
		}

		let _inputs = Array.from(this.state.inputs);
		_inputs[0].text = text;
		this.setState({ inputs: _inputs });

		for (let i = 0; i < this.state.result.length; i++) {
			if (!this.state.selected_models.includes(this.state.result[i].type)) {
				continue;
			}
			const requestOpt = this.getRequest({text: text, topk: number[i], sort: "prob",});
			fetch(this.apiURL[i], requestOpt).then(response => response.json()).then(jsons => {
				if (cur_id !== this.id) {
					console.log("id is different!");
					return;
				}
				let _result = Array.from(this.state.result);
				_result[i].summary = jsons["summary"];
				if (Array.isArray(jsons["summary"])) {
					_result[i].time = jsons["time"];
					_result[i].prob = jsons["prob"].map(ele => Math.round(ele * 1000) / 1000);
				} else {
					_result[i].summary = jsons["summary"];
				}
				this.setState({ result: _result });
			});
		}
	}

	getSummary(models, keyword, number, aiHub) { //number 추가
		this.setState({
			mode: "result",
			selected_models: models,
		});
		this.id += 1;
		const cur_id = this.id;
		// eslint-disable-next-line
		const regex = /(http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
		if (aiHub === true) {
			const b = Math.floor(Math.random() * 3000);
			const requestOpt = this.getRequest({random: b, "type":"ext"});
			fetch(URL_TO_API + "/api/aiHub", requestOpt).then(response => response.json()).then(jsons => {
				let list = [];
				jsons['extractive'].forEach(item => {
					list.push(jsons['article_original'][item]);
				});
				let _inputs = Array.from(this.state.inputs);
				_inputs[1].text = list;
				_inputs[1].type = "Gold Summary";
				_inputs[0].text = jsons['article_original'];
				this.setState({
					inputs: _inputs
				});
				this.getTextSummary(this.state.inputs[0].text, cur_id, number);
			});
		} else if (regex.test(keyword)) {
			if (keyword.startsWith("https://n.news.naver.com/")) {
				const startsurl = keyword.split('?')[0].split("/");
				const oid = startsurl[startsurl.length - 2];
				const aid = startsurl[startsurl.length - 1];
				keyword = `https://news.naver.com/main/read.naver?oid=${oid}&aid=${aid}`;
			}
			const requestOpt = this.getRequest({url: keyword,});
			fetch(URL_TO_API + "/api/original_text", requestOpt).then(response => response.json()).then(jsons => {
				console.log("navernews original article: ");
				console.log(jsons["text"]);
				this.getTextSummary(jsons["text"], cur_id, number);
			});
			fetch(URL_TO_API + "/api/naver_summary", requestOpt).then(response => response.json()).then(jsons => {
				if (this.id === cur_id) {
					let _inputs = Array.from(this.state.inputs);
					_inputs[1].type = "Naver Summary";
					_inputs[1].text = jsons["sent_list"];
					console.log("naver summary:", jsons["sent_list"]);
					this.setState({
						inputs: _inputs
					});
				} else {
					console.log("id is different!");
				}
			});
		} else {
			const requestOpt = this.getRequest({text: keyword});
			fetch(URL_TO_API + "/api/split_sentences", requestOpt).then(response => response.json()).then(jsons => {
				this.getTextSummary(jsons["sent_list"], cur_id, number);
			});

			let _inputs = Array.from(this.state.inputs);
			_inputs[1].text = "No Gold Summary";
			this.setState({
				inputs: _inputs
			});
		}
	}

	handleClick() {
		this.setState({
			onoff: !this.state.onoff
		});
	}

	showGold() {
		if (this.state.inputs[1].text !== "No Gold Summary")
			return <label><input type="checkbox" name="onoffGoldSum" checked={this.state.onoff} onChange={this.handleClick}></input> {this.state.inputs[1].type} Check </label>
		else
			return <span></span>
	}

	render() {
		let _main, _footer;
		if (this.state.mode === 'input') {
			_footer = <footer className="footer">
				{/* <img src={Logo_SKKU_32} alt="logo" className="logo" /> */}
				<img src className="skkuimg" alt = "skkulogo" src = "img/skku_logo.png"/>
				{/* <div>2021 성균관대학교 산학협력프로젝트 테스트사이트</div> */}
				<br></br>
				{/* <div><img src="https://storage.googleapis.com/chrome-gcs-uploader.appspot.com/image/WlD8wC6g8khYWPJUsQceQkhXSlv1/UV4C4ybeBTsZt43U4xis.png" alt="Available in the Chrom Web Store"></img></div> */}
			</footer>
		} else if (this.state.mode === 'result') {
			let _models = [];
			for (let _model of this.state.result) {
				if (this.state.selected_models.includes(_model.type)) {
					_models.push(
						<ModelTextField
							key={_model.key}
							result={_model}
							textlist={this.state.inputs[0].text}
							gs={this.state.inputs[1].text}
							mtchSumIdx={this.state.mtchHighlightSen}
						/>
					);
				} 
				else {
					_models.push(<div key={_model.key}></div>);
				}
			}
			
			let _modelSummary = null;
			if (this.state.val !== -1){
				_modelSummary = this.state.result[this.state.val].summary;
				if (_modelSummary && this.state.result[this.state.val].type === "MatchSum"){
					_modelSummary = _modelSummary[this.state.mtchHighlightSen];
				}
			}
				
			const _inputs = [
				<TextField
					key={this.state.inputs[0].key}
					title={this.state.inputs[0].type}
					text={this.state.inputs[0].text}
					goldsummary={this.state.onoff ? this.state.inputs[1].text : null}
					modelsummary={_modelSummary}
				/>,
				<GoldSummaryField
					key={this.state.inputs[1].key}
					title={this.state.inputs[1].type}
					text={this.state.inputs[1].text}
				/>
			];

			if (this.state.val !== -1) {
				_models = _models[this.state.val];
			}

			_main = (
				<div className="grid">
					<div className="left-box" id="left_div">
						{this.showGold()}
						{_inputs}
					</div>
					<div className="right-box" id="right_div">
						<HighlightRadioButton result={this.state.result} val={this.state.val} onClick={function(value){
							this.setState({
								val: value
							});
						}.bind(this)}/>
						{_models}
					</div>
				</div>);
		}

		return (
			<div className="">
				<Router>
					<Route exact path = "/">
						<Redirect to ="/home" />
					</Route>
					<Route path = "/contact" >
						<section className="sidenav">
						<div style ={{paddingTop:'70px'}}>
							<a href="/home" ><span style = {{color:'black', fontSize:'20px'}} >추출식(kor)</span></a>
							<hr/>
							<a href="/abstractive"><span style = {{color:"black", fontSize:'20px'}}>생성식(kor)</span></a>
							<hr/>
							<a href="/pegasus" ><span style = {{ color:"black", fontSize:'20px'}}>생성식(eng)</span></a>
							<hr/>
							<a href="/contact" ><span style = {{color:"white", fontSize:'20px'}}>Contact</span></a>
							</div>
							<hr/>
							<a href = "/KobertSum"><span style = {{color:"black", fontSize:'20px'}}>BertSumExt<br/>(제목)</span></a>
							<hr/>
							<a href = "/SummaRuNNer"><span style = {{color:"black", fontSize:'20px'}}>Summa<br/>RuNNer<br/>(제목)</span></a>
						</section>
						<section className="main">
							<header>
								<a href="/home"><img src className="skkuimg" alt = "vaivlogo" src = "img/vaiv_news.png"/></a>
								<h2 style = {{textAlign:"center"}}>성균관대학교 & 바이브 컴퍼니</h2>
							</header>

						<div style ={{fontSize : '3rem', textAlign:'center', fontFamily:'Arial'}}>
							<div style = {{fontSize : '1.5rem', marginLeft: '20px'}}>
								<p style = {{padding : '1px'}}>가수연(팀장) - email : bagger3025@g.skku.edu</p>
								<br></br>
								<p style ={{padding : '1px'}}>김동건 - email : kdk0@g.skku.edu</p>
								<br></br>
								<p style ={{padding : '1px'}}>김용 - email : skystar2345@g.skku.edu</p>
								<br></br>
								<p style ={{padding : '1px'}}>송현빈 - email : shbin05@g.skku.edu</p>
								<br></br>
								<p style ={{padding : '1px'}}>차현묵 - email : mook0227@g.skku.edu</p> 
							</div>
						</div>
						</section>
						
						{_footer}
					</Route>
					<Route path = "/home">
					<section className="sidenav">
						<div style ={{paddingTop:'70px'}}>
							<a href="/home" ><span style = {{color:'white', fontSize:'20px'}} >추출식(kor)</span></a>
							<hr/>
							<a href="/abstractive"><span style = {{color:"black", fontSize:'20px'}}>생성식(kor)</span></a>
							<hr/>
							<a href="/pegasus" ><span style = {{ color:"black", fontSize:'20px'}}>생성식(eng)</span></a>
							<hr/>
							<a href="/contact" ><span style = {{color:"black", fontSize:'20px'}}>Contact</span></a>
							</div>
							<hr/>
							<a href = "/KobertSum"><span style = {{color:"black", fontSize:'20px'}}>BertSumExt<br/>(제목)</span></a>
							<hr/>
							<a href = "/SummaRuNNer"><span style = {{color:"black", fontSize:'20px'}}>Summa<br/>RuNNer<br/>(제목)</span></a>
						</section>
						<section className="main">
							<header>
								{/* <h2>VaNSum</h2>
								<h6>Vaiv News Summary</h6> */}
								<a href="/home"><img src className="skkuimg" alt = "vaivlogo" src = "img/vaiv_news.png"/></a>
							</header>
							<InputField onSubmit={function (models, keyword, number, aiHub) {
								this.resetFields();
								this.getSummary(models, keyword, number, aiHub);
							}.bind(this)}/>
							{_main}
						</section>
						{_footer}
					</Route>
					<Route path = "/abstractive">
					<section className="sidenav">
						<div style ={{paddingTop:'70px'}}>
							<a href="/home" ><span style = {{color:'black', fontSize:'20px'}} >추출식(kor)</span></a>
							<hr/>
							<a href="/abstractive"><span style = {{color:"white", fontSize:'20px'}}>생성식(kor)</span></a>
							<hr/>
							<a href="/pegasus" ><span style = {{ color:"black", fontSize:'20px'}}>생성식(eng)</span></a>
							<hr/>
							<a href="/contact" ><span style = {{color:"black", fontSize:'20px'}}>Contact</span></a>
							</div>
							
							<hr/>
							<a href = "/KobertSum"><span style = {{color:"black", fontSize:'20px'}}>BertSumExt<br/>(제목)</span></a>
							<hr/>
							<a href = "/SummaRuNNer"><span style = {{color:"black", fontSize:'20px'}}>Summa<br/>RuNNer<br/>(제목)</span></a>
						</section>
						<section className="main">
							<header>
								<a href="/home/"><img src className="skkuimg" alt = "vaivlogo" src = "img/vaiv_news.png"/></a>
							</header>
							<AbsInputField/>
							
						</section>
					</Route>
					<Route path = "/KobertSum">
					<section className="sidenav">
						<div style ={{paddingTop:'70px'}}>
							<a href="/home" ><span style = {{color:'black', fontSize:'20px'}} >추출식(kor)</span></a>
							<hr/>
							<a href="/abstractive"><span style = {{color:"black", fontSize:'20px'}}>생성식(kor)</span></a>
							<hr/>
							<a href="/pegasus" ><span style = {{ color:"black", fontSize:'20px'}}>생성식(eng)</span></a>
							<hr/>
							<a href="/contact" ><span style = {{color:"black", fontSize:'20px'}}>Contact</span></a>
							</div>
							<hr/>
							<a href = "/KobertSum"><span style = {{color:"white", fontSize:'20px'}}>BertSumExt<br/>(제목)</span></a>
							<hr/>
							<a href = "/SummaRuNNer"><span style = {{color:"black", fontSize:'20px'}}>Summa<br/>RuNNer<br/>(제목)</span></a>
						</section>
						<section className="main">
							<header>
								<a href="/home"><img src className="skkuimg" alt = "vaivlogo" src = "img/vaiv_news.png"/></a>
							</header>
							<TitleInputField/>
							
						</section>
					</Route>
					<Route path = "/SummaRuNNer">
					<section className="sidenav">
						<div style ={{paddingTop:'70px'}}>
							<a href="/home" ><span style = {{color:'black', fontSize:'20px'}} >추출식(kor)</span></a>
							<hr/>
							<a href="/abstractive"><span style = {{color:"black", fontSize:'20px'}}>생성식(kor)</span></a>
							<hr/>
							<a href="/pegasus" ><span style = {{ color:"black", fontSize:'20px'}}>생성식(eng)</span></a>
							<hr/>
							<a href="/contact" ><span style = {{color:"black", fontSize:'20px'}}>Contact</span></a>
							</div>
							
							<hr/>
							<a href = "/KobertSum"><span style = {{color:"black", fontSize:'20px'}}>BertSumExt<br/>(제목)</span></a>
							<hr/>
							<a href = "/SummaRuNNer"><span style = {{color:"white", fontSize:'20px'}}>Summa<br/>RuNNer<br/>(제목)</span></a>
						</section>
						<section className="main">
							<header>
							<a href="/home"><img src className="skkuimg" alt = "vaivlogo" src = "img/vaiv_news.png"/></a>
							</header>
							<SummaInputField/>
							
						</section>
					</Route>
					<Route path = "/pegasus">
					<section className="sidenav">
						<div style ={{paddingTop:'70px'}}>
							<a href="/home" ><span style = {{color:'black', fontSize:'20px'}} >추출식(kor)</span></a>
							<hr/>
							<a href="/abstractive"><span style = {{color:"black", fontSize:'20px'}}>생성식(kor)</span></a>
							<hr/>
							<a href="/pegasus" ><span style = {{ color:"white", fontSize:'20px'}}>생성식(eng)</span></a>
							<hr/>
							<a href="/contact" ><span style = {{color:"black", fontSize:'20px'}}>Contact</span></a>
							</div>
							<hr/>
							<a href = "/KobertSum"><span style = {{color:"black", fontSize:'20px'}}>BertSumExt<br/>(제목)</span></a>
							<hr/>
							<a href = "/SummaRuNNer"><span style = {{color:"black", fontSize:'20px'}}>Summa<br/>RuNNer<br/>(제목)</span></a>
						</section>
						<section className="main">
							<header>
							<a href="/home"><img src className="skkuimg" alt = "vaivlogo" src = "img/vaiv_news.png"/></a>
							</header>
							<PegasusField/>
							
						</section>
					</Route>
				</Router>
				
			</div>
		);
	}
}

export default App;
