import React from "react";
import "./Header.css";
import MenuBookIcon from '@material-ui/icons/MenuBook';

class Header extends React.Component{
    render(){
        return (
           <nav className="Nav">
             <div className="Nav-menus">
               <div className="Nav-brand">
                 {/* <a className="Nav-brand-logo" href="/main">
                  
                   책 한 켠
                 </a> */}
                 <MenuBookIcon/>
               </div>
             </div>
           </nav>
       );
    }   
}

export default Header;
