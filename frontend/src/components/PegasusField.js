import React, { useState} from 'react';
import TextareaAutosize from '@material-ui/core/TextareaAutosize';

function PegasusField(){

    const URL_TO_API = "http://112.175.32.78:443"
    const apiURL = ['/api/pegasus_large', '/api/pegasus_large_skku', '/api/pegasus_base_skku']

    const [large, setLarge] = useState(false);
    const [largeSKKU, setLargeSKKU] = useState(false);
    const [baseSKKU, setBaseSKKU] = useState(false);
    const [largeVar, setLargeVar] = useState([]);
    const [largeSKKUVar, setLargeSKKUVar] = useState([]);
    const [baseSKKUVar, setBaseSKKUVar] = useState([]);
    const [sumTxt, setSumTxt] = useState([]); // summary text
    const [oriTxt,setOriTxt] = useState([]); // original text
    const [ctt,setCtt] = useState('')
    const [test, setTest] = useState(false);
    let index = -1;

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
        setLargeVar([]);
        setLargeSKKUVar([]);
        setBaseSKKUVar([]);
    }

    const getTextSummary=(_oriTxt)=>{
        const requestOpt = getRequest({"text":_oriTxt, "index": index})
        let lVar=[];
        let lsVar=[];
        let bVar=[];
        if (large===true){
            fetch(URL_TO_API+apiURL[0], requestOpt).then(response => response.json()).then(jsons => {
                lVar.push(jsons['summary'])
                lVar.push(jsons['time'].toFixed(2))
                lVar.push(jsons['rouge1']);
                lVar.push(jsons['rouge2']);
                lVar.push(jsons['rougeL']);
                setOriTxt(jsons['origin']);
                setLargeVar(lVar);
			});
        }
        if (largeSKKU===true){
            fetch(URL_TO_API+apiURL[1], requestOpt).then(response => response.json()).then(jsons => {
                lsVar.push(jsons['summary'])
                lsVar.push(jsons['time'].toFixed(2))
                lsVar.push(jsons['rouge1']);
                lsVar.push(jsons['rouge2']);
                lsVar.push(jsons['rougeL']);
                setOriTxt(jsons['origin']);
                setLargeSKKUVar(lsVar);
			});
        }
        if(baseSKKU===true){
            fetch(URL_TO_API+apiURL[2], requestOpt).then(response => response.json()).then(jsons => {
                bVar.push(jsons['summary'])
                bVar.push(jsons['time'].toFixed(2))
                bVar.push(jsons['rouge1']);
                bVar.push(jsons['rouge2']);
                bVar.push(jsons['rougeL']);
                setOriTxt(jsons['origin']);
                setBaseSKKUVar(bVar);
			});
        }
    }


    const showOriginal=()=>{
        return(
            <div>
                {
                    oriTxt===[]?
                    (
                        <span></span>
                    ):
                    (
                    <div>
                        
                        <h3>Original Text</h3>
                        <span>{(oriTxt)===[]}</span>
                        <p style = {{border:"1px solid black"}}>
                            <span>{oriTxt}</span>
                            <br/>
                        </p>
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
                            <h3>{test? "Gold Summary" : ""}</h3>
                            <p style={{border:"1px solid black"}}> {sumTxt}</p>
                        </div>
                    )
                }
            </div>
        )
    }
    
    const showlarge=()=> {

        return (
            <div>
                {
                    large===false?
                    (
                        <span>
                        </span>
                    ):(
                        <div>
                            <label><h3>Pegasus_LARGE(Author)</h3><span>{largeVar[1]} seconds</span>
                            <br/>{test===true ? (
                                <span>ROUGE-1 : {largeVar[2]}
                                    <br/>ROUGE-2 : {largeVar[3]}
                                    <br/>ROUGE-L : {largeVar[4]}</span>
                                ) : (<span></span>)}</label>
                            <p style={{border:"1px solid black"}}>{largeVar[0]}</p>
                        </div>
                    )
                }
            </div>
        )
    }

    const showlargeSKKU=()=> {

        return (
            <div>
                {
                    largeSKKU===false?
                    (
                        <span>
                        </span>
                    ):(
                        <div>
                            <label><h3>Pegasus_LARGE(SKKU)</h3><span>{largeSKKUVar[1]} seconds</span>
                            <br/>{test===true ? (
                                    <span>ROUGE-1 : {largeSKKUVar[2]}
                                        <br/>ROUGE-2 : {largeSKKUVar[3]}
                                        <br/>ROUGE-L : {largeSKKUVar[4]}</span>
                                    ) : (<span></span>)}</label>
                            <p style={{border:"1px solid black"}}>{largeSKKUVar[0]}</p>
                        </div>
                    )
                }
            </div>
        )
    }

    const showbaseSKKU = ()=> {
        return(
            <div>
                {
                    baseSKKU===false?
                    (
                        <span>

                        </span>
                    ):
                    (
                        <div>
                            <label><h3>Pegasus_BASE(SKKU)</h3><span>{baseSKKUVar[1]} seconds</span>
                            <br/>{test===true ? (
                                    <span>ROUGE-1 : {baseSKKUVar[2]}
                                        <br/>ROUGE-2 : {baseSKKUVar[3]}
                                        <br/>ROUGE-L : {baseSKKUVar[4]}</span>
                            ) : (<span></span>)}</label>
                            <p style={{border:"1px solid black"}}>{baseSKKUVar[0]}</p>
                        </div>
                    )
                }
            </div>
        )
    }

    const onClickSum=()=>{
        reset();
        let _sumTxt=[];
        let _oriTxt=[];
        const regex = /(http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
        if (test === true) {
			const b = Math.floor(Math.random() * 1000);
			const requestOpt = getRequest({random: b});
			fetch(URL_TO_API + "/api/cnnTest", requestOpt).then(response => response.json()).then(jsons => {
				setSumTxt(jsons["answer"]);
				setOriTxt(jsons['article_original']);
                _oriTxt=jsons['article_original']
                index = jsons['index']
                getTextSummary(_oriTxt);
			});

        }
        else {
			const requestOpt = getRequest({text: ctt});
			fetch(URL_TO_API + "/api/split_sentences", requestOpt).then(response => response.json()).then(jsons => {
                _oriTxt = jsons['sent_list']
                setOriTxt(_oriTxt);
                setSumTxt("No Gold Summary");
                index = -1;
                getTextSummary(_oriTxt);
			});
		}
        setSumTxt(_sumTxt)
    }

    return(
        <>
            <div>
                <span>Language Model</span>
                <h3>Select Model</h3>
                <label> | <input type="checkbox" checked = {large} onChange = {()=>setLarge(!large)}/> Pegasus_LARGE (Author)</label>
                <label> | <input type="checkbox" checked = {largeSKKU} onChange = {()=>setLargeSKKU(!largeSKKU)}/> Pegasus_LARGE (SKKU) </label>
                <label> | <input type="checkbox" checked = {baseSKKU} onChange = {()=>setBaseSKKU(!baseSKKU)}/> Pegasus_BASE (SKKU)</label>
                <br/>
                <br></br><br></br><br/>
                <h5>- Input</h5>
                <TextareaAutosize  placeholder="Enter the cnn news link or content of the news" style={style} cols="80" onKeyUp = {(e)=>{setCtt(e.target.value);console.log(ctt)}}/>
                &nbsp;&nbsp;&nbsp;
                <button type="submit" className="btn btn-primary" onClick = {onClickSum}>Summarize</button>
                <br /><br />
                <label><h5><input type="checkbox" name="test" checked={test} onChange={()=>{setTest(!test)}}></input>CNN_Dailymail Test Data</h5></label>
            </div>
            <div style = {leftBox}>
                {showOriginal()}
                {showGold()}
            </div>
            <div style = {rightBox}>
                {showlarge()}
                {showlargeSKKU()}
                {showbaseSKKU()}
            </div>
        </>
    )
}

export default PegasusField;