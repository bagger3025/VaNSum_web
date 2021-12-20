import React from "react";
// reactstrap components

import MainPage from "views/index-sections/mainPage.js";



function Main() {
  const [value, setValue] = React.useState('recents');

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  document.documentElement.classList.remove("nav-open");
  React.useEffect(() => {
    document.body.classList.add("index");
    return function cleanup() {
      document.body.classList.remove("index");
    };
  });
  return (
    <>
      <Top/>
      <MainPage/>
      <Navigation/>
    </>
  );
}


export default Main;
