import React, {useEffect} from "react";
import FetchIntercept from 'fetch-intercept';
import { Dropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
// reactstrap components
import MenuBookIcon from '@material-ui/icons/MenuBook';
import {
  Card,
  Container,
  Col,
  Carousel,
  CarouselItem,
  CarouselIndicators,
  CarouselCaption,
} from "reactstrap";
import "./App.css"
import {useState} from "react";
import {Button} from 'reactstrap'
import Toolbar from '@material-ui/core/Toolbar';
import Chip from '@material-ui/core/Chip';
import Fab from '@material-ui/core/Fab';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import Backdrop from '@material-ui/core/Backdrop';
import CircularProgress from '@material-ui/core/CircularProgress';
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import { Nav, NavItem} from 'reactstrap';
import Switch from '@material-ui/core/Switch';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import StarIcon from '@material-ui/icons/Star';
import StarBorderIcon from '@material-ui/icons/StarBorder';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from '@material-ui/core/Tooltip';
import RobotIcon from "./robot.png";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {faHome, faSave, faBookOpen} from '@fortawesome/free-solid-svg-icons';
import { NavLink } from 'react-router-dom';
import ListItemText from '@material-ui/core/ListItemText';
import Paper from '@material-ui/core/Paper';
import { Redirect, Link, Route, useHistory, useLocation } from "react-router-dom";


import text11 from "../../assets/text/text1.json";
import text2 from "../../assets/text/text2.json";
import text3 from "../../assets/text/text3.json"
import text4 from "../../assets/text/text4.json"
import text5 from "../../assets/text/text5.json"
import text6 from "../../assets/text/report6.json"
import text7 from "../../assets/text/report7.json"
import text8 from "../../assets/text/report8.json"



const useStyles = makeStyles((theme) => ({
  root: {
    backgroundColor: theme.palette.background.paper,
    width: 500,
    position: 'relative',
    minHeight: 200,
  },
  fab: {
    position: 'absolute',
    bottom: theme.spacing(2),
    right: theme.spacing(4),
  },
  icon: {
    width: '52px',
    height: '52px'
  },
  backdrop: {
    zIndex: theme.zIndex.drawer + 1,
    color: '#fff',
  },
  paper: {
    display: 'flex',
    justifyContent: 'center',
    flexWrap: 'wrap',
    listStyle: 'none',
    padding: theme.spacing(0.5),
    margin: 0,
  },
  chip: {
    align : 'center',
    textAlign: 'center',
    margin: theme.spacing(0.1),
  },
  pin: {
    position: 'absolute',
    top: theme.spacing(0),
    left: theme.spacing(2),
    zIndex : 30
  },
}));

function WritePage(props) {
  // const [text1, setText1] = useState(text11)
  // let location = useLocation();
  console.log(props.location.state)
  let history = useHistory()
  
  console.log(props.location.state)
  const [items, setItems] = React.useState(props.location.state.items);
  console.log(props.location.state)
  console.log(props.location.pathname.split('/')[2])
  console.log(props.location.state.items)
  let t=props.location.pathname.split('/')[2];
  console.log(t)
  let text1=text11
  
  if(t==="text1"){
    text1=text11
  }
  if(t==="text2"){
    text1=text2
  }
  if(t==="text3"){
    text1=text3
  }
  if(t=="text4"){
    text1=text4
  }
  if(t=="text5"){
    text1=text5
  }
  if(t=="text6"){
    console.log("asd");
    text1=text6
  }
  if(t=="text7"){
    text1=text7
  }
  if(t=="text8"){
    text1=text8
  }

  const handleSendState = () =>{
    console.log(typeof t)
    history.push({
      pathname:`/summary/${t}`,
      state: {book:props.location.state.book,
         items : props.location.state.items,
          textState:props.location.state.textState}
    })
  }


  const tabs = [{
    func:null,
    route: "/main",
    icon: faHome,
    label: "Home",
  },
  {
    func: handleSendState,
    route:`/summary/${t}`,
    icon: faBookOpen,
    label:"Summary",
  }]
  const [text, setText] = React.useState('');
  const [words, setWords] = React.useState(['','','','','']);
  const [sentences, setSentences] = React.useState(['','','']);
  let [state, setState] = React.useState(false);
  let [sent, setSent] = React.useState(false);
  const [toggle, setToggle] = React.useState(false);
  const [animating, setAnimating] = React.useState(false);
  const [autoPlay, setAutoPlay] = React.useState(false);
  
  const [activeIndex, setActiveIndex] = React.useState(1);
  const [curSummary, setCurSummary] = React.useState('');
  
  

  useEffect(()=>{
    // generateImage();
    // generateText();

    if(props.location.state.curState){
      setActiveIndex(props.location.state.curState);
    }
    else{
      setActiveIndex(0)
    }

  }, []);


  function renderRedirect(){
    if (false) {
      return <Redirect to='/main' />
    }
  }
  const unregister = FetchIntercept.register({
    request: function (url, config) {
      setState(true);
      return [url, config];
    },

    requestError: function (error) {
      setState(false);
      return Promise.reject(error);
    },

    response: function (response) {
      setState(false);
      return response;
    },

    responseError: function (error) {
      setState(false);
      return Promise.reject(error);
    }
  });
  const settings = {
    dots:true,
    className: "center",
    infinite: true,
    centerPadding: "1px",
    slidesToShow: 3,
    swipeToSlide: true,
    afterChange: function(index) {
      console.log(
        `Slider Changed to: ${index + 1}, background: #222; color: #bada55`
      );
    }
  };
  const handleChange = (event) => {
    setText(event.target.value);
  };
  function _post(Data) {
    const raw = JSON.stringify(Data);
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
      },
      body: raw
    };

    fetch(`/api/review-generation`, requestOptions)
    .then(response => response.json())
    .then(json => {
      toggle?setSentences(json['sentences']):setWords(json['words'])
      setSent(true);
    })
    .catch(error => {
      setText(error);
      setSent(true);
    });
    unregister();
  }

  function save(Data) {
    const raw = JSON.stringify(Data);
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
      },
      body: raw
    };


    // fetch(`/api/save-post`, requestOptions)
    // .then(response => {
    //   // return(<Redirect to="/main" />);
    //   setRedirect();
    // })
    // .catch(error => {
    //   setText(error);
    //   setState(false);
    // });
    unregister();
  }
  
  function handleClick() {
    const Data = {
      textID: "ReviewGeneration",
      content: text,
      model: "ogeoseo",
      temperature: 1.0,
      top_p: 1,
      top_k: 40,
      recommend_flag: toggle,
      auto_flag: false,
      count: (toggle ? 3 : 5)
    }
    setState(true);
    _post(Data);
    }
  const classes = useStyles();
  function handleSave() {
    const Data = {
      id:0,
      body:text,
      img:`./${props.match.params.book}/${activeIndex+1}`
    }
    setState(true);
    save(Data);
    }

  const handlePin = () => {
    setAutoPlay((prev) => !prev);
  };

  const toggleChecked = () => {
    setToggle((prev) => !prev);
  };
  const handleListItemClick = (value) => {
    setText(text + value);
  };

  const onExiting = () => {
    setAnimating(true);
  };
  const onExited = () => {
    setAnimating(false);
  };
  const next = () => {
    if (animating) return;
    const nextIndex = activeIndex === items.length - 1 ? 0 : activeIndex + 1;
    setActiveIndex(nextIndex);
  };
  const previous = () => {
    if (animating) return;
    const nextIndex = activeIndex === 0 ? items.length - 1 : activeIndex - 1;
    setActiveIndex(nextIndex);
  };
  const goToIndex = (newIndex) => {
    if (animating) return;
    setActiveIndex(newIndex);
  };

  const [isOpen, setIsOpen] = useState(false)
  const toggle1 =()=>{
    setIsOpen(!isOpen)
  }
  const showPassage=()=>{
    let _list = [];
    console.log(text1)
    for (let i = 0;i<text1["contents"].length;i++){
      _list.push(
        <DropdownItem onClick={()=>{setActiveIndex(props.location.state.textState[i])}}>
          {text1["contents"][i]["contents_name"]}
        </DropdownItem>
      )
    }

    return _list;
  }

  const showIndex=()=>{
    let border = props.location.state.textState;
    for( let i =0;i<=border.length;i++){
      if(border[i]>activeIndex){
        return <div style={{fontSize:"25px", textAlign:"center"}}> {i}. {text1["contents"][i-1]["contents_name"]}</div>
      }
      else if(i===border.length){
        return <div style={{fontSize:"25px", textAlign:"center"}}> {i}. {text1["contents"][i-1]["contents_name"]}</div>
      }
    }
  }

  const showSummary=()=>{
    let border = props.location.state.textState;
    console.log(activeIndex)
    for(let i =0;i<=border.length;i++){
      if(border[i]>activeIndex){
        return <div style={{fontSize:"19px"}}>{text1["contents"][i-1]["summary"]}</div>
      }
      else if(i===border.length){
        return <div style={{fontSize:"19px"}}>{text1["contents"][i-1]["summary"]}</div>
      }
    }
  }
  const [showDiv, setShowDiv] = useState(false)
  return (
    <>
    {renderRedirect()}
    <nav className="navbar navbar-expand-md navbar-light sticky-top" 	role="navigation">
        <div className="container-fluid">
            <Nav className="mr-auto">
              <NavItem>
              <Toolbar>
                <div style={{fontSize:"25px"}}></div>
              </Toolbar>
              </NavItem>
            </Nav>
            <Nav className="ml-auto">
              <NavItem>
              <Toolbar>
                <MenuBookIcon size="lg"/> {text1["title"]}
              </Toolbar>
              </NavItem>
            </Nav>
        </div>
      </nav>
      <div className="section pt-o" id="carousel">
      {showIndex()}
        <Container>
            <Col className="ml-auto mr-auto" md="12">
            {/* <Tooltip title="대표 사진 고정" >
                <IconButton className={classes.pin} onClick={handlePin}>
                    {autoPlay ? <StarBorderIcon/> : <StarIcon color='secondary'/>}
                </IconButton>
                </Tooltip>   */}
              <Card className="page-carousel" >
                <Carousel
                  activeIndex={activeIndex}
                  next={next}
                  previous={previous}
                  interval = {autoPlay?5000:false}
                >
                  <CarouselIndicators
                    items={items}
                    activeIndex={activeIndex}
                    onClickHandler={goToIndex}
                  />


                  {items.map((item, index) => {
                    
                    return (
                      <CarouselItem
                        onExiting={onExiting}
                        onExited={onExited}
                        key={index}
                      >
                        <div style={{margin: "100px 150px", fontSize: "20px"}}>{item}</div>
                        {/* <img src={item.src} alt={item.altText} />/*}
                        {/* <div style={{marginLeft: "200px", marginBottom: "200px"}}>ALLOHA!</div> */}
                        <CarouselCaption
                          captionText={""}
                          captionHeader=""
                        />
                      </CarouselItem>
                    );
                  })}
                  <a
                    className="left carousel-control carousel-control-prev"
                    data-slide="prev"
                    href="#pablo"
                    onClick={(e) => {
                      e.preventDefault();
                      previous();
                    }}
                    role="button"
                  >
                    <span className="fa fa-angle-left" />
                    <span className="sr-only">Previous</span>
                  </a>
                  <a
                    className="right carousel-control carousel-control-next"
                    data-slide="next"
                    href="#pablo"
                    onClick={(e) => {
                      e.preventDefault();
                      next();
                    }}
                    role="button"
                  >
                    <span className="fa fa-angle-right" />
                    <span className="sr-only">Next</span>
                  </a>
                </Carousel>
              </Card>
            </Col>
            <Col>
            {/* <TextField
            id="outlined-textarea"
            InputProps={{
              readOnly: false,
            }}
            label="요약"
            rows = {10}
            multiline
            fullWidth
            variant="outlined"
            onChange = {handleChange}
            >
              {showSummary()}
            </TextField> */}
            <span style={{backgroundColor:"red",marginBottom:"26px",color:"white", fontSize:"24px", fontFamily:"BlackhanSans"}} onClick={()=>setShowDiv(!showDiv)}> 현재 문단 생성식 요약 결과 </span>
            {
              <div style={{borderTop:"1px solid #fafafa", marginLeft:"20px",marginTop:"10px",fontFamily:"Yfont"}}>
                {showSummary()}
              </div>
              // showDiv?(
              //   <div style={{borderTop:"1px solid #fafafa", marginLeft:"10px"}}>
              //     {showSummary()}
              //   </div>
              // ):(
              //   <div style={{borderTop:"1px solid #fafafa"}}>
                
              //   </div>
              // )
            }
            {/* <Fab className={classes.fab}  onClick={handleClick}>
            <img src={RobotIcon} className={classes.icon}/>
            </Fab> */}
          </Col>
          <br/>
          <Col>
          {toggle?
            <>

            {sent ? sentences.map((sentence) => {
                  return (
                    <List>
                      <ListItem
                      onClick={()=>handleListItemClick(sentence)}
                      >
                        <Paper className={classes.paper}>
                        <ListItemText align='left'>
                          {sentence}
                        </ListItemText>
                        </Paper>
                      {/* <Chip
                      variant="outlined"
                      label={sentence}
                      className={classes.chip}
                      onClick={()=>handleListItemClick(sentence)}
                      /> */}
                      </ListItem>
                    </List>
                    
                  );
                }): ''}
            </> 
          :
              <Slider {...settings}>
                {sent ? words.map((word) => {
                  return (
                    <Chip
                      size="small"
                      variant="outlined"
                      label={word}
                      className={classes.chip}
                      onClick={()=>handleListItemClick(word)}
                   />
                  );
                }): ''}
              </Slider>
            }
          </Col>
          <br/><br/><br/><br/>
          <Col>
          <nav className="navbar fixed-bottom navbar-light bottom-tab-nav" role="navigation">
            <Nav className="w-100">
              <div className=" d-flex flex-row justify-content-around w-100">
                {
                  tabs.map((tab, index) =>(
                    <NavItem key={`tab-${index}`}>
                      <NavLink onClick={tab.func} to={{
                        pathname : `${tab.route}`,
                        state:{
                          book:t, 
                          items : props.location.state.items, 
                          textState:props.location.state.textState
                        }
                      }} className="nav-link" activeClassName="active">
                        <div className="row d-flex flex-column justify-content-center align-items-center">
                        <FontAwesomeIcon size="lg" icon={tab.icon}/>
                          <div>{tab.label}</div>
                        </div>
                      </NavLink>
                    </NavItem>
                  ))
                }
                <NavItem key = {`tab-3`}>
                <Dropdown direction="up" isOpen={isOpen} toggle={toggle1} size = "sm">
                  <DropdownToggle caret>
                  <MenuBookIcon/> 목차
                  </DropdownToggle>
                  <DropdownMenu>
                    {showPassage()}
                  </DropdownMenu>
                </Dropdown>
                </NavItem>

              </div>

            </Nav>
          </nav>
          </Col>
        </Container>
      <Backdrop className={classes.backdrop} open={state}>
        <CircularProgress color="inherit" />
      </Backdrop>
      </div>

    </>
  );
}
export default WritePage;
