import React, { useState} from 'react';
import TextareaAutosize from '@material-ui/core/TextareaAutosize';

function PegasusField(){

    const URL_TO_API = "http://112.175.32.78:443"
    const apiURL = ['/api/pegasus_cnn', '/api/pegasus_xsum']

    const [cnn, setCnn] = useState(false);
    const [xsum, setXsum] = useState(false);
    const [cnnVar, setCnnVar] = useState([]);
    const [xsumVar, setXsumVar] = useState([]);
    const [sumTxt, setSumTxt] = useState([]); // summary text
    const [oriTxt,setOriTxt] = useState([]); // original text
    const [ctt,setCtt] = useState('')

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
        setCnnVar([]);
        setXsumVar([]);
    }

    const getTextSummary=(_oriTxt)=>{
        const requestOpt = getRequest({"text":_oriTxt})
        let cVar=[];
        let xVar=[];
        if (cnn===true){
            fetch(URL_TO_API+apiURL[0], requestOpt).then(response => response.json()).then(jsons => {
                cVar.push(jsons['summary'])
                cVar.push(jsons['time'].toFixed(2))
                cVar.push(jsons['score'].toFixed(4))
                setCnnVar(cVar);
			});
        }
        if(xsum===true){
            fetch(URL_TO_API+apiURL[1], requestOpt).then(response => response.json()).then(jsons => {
                xVar.push(jsons['summary'])
                xVar.push(jsons['time'].toFixed(2))
                xVar.push(jsons['score'].toFixed(4))
                
                setXsumVar(xVar);
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
                            <span style = {{fontWeight: 'bold', fontSize : '20px'}}>{oriTxt[0]}</span>
                            <br/>
                        </p>
                    </div>)
                }
            </div>
        )
    }

    

    const showXsum = ()=> {
        return(
            <div>
                {
                    xsum===false?
                    (
                        <span>

                        </span>
                    ):
                    (
                        <div>
                            <label><h3>Pegasus(XSUM)</h3><span>{xsumVar[1]} seconds</span>
                            <br/>
                            <span>score : {xsumVar[2]}</span></label>
                            <p style={{border:"1px solid black"}}>{xsumVar[0]}</p>
                        </div>
                    )
                }
            </div>
        )
    }

    const showCnn=()=> {

        return (
            <div>
                {
                    cnn===false?
                    (
                        <span>
                        </span>
                    ):(
                        <div>
                            <label><h3>Pegasus(cnn_dailymail)</h3><span>{cnnVar[1]} seconds</span>
                            <br/>
                            <span>score : {cnnVar[2]}</span></label>
                            <p style={{border:"1px solid black"}}>{cnnVar[0]}</p>
                        </div>
                    )
                }
            </div>
        )
    }
    const onClickSum=()=>{
        reset();
        let _sumTxt=[];
        getTextSummary(ctt);
        setSumTxt(_sumTxt)
        console.log(sumTxt)
    }

    return(
        <>
            <div>
                <span>Language Model</span>
                <h3>Select Model</h3>
                <label> | <input type="checkbox" checked = {cnn} onChange = {()=>setCnn(!cnn)}/> Pegasus(cnn_dailymail) </label>

                <label> | <input type="checkbox" checked = {xsum} onChange = {()=>setXsum(!xsum)}/> Pegasus(XSUM) </label>
                <br/>
                <br></br><br></br><br/>
                <h5>- Input</h5>
                <TextareaAutosize  placeholder="Enter the naver news link or content of the news" style={style} cols="80" onKeyUp = {(e)=>{setCtt(e.target.value);console.log(ctt)}}/>
                &nbsp;&nbsp;&nbsp;
                <button type="submit" className="btn btn-primary" onClick = {onClickSum}>Summarize</button>
                <br /><br />
            </div>
            <div style = {leftBox}>
                {showOriginal()}
            </div>
            <div style = {rightBox}>
                {showCnn()}
                {showXsum()}
            </div>
        </>
    )
}

export default PegasusField;