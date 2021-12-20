import React, {useState, useEffect} from "react";
import { Nav, NavItem} from 'reactstrap';
import { NavLink, useLocation, useHistory } from "react-router-dom";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import Toolbar from '@material-ui/core/Toolbar';
import { Dropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import MenuBookIcon from '@material-ui/icons/MenuBook';
import text11 from "../../assets/text/text1.json";
import text2 from "../../assets/text/text2.json"
import text3 from "../../assets/text/text3.json"
import text4 from "../../assets/text/text4.json"
import text5 from "../../assets/text/text5.json"
import text6 from "../../assets/text/report6.json"
import text7 from "../../assets/text/report7.json"
import text8 from "../../assets/text/report8.json"
import {Button} from 'reactstrap'
import { AiFillCaretUp,AiFillCaretDown} from "react-icons/ai";
import {FormOutlined} from "@ant-design/icons"

import Sidebar from "./Sidebar"
import "./App.css"
import {
    Container,
    Col,
} from "reactstrap";

import {faEdit, faHome, faBookOpen} from '@fortawesome/free-solid-svg-icons';
import { SettingsInputAntennaTwoTone } from "@material-ui/icons";




const BottomNav = ({tabs}) => {
  
    return (
        <div style={{position:"relative"}}>
          
          {/* Bottom Tab Navigator*/}
          <nav className="navbar fixed-bottom navbar-light bottom-tab-nav" role="navigation">
            <Nav className="w-100">
              <div className=" d-flex flex-row justify-content-around w-100">
                {
                  tabs.map((tab, index) =>(
                    <NavItem key={`tab-${index}`}>
                      <NavLink to={tab.route} className="nav-link" activeClassName="active">
                        <div className="row d-flex flex-column justify-content-center align-items-center">
                        <FontAwesomeIcon size="lg" icon={tab.icon}/>
                          <div>{tab.label}</div>
                        </div>
                      </NavLink>
                    </NavItem>
                  ))
                }
              </div>
            </Nav>
          </nav>
        </div>
    )
};



function SummaryPage({location, history}){
    // console.log(location.state.items)
    
    const [sentence, setSentence] = useState('');
    const [subtitle, setSubtitle] = useState('');
    const [summary, setSummary] = useState([])
    const [buttonIdx, setButtonIdx] = useState([]);
    const [text1, setText1] = useState(text2);
    
    const items=location.state.items 
    const textState = location.state.textState

    useEffect(()=>{
      console.log(location.state)
      let summaryVar = []
      let buttonIdxVar=[]
      let text
      if(location.state.book === "text1"){
        text=text11
        setText1(text11)
      }
      if(location.state.book === "text2"){
        text=text2
        setText1(text2)
      }
      if(location.state.book==="text3"){
        text=text3
        setText1(text3)
      }
      if(location.state.book==="text4"){
        text=text4
        setText1(text4)
      }
      if(location.state.book==="text5"){
        text = text5
        setText1(text5)
      }
      if(location.state.book==='text6'){
        text = text6
        setText1(text6)
      }
      if(location.state.book==='text7'){
        text= text7
        setText1(text7)
      }
      if(location.state.book==="text8"){
        text = text8
        setText1(text8)
      }
      console.log(text1['contents'].length)
      for(let i =0;i<text["contents"].length;i++){
        summaryVar.push(text["contents"][i]["summary"]);
        buttonIdxVar.push(true);
      }
      console.log(summaryVar.length)
      setButtonIdx(buttonIdxVar)
      setSummary(summaryVar)
    },[])

    const fetchData=(index)=>{
      let but = [...buttonIdx];
      but[index] = !but[index]
      setButtonIdx(but)
      console.log(buttonIdx);
      console.log(index, summary[index], summary[index] === '');
      // if(summary[index]==='' || summary[index] === undefined){
      //   let newSummaryVar=[...summary]
      //   newSummaryVar[index] = "loading..."
      //   setSummary(newSummaryVar) 
      //   const requestOptions = {
      //     method: 'POST',
      //     headers: {
      //       'Content-Type': 'application/json',
      //       'Access-Control-Allow-Origin': '*',
      //       'Access-Control-Allow-Headers': '*',
      //     },
      //     body: JSON.stringify({text: text1["contents"][index]["content"]})
      //   };
    
      //   fetch("http://112.175.32.78:443/api/kobart_rdrop_book", requestOptions)
      //   .then(response => response.json())
      //   .then(json => {
      //     var target = json["summary"];
      //     console.log(target);
      //     setSentence(target)
      //     setSubtitle(text1["contents"][index]["contents_name"])
      //     let newArray = [...summary];
      //     newArray[index]= target;
      //     setSummary(newArray);
        
      //     console.log(summary);
      //   })
      //   .catch(error => {
      //   });
      // }
    }

    let [book, setBook] = useState('');

    useEffect(()=>{
        if(location.state === undefined){
            history.push('/')
        }
        else{
          // setLoc(location.state.book)
          setBook(location.state.book)
        }
    })

    const tabs = [{
      route: "/home",
      icon: faHome,
      label: "Home"
    }]

    const showPassage=()=>{
      let _list = [];
      for (let i = 0;i<text1["contents"].length;i++){
        _list.push(
          <DropdownItem onClick={(e)=>{console.log(items); history.push({
            pathname:`/write/${location.state.book}`,
            state : {book:location.state.book, items:items, textState:textState, curState:textState[i]}
          })}}>
            {text1["contents"][i]["contents_name"]}
          </DropdownItem>
        )
      }

      return _list;
    }

    const [isOpen, setIsOpen] = useState(false)
    const toggle =()=>{
      setIsOpen(!isOpen)
    }
    
    const text=['text1', 'text2','text3', 'text4', 'text5', 'text6', 'text7', 'text8']
    return(
        <>
        <nav className="navbar navbar-expand-md navbar-light sticky-top" 	role="navigation">
        
        <div className="container-fluid"> 
          <Nav className="ml-auto" style={{marginRight:"100px"}}>
              
              <NavItem>
              <Toolbar>
                 
                <div style={{fontSize:"32px", fontFamily:"Yfont"}}>
                  각 문단 별 요약
                </div>
              </Toolbar>
              </NavItem>
            </Nav>
            <Nav className="ml-auto" style={{marginRight:"100px"}}>
              
              <NavItem>
              <Toolbar>
                 
                <Dropdown direction="left" isOpen={isOpen} toggle={toggle} size = "sm">
                  <DropdownToggle caret>
                  <MenuBookIcon/> 본문보기
                  </DropdownToggle>
                  <DropdownMenu>
                    {showPassage()}
                  </DropdownMenu>
                </Dropdown>
              </Toolbar>
              </NavItem>
            </Nav>
           
        </div>
      </nav>
      
      {/* <span>
        <Sidebar isOpen={true} />
      </span> */}
      <div  style={{marginLeft:"250px", marginTop:"50px"}}>
      <div style={{display:"flex",border:"none", fontSize:"40px",  fontFamily:"BlackhanSans"}} color="dark" outline="true" size="sm">
        {text1["title"]}
      </div>
      </div>
      <br/><br/>
      <span style={{marginLeft:"350px", fontSize:"32px", fontFamily:"BlackhanSans", marginBottom:"30px"}}>
        목차
      </span>
      &nbsp;&nbsp;&nbsp;&nbsp;
      <span style={{backgroundColor:"red", marginLeft:"13px", fontSize:"22px", fontFamily:"Yfont", marginBottom:"30px", color:"white"}}>각 문단의 summary 생성 결과</span>
        
      <br/>
      <div style={{ marginLeft:"350px", }}>{
        // const map1 = array1.map(x => x * 2);
        
        text1["contents"].map((x, index) => 
        <div key={index} style={{marginBottom: "10px", marginRight:"10%", }}>
          { buttonIdx[index]===false ? 
          <Button style={{boxShadow:"0 13px 27px -5px rgba(50, 50, 93, 0.25), 0 8px 16px -8px rgba(0, 0, 0, 0.3), 0 -6px 16px -6px rgba(0, 0, 0, 0.025)",border:"none", backgroundColor:"#fafafa"}} onClick={()=>{fetchData(index)}} color="dark" outline={true} size="sm"><p style={{color:"black", fontSize:"25px", fontFamily:"BlackhanSans"}}>{index +1}.  {x["contents_name"]} <FormOutlined /></p></Button>
          :
          (<>
          <Button style={{border:"none", }} onClick={()=>{fetchData(index)}} color="dark" outline={true} size="sm"><p style={{color:"black", fontSize:"20px", fontSize:"25px", fontFamily:"BlackhanSans"}}>
            {index +1}.  {x["contents_name"]}<AiFillCaretUp/></p>
          </Button>
          
          </>)
        }
          {/* <Button style={{marginRight:"30px" ,float:"right"}}onClick={()=>gotoWritePage} color="dark" outline={true} size="sm"><p style={{color:"black", fontSize:"20px"}}>{x["contents_name"]}이동</p></Button> */}
          
          <br/> 
          {buttonIdx[index]===false?<div></div> : <div style={{  marginLeft:"4%",marginRight: "30%", fontSize: "18px", backgroundColor:"#f0f0f0", fontFamily:"Yfont"}}>{summary[index]}</div>}
          <hr style={{marginRight:"30%"}}/>
        </div>
        )
      }</div>

      <Col style={{marginTop:"10%"}}>
            <BottomNav tabs={tabs}/>
      </Col>
      </>
    )
}

export default SummaryPage;