import React from "react";

// reactstrap components

// // core components
// import IndexNavbar from "components/Navbars/IndexNavbar.js";
// import IndexHeader from "components/Headers/IndexHeader.js";
// import DemoFooter from "components/Footers/DemoFooter.js";

import WritePage from "views/index-sections/writePage.js";
function Index() {
  document.documentElement.classList.remove("nav-open");
  React.useEffect(() => {
    document.body.classList.add("index");
    return function cleanup() {
      document.body.classList.remove("index");
    };
  });
  return (
    <>
      <div className="main">

        <WritePage/>

      </div>
    </>
  );
}

export default Index;
