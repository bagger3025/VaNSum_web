import React, {useState, useEffect} from "react";
import { BrowserRouter, Redirect, Route, Switch } from "react-router-dom";

// styles
import "assets/css/bootstrap.min.css";
import "assets/scss/paper-kit.scss?v=1.2.0";
import "assets/demo/demo.css?v=1.2.0";
// pages
import WritePage from "views/index-sections/writePage.js";
import SelectPage from "views/index-sections/selectPage.js";
import SummaryPage from "views/index-sections/SummaryPage.js";
import MainPage from "./gridList.js";


function Page(){
  const [Posts,setPosts] = useState([
    {id: 1, body: '테스트테스트테스트테스트테스트테스트', img: 'pig/6', date: '21/02/21'},
    // {id: 2, body: '책한권책한권책한권책한권책한권책한권', img: 'fall/5', date: '21/02/21'},
    // {id: 3, body: '테스트테스트테스트테스트테스트테스트', img: 'reon/31', date: '21/02/21'},
    // {id: 4, body: '책한권책한권책한권책한권책한권책한권', img: 'reon/7', date: '21/02/21'},
    // {id: 5, body: '책한권책한권책한권책한권책한권책한권', img: 'pig/25', date: '21/02/21'},
    // {id: 6, body: '테스트테스트테스트테스트테스트테스트', img: 'fall/6', date: '21/02/21'},
    // {id: 7, body: '테스트테스트테스트테스트테스트테스트', img: 'reon/19', date: '21/02/21'},
    // {id: 8, body: '책한권책한권책한권책한권책한권책한권', img: 'pig/31', date: '21/02/21'},
    // {id: 9, body: '책한권책한권책한권책한권책한권책한권', img: 'fall/7', date: '21/02/21'},
    // {id: 10, body: '책한권책한권책한권책한권책한권책한권', img: 'pig/12', date: '21/02/21'},
  ]);

  useEffect(()=>{
    get();
  }, []);

  function get(){
    const requestOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
      },
    };
  
    // fetch(`/api/load-post`, requestOptions)
    // .then(response => response.json())
    // .then(json => {
    //   setPosts(json['card']);
    // })
    // .catch(error => {
      
    // });
  }
 return(
 <BrowserRouter>
    <Switch>
      {/* <Route path="/main" render={(props) => <MainPage {...props} postData={Posts} />} /> */}
      <Route path="/select" render={(props) => <SelectPage {...props} />} />
      <Route path="/write/:book"  render={(props) => <WritePage {...props} />} />
      <Route path="/summary/:book" render={(props)=><SummaryPage {...props}/>}/>
      <Redirect to="/select" />
    </Switch>
  </BrowserRouter>
  );
}

export default Page;