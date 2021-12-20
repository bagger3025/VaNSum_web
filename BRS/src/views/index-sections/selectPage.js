import React,{useEffect} from 'react';

import { Redirect, Link, Route, useHistory, useLocation} from "react-router-dom";
import { makeStyles } from '@material-ui/core/styles';
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';
import GridListTileBar from '@material-ui/core/GridListTileBar';
import MenuBookIcon from '@material-ui/icons/MenuBook';
import IconButton from "@material-ui/core/IconButton"
import Toolbar from '@material-ui/core/Toolbar';
import { NavLink } from "react-router-dom";
import InfoIcon from "@material-ui/icons/Info"
import {Document, Page} from "react-pdf";
import CA from "../../assets/pdf/CA.pdf"
import CJ from "../../assets/pdf/CJ.pdf"
import LG from "../../assets/pdf/LG.pdf"
import ROB from "../../assets/pdf/ROB.pdf"
import Text1 from "../../assets/pdf/Text1.pdf"
import Text2 from "../../assets/pdf/Text2.pdf"
import Text3 from "../../assets/pdf/Text3.pdf"
import { Nav, NavItem} from 'reactstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {faEdit, faHome, faBookOpen} from '@fortawesome/free-solid-svg-icons';
import {FilePdfOutlined, FileDoneOutlined} from "@ant-design/icons"
import {Button} from 'reactstrap'
import {
  Container,
  Col,
} from "reactstrap";
import sum from './sum.jpg'
import text11 from "../../assets/text/text1.json";
import text2 from "../../assets/text/text2.json";
import text3 from "../../assets/text/text3.json"
import text4 from "../../assets/text/text4.json"
import text5 from "../../assets/text/text5.json"
import text6 from "../../assets/text/report6.json"
import text7 from "../../assets/text/report7.json"
import text8 from "../../assets/text/report8.json"

const textList = [text11, text2,text3,text6, text7, text8];
const tabs = [{
  route: "/home",
  icon: faHome,
  label: "Home"
}
]

const bookPDF=[
  Text1, Text2, Text3
]

const reportPDF=[
  CJ, LG, ROB
]

// const [texts, setTexts] = React.useState([]);

// const [subTitleLoc, setSubTitleLoc] = React.useState([]);

const BottomNav = (props) => {
    return (
        <div>
          
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


const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    overflow: 'hidden',
    backgroundColor: 'rgba(255, 255, 255, 0.54)',
  },
  gridList: {
    width: 'auto',
    height: 'auto',
  },
  icon: {
    color: 'rgba(255, 255, 255, 0.54)',
  },
  bookImg:{
    width: 'auto',
    height: 'auto'
  }
}));



// const tileData = [
// {
//   id: 1,
//   img: './img/fall/1.jpg',
//   title: '풍성한 가을 채소밭',
//   book: 'fall'
// },
// {
//   id: 2,
//   img: './img/pig/1.jpg',
//   title: '아기돼지 삼형제',
//   book: 'pig'
// },
// {
//   id: 3,
//   img: './img/reon/1.jpg',
//   title: '리옹',
//   book: 'reon'
// },

// ];

const tileData = [
  {
    id: 1,
    img: './img/fall/img1.jpg',
    title: '문화정책에서 예술강사 육성지원의 전망과 과제',
    book: 'text1'
  },
  {
    id: 2,
    img: './img/fall/img2.jpg',
    title: '2013년 한국영화산업 결산',
    book: 'text2'
  },
  {
    id: 3,
    img: './img/fall/img3.jpg',
    title: '영화인지향상연구',
    book: 'text3'
  },
  // {
  //   id: 4,
  //   img: './img/fall/img4.jpg',
  //   title: '아시아영화산업 현황과 지역내 협력방안 연구',
  //   book: 'text4'
  // },
  // {
  //   id:5,
  //   img:'./img/fall/img5.jpg',
  //   title: '저예산 디지털연구',
  //   book: 'text5'
  // },
  
];

