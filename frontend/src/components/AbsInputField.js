import React, { useState} from 'react';
import TextareaAutosize from '@material-ui/core/TextareaAutosize';

function AbsInputField (){
    const URL_TO_API = "http://112.175.32.78:443";
    const apiURL = ['/api/kobart','/api/kobart_rdrop','/api/kobart_rdrop_magazine', '/api/kobart_rdrop_book', '/api/KobertSumExtAbs','/api/kobart_rdrop_aihubnews']

    const [extabschk, setExtabschk] = useState(false);
    const [bart, setBart] = useState(false); //bart 체크박스 체크가 되었는지
    const [rdrop, setRdrop] = useState(true); // bart r-drop 체크박스 체크가 되었는지
    const [aihubRdropchk, setAihubRdropchk] = useState(true);
    const [aiHub, setAiHub] = useState(false); // aihub 체크박스 체크가 되었는지
    const [sumTxt, setSumTxt] = useState([]); // summary text
    const [oriTxt,setOriTxt] = useState([]); // original text
    const [ctt, setCtt] = useState(''); // textarea의 값이 무엇인지
    const [bartVar, setBartVar] = useState([]);
    const [rdVar, setRdVar] = useState([]);
    
    const style = {
        minHeight: '50px',
        resize: 'none',
        padding: '9px',
        boxSizing: 'border-box',
        fontSize: '15px'
    };

    const leftBox = {
        float : 'left',
        width : '42%',
        marginRight: '100px',
        marginTop: '0px',
    }

    const rightBox= {
        float : 'right',
        width:'42%',
        marginRight: '100px',
        marginTop: '0px',
    }

    function getRequest(jsons){
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

    const reset = ()=>{
        setSumTxt([]);
        setOriTxt([]);
        setBartVar([]);
        setRdVar([]);
        setRdBVar([]);
        setRdMVar([]);
        setExtab([]);
        setAihubRdrop([]);
    }

    const getTextSummary = (_oriTxt) =>{
        // const requestOpt = getRequest({"text":oriTxt})
        const requestOpt = getRequest({"text":_oriTxt})
        let bVar=[];
        let rVar=[];
        let rBVar=[];
        let rMVar=[];
        let extVar=[];
        let aihubRdropVar=[];
        console.log('original txt', requestOpt)
        if(rdrop===true){
            fetch(URL_TO_API+apiURL[1], requestOpt).then(response => response.json()).then(jsons => {
                console.log(jsons['summary'])
				// setRVar(jsons['summary'], jsons['time'])
                rVar.push(jsons['summary'])
                rVar.push(jsons['time'].toFixed(2))
                rVar.push(jsons['score'].toFixed(4))
                
                setRdVar(rVar);
			});
        }
        if (bart===true){
            fetch(URL_TO_API+apiURL[0], requestOpt).then(response => response.json()).then(jsons => {
				// setBartVar(jsons['summary'],jsons['time'])
                bVar.push(jsons['summary'])
                bVar.push(jsons['time'].toFixed(2))
                bVar.push(jsons['score'].toFixed(4))
                setBartVar(bVar);
			});
        }
        if(rdropBook===true){
            fetch(URL_TO_API+apiURL[3], requestOpt).then(response=>response.json()).then(jsons=>{
                rBVar.push(jsons['summary'])
                rBVar.push(jsons['time'].toFixed(2))
                rBVar.push(jsons['score'].toFixed(4))

                setRdBVar(rBVar);
            })
        }
        if(rdropMag===true){
            fetch(URL_TO_API+apiURL[2], requestOpt).then(response=>response.json()).then(jsons=>{
                rMVar.push(jsons['summary'])
                rMVar.push(jsons['time'].toFixed(2))
                rMVar.push(jsons['score'].toFixed(4))

                setRdMVar(rMVar);
            })
        }
        if(extabschk===true){
            fetch(URL_TO_API+apiURL[4], requestOpt).then(response=>response.json()).then(jsons=>{
                extVar.push(jsons['summary'].replace('\n',''))
                extVar.push(jsons['time'].toFixed(2))
                if(typeof jsons['score']==='number'){
                    extVar.push(jsons['score'].toFixed(4))
                }
                else{extVar.push(jsons['score'])}

                setExtab(extVar);
            })
        }
        if(aihubRdropchk===true){
            fetch(URL_TO_API+apiURL[5],requestOpt).then(response=>response.json()).then(jsons=>{
                aihubRdropVar.push(jsons['summary'].replace('\n',''))
                aihubRdropVar.push(jsons['time'].toFixed(2))
                if(typeof jsons['score']==='number'){
                    aihubRdropVar.push(jsons['score'].toFixed(4))
                }
                else{
                    aihubRdropVar.push(jsons['score'])
                }
                setAihubRdrop(aihubRdropVar);
            })
        }
        
        
    }

    const onClickSum=()=>{
        reset();
        let _sumTxt='';
        let _oriTxt=[];
        const regex = /(http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
        if (aiHub === true) {
			const b = Math.floor(Math.random() * 3000);
			const requestOpt = getRequest({random: b, type:"abs"});
			fetch(URL_TO_API + "/api/aiHub", requestOpt).then(response => response.json()).then(jsons => {
				
				setSumTxt(jsons["abstractive"]);
				setOriTxt(jsons['article_original']);
                _oriTxt=jsons['article_original']
                getTextSummary(_oriTxt);
			});
        }
        else if (regex.test(ctt)) {
            if (ctt.startsWith("https://n.news.naver.com/")) {
				const startsurl = ctt.split('?')[0].split("/");
				const oid = startsurl[startsurl.length - 2];
				const aid = startsurl[startsurl.length - 1];
				setCtt(`https://news.naver.com/main/read.naver?oid=${oid}&aid=${aid}`);
			}

            if (ctt.startsWith("https://news.naver.com/")){
                const requestOpt = getRequest({url: ctt});
                fetch(URL_TO_API + "/api/original_text", requestOpt).then(response => response.json()).then(jsons => {
                    
                    setOriTxt(jsons['text']);
                    _oriTxt=jsons['text']
                });
                fetch(URL_TO_API + "/api/naver_summary", requestOpt).then(response => response.json()).then(jsons => {
                    setSumTxt(jsons["sent_list"]);
                    getTextSummary(_oriTxt);
                });
            } else if (ctt.startsWith("https://vip.mk.co.kr/newSt/news/")){
                const requestOpt = getRequest({url: ctt});
                fetch(URL_TO_API + "/api/mkreport", requestOpt).then(response => response.json()).then(jsons => {
                    
                    setOriTxt(jsons['text']);
                    _oriTxt=jsons['text'];
                    getTextSummary(_oriTxt);
                });
                setSumTxt(["No Summary"]);
            }

			

		} else {
			const requestOpt = getRequest({text: ctt});
			fetch(URL_TO_API + "/api/split_sentences", requestOpt).then(response => response.json()).then(jsons => {
                _oriTxt = jsons['sent_list']
                setOriTxt(_oriTxt);
                setSumTxt("No Gold Summary");
                getTextSummary(_oriTxt);
			});
			// setSumTxt("No Gold Summary");
		}

        setSumTxt(_sumTxt)
        console.log(sumTxt)
    }

    const showOriginal=()=>{
        return(
            <div>
                {
                    oriTxt===[]?
                    (
                        <span></span>
                    ):
                    (<div>
                        
                        <h3>Original Text</h3>
                        <span>{(oriTxt)===[]}</span>
                        <p style={{border:"1px solid black"}}>{oriTxt.join(" ")}</p>
                    </div>)
                }
            </div>
        )
    }

    const showGold=()=>{
        return (
            <div>
                {
                    sumTxt===[]?
                    (
                        <span>
                        </span>
                    ):
                    (
                        <div>
                            <h3>{aiHub?"Gold Summary" : "Ext Summary"}</h3>
                            <p style={{border:"1px solid black"}}> {sumTxt}</p>
                        </div>
                    )
                }
            </div>
        )
    }

    const showBart=()=>{
        return (
            <div>
                {
                    bart===false?
                    (
                        <span>
                        </span>
                    ):(
                        <div>
                            <label><h3>BART</h3><span>{bartVar[1]} seconds</span>
                            <br/>
                            <span>score : {bartVar[2]}</span></label>
                            <p style={{border:"1px solid black"}}>{bartVar[0]}</p>
                        </div>
                    )
                }
            </div>
        )
    }

    const showRdrop=()=>{
        console.log((typeof(rdVar[0]) === "string") ? rdVar[0].split("\n") : "undef");
        return (
            <div>
                {
                    rdrop===false?
                    (
                        <span>
                        </span>
                    ):(
                        <div>
                            <label><h3>BART R-Drop(news)</h3><span>{rdVar[1]} seconds</span>
                            <br/>
                            <span>score : {rdVar[2]}</span></label>
                            {/* Temporary mapping */}
                            <p style={{border:"1px solid black"}}>{typeof(rdVar[0]) === "string" ? rdVar[0].split("\n").map(line=>{
                                return <span>{line}<br></br></span>
                            }) : ""} </p>
                        </div>
                    )
                }
            </div>
        )
    }
    const showRdropBook=()=>{
        return(
            <div>
                {
                    rdropBook===false?
                    (<span>

                    </span>
                    ):(
                        <div>
                            <label><h3>BART R-Drop(Book)</h3><span>{rdBVar[1]} seconds</span>
                            <br/>
                            <span>score : {rdBVar[2]}</span></label>
                            <p style={{border:"1px solid black"}}>{typeof(rdBVar[0]) === "string" ? rdBVar[0].split("\n").map(line=>{
                                return <span>{line}<br></br></span>
                            }) : ""} </p>
                        </div>
                    )
                }
            </div>
        )
    }
    const showRdropMag=()=>{
        return (
            <div>
                {
                    rdropMag===false?
                    (<span>

                    </span>
                    ):(
                        <div>
                            <label><h3>BART R-Drop(Magazine)</h3><span>{rdMVar[1]} seconds</span>
                            <br/>
                            <span>score : {rdMVar[2]}</span></label>
                            {/* Temporary mapping */}
                            <p style={{border:"1px solid black"}}>{typeof(rdMVar[0]) === "string" ? rdMVar[0].split("\n").map(line=>{
                                return <span>{line}<br></br></span>
                            }) : ""} </p>
                        </div>
                    )
                }
            </div>
        )
    }
    const showExtAbs = ()=>{
        return (
            <div>
                {
                    extabschk===false?
                    (<span>

                    </span>
                    ):(
                        <div>
                            <label><h3>BERTSumExtAbs</h3><span>{extabs[1]} seconds</span>
                            <br/>
                            <span>score : {extabs[2]}</span></label>
                            <p style={{border:"1px solid black"}}>{typeof(extabs[0]) === "string" ? extabs[0].split("\n").map(line=>{
                                return <span>{line}<br></br></span>
                            }) : ""} </p>
                        </div>
                    )
                }
            </div>
        )
    }

    const showAiRdrop=()=>{
        return (
            <div>
                {
                    aihubRdrop===false?
                    (<span>

                    </span>):(
                        <div>
                            <label><h3>BART R-Drop (AIHub News)</h3><span>{aihubRdrop[1]}</span>
                            <br/>
                            <span>score : {aihubRdrop[2]}</span></label>
                            <p style={{border:"1px solid black"}}>{typeof(aihubRdrop[0])==="string" ? aihubRdrop[0].split('\n').map(line=>{
                                return <span>{line}<br/></span>}):""}</p>
                        </div>
                    )
                }
            </div>

        )
    }

    
    const [rdropBook, setRdropBook] = useState(true);
    const [rdropMag, setRdropMag] = useState(true);
    const [rdMVar, setRdMVar] = useState([]);
    const [rdBVar, setRdBVar] = useState([]);
    const [extabs, setExtab] = useState([]);
    const [aihubRdrop, setAihubRdrop] = useState([]);

    return (
        <>
        <div>
            <span>Language Model</span>
            <h3>Select Model</h3>
            <label> | <input type="checkbox" checked={extabschk} onChange={()=>setExtabschk(!extabschk)}></input> BERTSumExtAbs </label>
            &nbsp;&nbsp;
            <label> | <input type="checkbox" checked = {bart} onChange = {()=>setBart(!bart)}/> BART </label>
            &nbsp;&nbsp;
            <label> | <input type = "checkbox" checked={rdrop} onChange = {()=>setRdrop(!rdrop)}/> BART R-Drop(News) </label>
            &nbsp;&nbsp;
            <label> | <input type = "checkbox" checked={aihubRdropchk} onChange={()=>setAihubRdropchk(!aihubRdropchk)}/> BART R-Drop(AIHub news)</label>
            &nbsp;&nbsp;
            <label> | <input type = "checkbox" checked={rdropBook} onChange={()=>setRdropBook(!rdropBook)}/> BART R-Drop(book)</label>
            &nbsp;&nbsp;
            <label> | <input type = "checkbox" checked={rdropMag} onChange={()=>setRdropMag(!rdropMag)}/> BART R-Drop(magazine)</label>

            <br/><br/><br/><br/>
            <h5>- Input</h5>
            <TextareaAutosize  placeholder="Enter the naver news link or content of the news" style={style} cols="80" onKeyUp = {(e)=>{setCtt(e.target.value)}}/>
            &nbsp;&nbsp;&nbsp;
            <button type="submit" className="btn btn-primary" onClick = {onClickSum}>Summarize</button>
            <br /><br />
            <label><h5><input type="checkbox" name="ai" checked={aiHub} onChange={()=>{setAiHub(!aiHub)}}></input>AIHUB 뉴스 기사 입력(랜덤)</h5></label>
        </div>
        <div style = {leftBox}>
            {showOriginal()}
            {showGold()}
        </div>
        <div style = {rightBox}>
            
            {showExtAbs()}
            {showBart()}
            {showRdrop()}
            {showAiRdrop()}
            {showRdropBook()}
            {showRdropMag()}
        </div>
        </>
    );
}

export default AbsInputField