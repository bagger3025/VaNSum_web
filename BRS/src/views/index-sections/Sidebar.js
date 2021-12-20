import React from "react";
import {useState} from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faHome,
  faBriefcase,
  faPaperPlane,
  faQuestion,
  faImage,
  faCopy,
} from "@fortawesome/free-solid-svg-icons";
import { NavItem, NavLink, Nav } from "reactstrap";
import classNames from "classnames";
import { Link } from "react-router-dom";
import {Button} from 'reactstrap'

import SubMenu from "./SubMenu";
import text1 from "../../assets/text/text1.json";

const SideBar = ({ isOpen, toggle }) => {
  console.log(JSON.stringify(text1["contents"][0]["content"]));
  const [sentence, setSentence] = useState('');
  const [subtitle, setSubtitle] = useState('');

  const fetchData=(index)=>{
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
      },
      body: JSON.stringify({text: text1["contents"][index]["content"]})
    };

    fetch("http://112.175.32.78:443/api/kobart_rdrop_book", requestOptions)
    .then(response => response.json())
    .then(json => {
      var target = json["summary"];
      console.log(target);
      setSentence(target)
      setSubtitle(text1["contents"][index]["contents_name"])
    })
    .catch(error => {
    });
  }

  
  return (
  <><div className="sidenav" style={{marginTop:"0px"}}>
    <div className="sidebar-header">
    <span color="info" onClick={toggle} style={{ color: "#fff", marginTop:"10px" }}>
      &times;
    </span>
    <h3 style={{marginTop:"50px"}}>{text1["title"]}</h3>
  </div>
  <div className="side-menu" style={{marginLeft:"25px"}}>
    <Nav vertical className="list-unstyled pb-3">
      {/* <SubMenu title="Home" icon={faHome} items={submenus[0]} /> */}
      {
        // const map1 = array1.map(x => x * 2);
        text1["contents"].map((x, index) => 
          <NavItem key={index} onClick={()=>{fetchData(index)}}>
            <Button outline style={{border:"none", margin:"0px"}}><p style={{color:"black"}}>{x["contents_name"]}</p></Button>
          </NavItem>
        )
      }
      {/* <NavItem>
          <Button outline style={{border:"none", margin:"0px"}}>
              <p style={{color:"black"}}>전체 요약</p>
          </Button>
      </NavItem> */}
      {/* <NavItem>
          <Button outline style={{border:"none", margin:"0px"}}>
              <p style={{color:"black"}}>페이지 요약</p>
          </Button>
          
      </NavItem> */}
      {/* <NavItem>
          <Button outline style={{border:"none", margin:"0px"}}>
              <p style={{color:"black"}}>문단 요약</p>
          </Button>
      </NavItem> */}
    </Nav>
  </div>
</div>
<div style={{marginLeft:"300px", marginTop : "32px", marginRight:"100px"}}>
  <h3>{subtitle}</h3>
  <div>{sentence}</div>
</div>
  </>
)};

const submenus = [
  [
    {
      title: "Home 1",
      target: "Home-1",
    },
    {
      title: "Home 2",
      target: "Home-2",
    },
    {
      itle: "Home 3",
      target: "Home-3",
    },
  ],
  [
    {
      title: "Page 1",
      target: "Page-1",
    },
    {
      title: "Page 2",
      target: "Page-2",
    },
  ],
];

export default SideBar;