const tileData_report=[
  {
    id:6,
    img:'./img/fall/cgv.jpg',
    title: "CJ CGV: 코로나19의 상흔에서 천천히 회복중",
    book: "text6"
  },
  {
    id:7,
    img:'./img/fall/lg.jpg',
    title : "LG화학: 테슬라 향 원통형 사업 가치에 주목할 시점",
    book:"text7"
  },
  {
    id:8,
    img:"./img/fall/ro.jpg",
    title : "로블록스 성장의 시사점",
    book:"text8"
  }
]




// function generateText(){
//   var page_list = [];
//   var page_index_list = [];
//   for(var i=0;i<text1["contents"].length;i++){
//     var sub_content = text1["contents"][i];
//     var sub_content_text = sub_content["contents_name"] + "\n";
//     page_index_list.push(page_list.length);
//     for(var j=0;j<sub_content["content"].length;j++){
//       if(sub_content_text === "")
//         sub_content_text = sub_content["content"][j];
//       else if(sub_content_text.length + sub_content["content"][j].length > 500){
//         page_list.push(sub_content_text);
//         sub_content_text = sub_content["content"][j];
//       }
//       else{
//         sub_content_text = sub_content_text + " " + sub_content["content"][j];
//       }

//       if(j === sub_content["content"].length - 1){
//         page_list.push(sub_content_text);
//       }
//     }
//   }
//   setButLoc(textState)
//   console.log(butLoc)
//   console.log(page_list);
//   console.log(page_index_list);
// }
// let [redir, setRedir] = React.useState({redirect: false});
// const setRedirect = () => {
//   setRedir({
//     redirect: true
//   })
// }

function TitlebarGridList({items, textState}) {
  const classes = useStyles();
  console.log(items)
  console.log(textState)
  let [redir, setRedir] = React.useState({redirect: false});
  let [book, setBook] = React.useState('fall');

  let history = useHistory();

  
  const setRedirect = (bookName, items, textState) => {
    setBook(`${bookName}`)
    console.log(bookName)
    history.push({pathname:`write/${bookName}`, state:{book:book, items:items, textState:textState}})
  }
  // function renderRedirect(){
  //   if (redir.redirect) {
  //     return <Redirect to= {`write/${book}`} />
  //   }
  //}
  const [genreButton, setGenreButton] = React.useState(false)// false면 레포트, true면 도서
  return (
    <>
    {/* {renderRedirect()} */}
    <Container>
      <Col>
    <div className={classes.root}>
        <nav className="navbar navbar-expand-md navbar-light sticky-top" 	role="navigation">
        <div className="container-fluid">
            <Nav className="ml-auto">
              
              <NavItem>
              <Toolbar>
              <FileDoneOutlined style={{fontSize:"25px"}}/> <Button style={{border:"none"}} onClick={()=>setGenreButton(false)} color="dark" outline={true} size="lg"><div style={{color:"black", fontSize:"25px"}}>주식종목 분석 레포트</div></Button>
              </Toolbar>
              </NavItem>
              <NavItem>
              <Toolbar>
                <MenuBookIcon/> <Button style={{border:"none"}} onClick={()=>setGenreButton(true)} color="dark" outline={true} size="lg"><div style={{color:"black", fontSize:"25px"}}>도서</div></Button>
              </Toolbar>
              </NavItem>
            </Nav>
        </div>
      </nav>
      
        
          {
            genreButton?(
              <GridList cellHeight={300} className={classes.gridList}>
              <GridListTile key="Subheader" cols={2} style={{ height: 'auto' }}>
              </GridListTile>
              {tileData.map((tile, idx) => (
                <GridListTile style={{}} key={tile.img} > 
                  <img  src={tile.img} alt={tile.title} onClick={()=>setRedirect(tile.book, items[idx], textState[idx])}/>
                  <GridListTileBar
                    title={tile.title.length>= 18 ? (tile.title.slice(0,18)+"...") : (tile.title)}
                    actionIcon={
                      <>
                      <IconButton 
                      id = {tile.book}
                      onClick={(e)=>{history.push({
                        pathname:`/summary/${e.currentTarget.id}`,
                        state : {book:e.currentTarget.id, items:items[idx], textState:textState[idx]}
                      })}}>
                        <div >
                          <FontAwesomeIcon style={{color:"white"}} size="sm" icon={faBookOpen}/>
                          <div style={{color:"white", fontSize:"10px"}}>요약</div>
                        </div>
                      </IconButton>
                      <IconButton 
                      id = {tile.book}
                      >
                        <div >
                        <Link to={bookPDF[idx]} target="_blank">
                            <FilePdfOutlined style={{color:"white"}}/>
                            <div style={{color:"white", fontSize:"10px"}}>원문</div>
                          </Link>
                        </div>
                        <div>

                        </div>
                      </IconButton>
                      </>
                    }
                  />
                  
                </GridListTile>
              ))}
              </GridList>
            ):(
              <GridList cellHeight={300} className={classes.gridList}>
              <GridListTile key="Subheader" cols={2} style={{ height: 'auto' }}>
              </GridListTile>
              {tileData_report.map((tile, idx) => (
                <GridListTile style={{}} key={tile.img} > 
                  <img  src={tile.img} alt={tile.title} onClick={()=>setRedirect(tile.book, items[idx+3], textState[idx+3])}/>
                  <GridListTileBar
                    title={tile.title.length>= 25 ? (tile.title.slice(0,23)+"...") : (tile.title)}
                    actionIcon={
                      <>
                      <IconButton 
                      id = {tile.book}
                      onClick={(e)=>{history.push({
                        pathname:`/summary/${e.currentTarget.id}`,
                        state : {book:e.currentTarget.id, items:items[idx+3], textState:textState[idx+3]}
                      })}}>
                        <div >
                          <FontAwesomeIcon style={{color:"white"}} size="sm" icon={faBookOpen}/>
                          <div style={{color:"white", fontSize:"10px"}}>요약</div>
                        </div>
                      </IconButton>
                      <IconButton 
                      id = {tile.book}
                      >
                        <div >
                          <Link to={reportPDF[idx]} target="_blank">
                            <FilePdfOutlined style={{color:"white"}}/>
                            <div style={{color:"white", fontSize:"10px"}}>원문</div>
                          </Link>
                        </div>
                        <div>

                        </div>
                      </IconButton>
                      </>
                    }
                  />
                </GridListTile>
              ))}
              </GridList>
            )
          }
        </div>
        </Col>
        
        <br/><br/><br/><br/>
        <Col>
          <BottomNav/>
        </Col>

    </Container>
    </>
  );
}

