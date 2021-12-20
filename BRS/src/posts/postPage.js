import React from "react";
import "./postPage.css";


import Header from "./components/Header";
import Posts from "./components/Posts";
import { Nav, NavItem} from 'reactstrap';
import { NavLink } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit, faHome} from '@fortawesome/free-solid-svg-icons';

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

const PostPage = (props) =>{
    return (
          <>
          <Header />
          <Posts Data = {props.postData} id = {props.match.params.id}/>
          <BottomNav/>
          </>
    );
}

export default PostPage;
