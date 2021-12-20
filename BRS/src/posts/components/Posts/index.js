import React from "react";
import "./Posts.css";
import Post from "../Post";

const Posts = (props) =>{
    return (
          <Post
                nickname={'김곰곰'}
                avatar={'./kogi.jpg'}
                image={`./${props.Data[props.id-1].img}.jpg`}
                caption={`${props.Data[props.id-1].body}`}
              />
    );
}

export default Posts;