function SelectPage({ }) {
  
  const [textState, setTextState] = React.useState([]);
  const [items, setItems] = React.useState([])  
  let items_copy = []
  let textState_copy=[]
  useEffect(()=>{
    var page_list = [];
    var page_index_list=[];
    for (var k =0 ; k<textList.length;k++){
      for(var i =0;i<textList[k]["contents"].length;i++){
        var sub_content = textList[k]["contents"][i]["content"];
        // var sub_content_text = sub_content["contents_name"] + "\n";
        var sub_content_text = "";
        page_index_list.push(page_list.length);
        for(var j=0;j<sub_content.length;j++){
          if(sub_content_text === "")
            sub_content_text = sub_content[j];
          else if(sub_content_text.length + sub_content[j].length > 500){
            page_list.push(sub_content_text);
            sub_content_text = sub_content[j];
          }
          else{
            sub_content_text = sub_content_text + " " + sub_content[j];
          }
  
          if(j === sub_content.length - 1){
            page_list.push(sub_content_text);
          }
        }
      }
      
      items_copy.push(page_list)
      // items_copy[k]=page_list;
      
      textState_copy.push(page_index_list)
      // console.log(page_list)
      // console.log(page_index_list)
      // textState_copy[k] = page_index_list;
      

      page_list=[]
      page_index_list=[]
    }
    console.log(textState_copy)
    console.log(items_copy)
    setItems(items_copy)
    setTextState(textState_copy);
    console.log(items)
    console.log(textState)
  },[])
  return (
    <div>
        <TitlebarGridList items={items} textState={textState}/>
    </div>
  );
}



export default SelectPage;