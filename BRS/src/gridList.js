import React, {useEffect} from 'react';
import { makeStyles } from '@material-ui/core/styles';
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';
import GridListTileBar from '@material-ui/core/GridListTileBar';
import { Nav, NavItem} from 'reactstrap';
import { NavLink } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit, faHome} from '@fortawesome/free-solid-svg-icons';
import UserGrid from './UserGrid';
import {AutoRotatingCarousel, Slide} from 'material-auto-rotating-carousel';
import useMediaQuery from "@material-ui/core/useMediaQuery";
import {
  Container,
  Col,
  Row,
  Carousel,
  CarouselItem,
  CarouselControl,
  CarouselIndicators,
  CarouselCaption,
  Modal,
  ModalHeader,
  ModalFooter,
  ModalBody,
} from "reactstrap";
import { grey } from "@material-ui/core/colors";
import Paper from '@material-ui/core/Paper';
const tabs = [{
  route: "/home",
  icon: faHome,
  label: "Home"
},{
  route: "/select",
  icon: faEdit,
  label: "Write"
}]



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
    backgroundColor: theme.palette.background.paper,
  },
  gridList: {
    width: 'auto',
    height: 'auto',
  },
  icon: {
    color: 'rgba(255, 255, 255, 0.54)',
  },
  typography: {
    "fontFamily" : `"NanumPen"`,
    "fontSize" : 25,
    "fontWeightLight": 300,
    "fontWeightRegular": 400,
    "fontWeightMedium": 500,
  },
  name: {
    "fontFamily" : `"NanumPen"`,
    "fontSize" : 18,
    "fontWeightLight": 300,
    "fontWeightRegular": 400,
    "fontWeightMedium": 500,
    textAlign : 'right'
  },
}));



function MainPage(props) {
  const classes = useStyles();
  const [isModalOpen,setModal] = React.useState(false);
  const [currentIndex,setCurrentIndex] = React.useState(0);
  const toggleModal = () => {
    setModal(!isModalOpen);
  }
  const showModalImage = (imageId) =>{
    toggleModal();
    setCurrentIndex(imageId);
  }
  return (
    <div className={classes.root}>
      <nav className="navbar navbar-expand-md navbar-light sticky-top" 	role="navigation">
            <div className="container-fluid">
              {'책 한 켠'}
            </div>
          </nav>
          <Container>
            <Col>
            <UserGrid/>
      <GridList cellHeight={200} className={classes.gridList}>
        {props.postData.map((tile,index) => (
          <GridListTile 
          key={index}
          onClick={() => showModalImage(index)}
          >
            <img src={`/img/${tile.img}.jpg`}/>
            <GridListTileBar
              title={tile.date}
              subtitle={<span> {tile.body}</span>}
            />
          </GridListTile>
        ))}
        
      </GridList>

      <Modal
          className="modal-xl"
          isOpen={isModalOpen}
          toggle={toggleModal}
        >
          <ModalHeader>{props.postData[currentIndex].date}</ModalHeader>
          <ModalBody>
            <Row>
              <Col md="12">
              <ImageCarousel postData={props.postData} currentIndex={currentIndex}/>
              </Col>
            </Row>
          </ModalBody>
       </Modal>


      </Col>
      <br/><br/><br/>
          <Col>
          <BottomNav/>
          </Col>
      </Container>
    </div>
  );
}
export default MainPage;



function ImageCarousel (props) {
  const classes = useStyles();
  var [activeIndex, setActiveIndex] = React.useState(0);
  var [animating, setAnimate] = React.useState(false);;
    useEffect(()=>{
      setActiveIndex(props.currentIndex);
  }, []);

  const next = () => {
    if (animating) return;
    const nextIndex = activeIndex === props.postData.length - 1 ? 0 : activeIndex + 1;
    setActiveIndex(nextIndex);
  };

  const previous = () => {
    if (animating) return;
    const nextIndex = activeIndex === 0 ? props.postData.length - 1 : activeIndex - 1;
    setActiveIndex(nextIndex);
  };

  const goToIndex = (newIndex) => {
    if (animating) return;
    setActiveIndex(newIndex);
  };

  const setAnimating = (value) => {
    setAnimate(value);
  };
  const slides = props.postData.map(post => {
      return (
        <CarouselItem
          onExiting={() => setAnimating(true)}
          onExited={() => setAnimating(false)}
          key={post.id}
        >
          <Paper>
          <Col>
          <div className="d-flex justify-content-center">
            <img src={`/img/${post.img}.jpg`} alt={post.body} className="img-fluid" />
          </div>
          </Col>
          <br/>
          <Col>
          <div
          className = {classes.typography}
          varient = "outlined"
          >{`${props.postData[activeIndex].body}`}
          </div>
          <div className={classes.name}>
             {`by. 김곰곰`}
          </div>
           </Col>

           <br/>
          </Paper>


        </CarouselItem>
      );
  });

    return (
      <Carousel
        activeIndex={activeIndex}
        next={next}
        previous={previous}
        interval = {false}
      >

        <CarouselIndicators
          items={props.postData}
          activeIndex={activeIndex}
          onClickHandler={goToIndex}
        />

        {slides}
        <br/>

        <CarouselControl
          direction="prev"
          directionText="Previous"
          onClickHandler={previous}
        />
        <CarouselControl
          direction="next"
          directionText="Next"
          onClickHandler={next}
        />
      </Carousel>
    );
}
