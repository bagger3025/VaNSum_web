import React from 'react';
import styled, {css} from 'styled-components';
import UserGrid from '../Profile/UserGrid';
import {
    Link,
    useLocation
  } from "react-router-dom";
import { Nav, NavItem} from 'reactstrap';
import { NavLink } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit, faHome} from '@fortawesome/free-solid-svg-icons';

import {
  Container,
  Col,
} from "reactstrap";

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

const ImageLink = styled(Link)`
  background: no-repeat center/100% url(/img/${({index}) => index}.jpg);
  background-size: cover;
  :hover {
      opacity: .7
    }
  ${({cascade}) => cascade && css`
    background-size: cover;
    &:nth-of-type(2n) {
        grid-row-start: span 2;
    }
  `}
  
`;

const PhotoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 305px);
  justify-content: center;
  gap:10px;
  grid-auto-rows: 305px;
  ${({cascade}) => cascade && css`
    grid-auto-rows: 200px;
  `}
  @media (max-width: 990px){
    gap: 5px;
    padding-left: 20px;
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: calc(33vw - 10px);
    }
`;

// const LinkGrid = styled.div`
//   display: grid;
//   grid-template-columns: auto auto;
//   justify-content: center;
//   gap: 20px;
//   margin-bottom: 20px;
// `;
// const TabLink = styled(Link)`
//   text-decoration: none;
//   color: #ccc;
//   text-transform: uppercase;
//   letter-spacing: 3px;
//   ${({selected}) => selected && 'color: black;'}
// `;

function Gallery(props) {
    let location = useLocation();
    return (
      <div>
          <nav className="navbar navbar-expand-md navbar-light sticky-top" 	role="navigation">
            <div className="container-fluid">
              {'책 한 켠'}
            </div>
          </nav>
          <Container>
          <Col>
          <UserGrid />
          <PhotoGrid>
          {props.postData.map(i => (
            <ImageLink
              key={i.id}
              index={i.img}
              to={{
                pathname: `/img/${i.id}`,
                state: { background: location }
              }}
              
            >
            </ImageLink>
            
          ))}
        </PhotoGrid>
          </Col>
          <br/><br/><br/><br/>
          <Col>
          <BottomNav/>
          </Col>
        </Container>
       

      </div>

    );
  }
  export default Gallery