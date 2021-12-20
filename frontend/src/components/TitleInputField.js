import React, { useState} from 'react';
import TextareaAutosize from '@material-ui/core/TextareaAutosize';

function TitleInputField(){

    const options = [
        {value:3, label : '3sen'},
        {value:4, label : '4sen'},
        {value:5, label : '5sen'}
    ]

    const URL_TO_API = "http://112.175.32.78:443"
    const apiURL = ['/api/KoBertSum_with_title', '/api/KoBertSum']

    const [kobert, setKobert] = useState(true)
    const [ctt,setCtt] = useState('') //content : url
    const [sumTxt, setSumTxt] = useState([]); // summary text
    const [oriTxt,setOriTxt] = useState([]); // original text
    const [aiHub, setAiHub] = useState(false);

    const [kobertSum,setKobertSum] = useState([]);
    const [kobertSumnt, setKobertSumnt] = useState([]);
    const [kbtTime, setKbtTime] = useState(0);
    const [kbtTim, setKbtTim] = useState(0);
    const [kbtnumber, setKbtNumber] = useState(3);
    const [kbtProb, setKbtProb] = useState([]);
    const [kbtProbnt, setKbtProbnt] = useState([]);
    const [isP, setIsP] = useState(true); //확률순 : true, 문장순 : false
    const [isPnt, setIsPnt] = useState(true);
    const [kbtHigh, setKbtHigh] = useState(false);
    const [kbtHighnt, setKbtHighnt] = useState(false);
    const [sumHigh, setSumHigh] = useState(false);

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

    const sumStyle = {
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

    const sumStyleb = {
        backgroundColor: 'skyblue',
        color: "blue",
        fontWeight: "bold"
        
    }
    const goldStyleb={
        backgroundColor:"#FFE146",
        color : "#282828",
        fontWeight: "bold"
    }

    const overlapStyleb={
        backgroundColor: "#64CD3C",
        color : "black",
        fontWeight: "bold"
    } 

    const bold1 = {
        fontWeight : "bold"
    }

    const handleChange= kbtnumber =>{
        setKbtNumber(kbtnumber)
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

    const onChangeRadio=()=>{
        setIsP(!isP);
        let mapped = kobertSum.map((ele,i)=>{
            return {
                index:kbtProb[i],
                value :ele
            }
        })
        if(isP){
            mapped.sort((a,b)=>a.value-b.value);
            console.log(mapped);
            let list1 = [];
            let list2=[];
            for(let i=0;i<mapped.length;i++){
                list1.push(mapped[i].index);
                list2.push(mapped[i].value);
            }
            setKbtProb(list1);
            setKobertSum(list2);
        }
        else{
            mapped.sort((a,b)=>b.index-a.index);
            console.log(mapped);
            let list1=[];
            let list2=[];
            for( let i=0;i<mapped.length;i++){
                list1.push(mapped[i].index);
                list2.push(mapped[i].value);
            }
            setKbtProb(list1);
            setKobertSum(list2);
        }
    }

    const onChangeRadio1=()=>{
        setIsPnt(!isPnt);
        let mapped = kobertSumnt.map((ele,i)=>{
            return {
                index:kbtProbnt[i],
                value :ele
            }
        })
        if(isPnt){
            mapped.sort((a,b)=>a.value-b.value);
            console.log(mapped);
            let list1 = [];
            let list2=[];
            for(let i=0;i<mapped.length;i++){
                list1.push(mapped[i].index);
                list2.push(mapped[i].value);
            }
            setKbtProbnt(list1);
            setKobertSumnt(list2);
        }
        else{
            mapped.sort((a,b)=>b.index-a.index);
            console.log(mapped);
            let list1=[];
            let list2=[];
            for( let i=0;i<mapped.length;i++){
                list1.push(mapped[i].index);
                list2.push(mapped[i].value);
            }
            setKbtProbnt(list1);
            setKobertSumnt(list2);
        }
    }

    const reset = ()=>{
        setSumTxt([])
        setOriTxt([])
    }

    const getTextSummary=(_oriTxt)=>{
        const requestOpt = getRequest({"text":_oriTxt, "topk": kbtnumber*1, "sort": "prob"})
        let ori=[];
        for (let j=1;j<_oriTxt.length;j++){
            ori.push(_oriTxt[j]);
        }
        const requestOpt1 = getRequest({"text": ori, "topk":kbtnumber*1, "sort":"prob"})
        if(kobert===true){
            fetch(URL_TO_API+apiURL[0], requestOpt).then(response => response.json()).then(jsons => {
                let probli = jsons['prob']
                for(let i=0;i<probli?.length;i++){
                    probli[i]=probli[i].toFixed(2)
                }
                console.log(probli)

                setKbtProb(probli)
                let summary = jsons['summary'];
                summary = summary.map(ele=>ele+1)
                setKobertSum(summary);
                let time = jsons['time'].toFixed(2)
                setKbtTime(time)

			});
            fetch(URL_TO_API+apiURL[1], requestOpt1).then(response=>response.json()).then(jsons=>{
                let probli = jsons['prob']
                for(let i=0;i<probli?.length;i++){
                    probli[i]=probli[i].toFixed(2)
                }
                console.log(probli)
                let summary = jsons['summary'];
                summary = summary.map(ele=>ele+1);
                setKbtProbnt(probli)
                setKobertSumnt(summary);
                let time = jsons['time'].toFixed(2);
                setKbtTim(time)
                
            })
        }
    }

    const highOri = ()=>{
        let _list=[]
        
        if(kbtHighnt){
            if(sumHigh&&kbtHigh){
                for(let i = 1;i<oriTxt.length;i++){
                    if(typeof(sumTxt)!='str'&&sumTxt.includes(oriTxt[i])&&kobertSum.includes(i)&&kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style = {overlapStyleb}>{oriTxt[i]}</span>)
                    }
                    else if(typeof(sumTxt)!='str'&&sumTxt.includes(oriTxt[i])&&kobertSum.includes(i)){
                        _list.push(<span key = {i} style = {overlapStyle}>{oriTxt[i]}</span>)
                    }
                    else if (typeof(sumTxt=='str')&&sumTxt.includes(oriTxt[i])&&kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style = {goldStyleb}>{oriTxt[i]}</span>)
                    }
                    else if (typeof(sumTxt=='str')&&sumTxt.includes(oriTxt[i])){
                        _list.push(<span key = {i} style = {goldStyle}>{oriTxt[i]}</span>)
                    }
                    
                    else if(kobertSum.includes(i)&&kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style = {sumStyleb}>{oriTxt[i]}</span>)
                    }
                    else if(kobertSum.includes(i)){
                        _list.push(<span key = {i} style = {sumStyle}>{oriTxt[i]}</span>)
                    }
                    else if(kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style={bold1}>{oriTxt[i]}</span>)
                    }
                    else{
                        _list.push(<span key = {i}>{oriTxt[i]}</span>)
                    }
                }
            }
            else if (sumHigh){
                console.log('hello sumHigh');
                for(let i=1;i<oriTxt.length;i++){
                    if(typeof(sumTxt)!='str'&&sumTxt.includes(oriTxt[i])&&kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style = {goldStyleb}>{oriTxt[i]}</span>)
                    }
                    else if(typeof(sumTxt)!='str'&&sumTxt.includes(oriTxt[i])){
                        _list.push(<span key = {i} style ={goldStyle}>{oriTxt[i]}</span>)
                    }
                    else if(kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style={bold1}>{oriTxt[i]}</span>)
                    }
                    else{
                        _list.push(<span key = {i}>{oriTxt[i]}</span>)
                    }
                }
            }
            else if(kbtHigh){
                for(let i =1;i<oriTxt.length;i++){
                    if(kobertSum.includes(i)&&kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style={sumStyleb}>{oriTxt[i]}</span>)
                    }
                    else if(kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style={bold1}>{oriTxt[i]}</span>)
                    }
                    else if(kobertSum.includes(i)){
                        _list.push(<span key = {i} style = {sumStyle}>{oriTxt[i]}</span>)
                    }
                    else{
                        _list.push(<span key = {i}>{oriTxt[i]}</span>)
                    }
                }
            }
            else{
                for (let i =1 ;i<oriTxt.length;i++){
                    if(kobertSumnt.includes(i)){
                        _list.push(<span key = {i} style = {bold1}>{oriTxt[i]}</span>)
                    }
                    else{
                        _list.push(<span key = {i}>{oriTxt[i]}</span>)
                    }
                }
            }
            return _list
        }
        else{
            if(sumHigh&&kbtHigh){
                for(let i = 1;i<oriTxt.length;i++){
                    if(typeof(sumTxt)!='str'&&sumTxt.includes(oriTxt[i])&&kobertSum.includes(i)){
                        _list.push(<span key = {i} style = {overlapStyle}>{oriTxt[i]}</span>)
                    }
                    else if (typeof(sumTxt=='str')&&sumTxt.includes(oriTxt[i])){
                        _list.push(<span key = {i} style = {goldStyle}>{oriTxt[i]}</span>)
                    }
                    else if(kobertSum.includes(i)){
                        _list.push(<span key = {i} style = {sumStyle}>{oriTxt[i]}</span>)
                    }
                    else{
                        _list.push(<span key = {i}>{oriTxt[i]}</span>)
                    }
                }
            }
            else if (sumHigh){
                console.log('hello sumHigh');
                for(let i=1;i<oriTxt.length;i++){
                    if(typeof(sumTxt)!='str'&&sumTxt.includes(oriTxt[i])){
                        _list.push(<span key = {i} style = {goldStyle}>{oriTxt[i]}</span>)
                    }
                    else{
                        _list.push(<span key = {i}>{oriTxt[i]}</span>)
                    }
                }
            }
            else if(kbtHigh){
                for(let i =1;i<oriTxt.length;i++){
                    if(kobertSum.includes(i)){
                        _list.push(<span key = {i} style={sumStyle}>{oriTxt[i]}</span>)
                    }
                    else{
                        _list.push(<span key = {i}>{oriTxt[i]}</span>)
                    }
                }
            }
            else{
                for (let i =1 ;i<oriTxt.length;i++){
                    _list.push(<span key = {i}>{oriTxt[i]}</span>)
                }
            }
            return _list
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
                            {highOri()}
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
                            <h3>{aiHub?"Gold Summary" : "Ext Summary"}</h3>
                            <label><h5><input type="checkbox" checked={sumHigh} onChange={()=>{setSumHigh(!sumHigh)}}></input>Summary Highlight</h5></label>
                            <p style={{border:"1px solid black"}}> {sumTxt}</p>
                        </div>
                    )
                }
            </div>
        )
    }

    const showKbtnt = ()=>{
        return(
            <div>
                {
                    kobert===false?
                    (
                        <span>

                        </span>
                    ):
                    (
                        <div>
                            <label><h3>Kobertsum(no title)</h3><span>{kbtTim} seconds</span></label>
                            <label> |
                            <input
                                type="radio"
                                checked={isPnt===true}
                                onChange={onChangeRadio1}
                            ></input>
                            확률 순 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            </label>
                            <label> |
                                <input 
                                    type = "radio"
                                    checked={isPnt===false}
                                    onChange={onChangeRadio1}
                                ></input>
                                문장 순 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            </label>
                            <div style={{border:"1px solid black"}}>
                                {
                                kobertSumnt.map((ele, idx)=>(
                                    <p key = {idx}>{oriTxt[ele+1]} {kbtProbnt[idx]}</p>
                                ))}
                            </div>
                        </div>
                    )
                }
            </div>
        )
    }

    const showKbt=()=>{
        return (
            <div>
                {
                    kobert===false?
                    (
                        <span>
                        </span>
                    ):(
                        <div>
                            <label><h3>Kobertsum(title)</h3><span>{kbtTime} seconds</span></label>
                            <label> |
                            <input
                                type="radio"
                                checked={isP===true}
                                onChange={onChangeRadio}
                            ></input>
                            확률 순 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            </label>
                            <label> |
                                <input 
                                    type = "radio"
                                    checked={isP===false}
                                    onChange={onChangeRadio}
                                ></input>
                                문장 순 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            </label>
                            <div style={{border:"1px solid black"}}>
                                {
                                kobertSum.map((ele, idx)=>(
                                    <p key = {idx}>{oriTxt[ele]} {kbtProb[idx]}</p>
                                ))}
                            </div>
                        </div>
                    )
                }
            </div>
        )
    }
    const onClickSum=()=>{
        console.log(kbtnumber)
        //reset()
        let _oriTxt=[];
        let _sumTxt=[];

        const regex = /(http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
        if (aiHub === true) {
			const b = Math.floor(Math.random() * 3000);
			const requestOpt = getRequest({random: b, type:"ext"});
			fetch(URL_TO_API + "/api/aiHub_title", requestOpt).then(response => response.json()).then(jsons => {
				let list = [];
				jsons['extractive'].forEach(item => {
					list.push(jsons['article_original'][item]);
				});
				
				setSumTxt(list);
                _sumTxt=list;
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
			const requestOpt = getRequest({url: ctt});
			fetch(URL_TO_API + "/api/original_text_with_title", requestOpt).then(response => response.json()).then(jsons => {
                setOriTxt(jsons['text']);
                _oriTxt=jsons['text']
			});
            fetch(URL_TO_API + "/api/naver_summary", requestOpt).then(response => response.json()).then(jsons => {
                setSumTxt(jsons["sent_list"]);
                getTextSummary(_oriTxt);
            });
			

		} else {
			const requestOpt = getRequest({text: ctt});
			fetch(URL_TO_API + "/api/split_sentences", requestOpt).then(response => response.json()).then(jsons => {
                _oriTxt = jsons['sent_list']
                setOriTxt(_oriTxt)
                setSumTxt("No Gold Summary");
                getTextSummary(_oriTxt);
			});
			// setSumTxt("No Gold Summary");
		}

        setSumTxt(_sumTxt)
        console.log(sumTxt)
    }

    return(
        <>
            <div>
                <span>Language Model(fine-tuning with title)</span>
                <h3>Select Model</h3>
                <label> | <input type="checkbox" checked = {kobert} onChange = {()=>setKobert(!kobert)}/> KoBertSum </label>
                <br/>
                <select name="number1" id="number1" onChange={(e)=>setKbtNumber(e.target.value)}>
                    <option value={3} onChange={()=>{console.log("3 selected");}}>요약문 개수 : 3</option>
                    <option value={4} onChange={()=>{console.log("4 selected");}}>요약문 개수 : 4</option>
                    <option value={5} onChange={()=>{console.log("5 selected");}}>요약문 개수 : 5</option>
                </select>
                <br></br><br></br><br/>
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
            <label><h5><input type="checkbox" checked={kbtHigh} onChange={()=>{setKbtHigh(!kbtHigh)}}></input>Kobertsum(title) Highlight</h5></label>
            <label><h5><input type = "checkbox" checked = {kbtHighnt} onChange={()=>{setKbtHighnt(!kbtHighnt)}}></input>Kobertsum(no title) Highlight</h5></label>
                {showKbt()}
                {showKbtnt()}
            </div>
        </>
    )
}

export default TitleInputField;