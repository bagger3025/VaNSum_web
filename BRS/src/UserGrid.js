import React from 'react';
import styled from 'styled-components';
import {ProfileImage} from './ProfileImage';

const UserGridStyled = styled.div`
    display: grid;
    justify-content: center;
    margin-top: 80px;
    margin-bottom: 50px;
    gap: 15px;
    grid-template-areas: "photo name"
                         "photo label"
                         "photo description";
    @media (max-width: 990px){
        grid-template-areas: "photo name"
                                "label ."
                                "description .";
    }
`;

 const MiniUserGrid = styled.div`
    display: grid;
    justify-content: center;
    grid-template-columns: auto auto;
    gap: 5px;
    
`;

const Photo = styled.div`
    grid-area: photo;
    align-self: center;
`;

const Name = styled.div`
    grid-area: name;
    font-size: 28px;
    align-self: center;
    justify-content: center;
`;

const Label = styled.div`
    grid-area: label;
    @media (max-width: 990px){
        padding-left: 25px;
    }
`;

const Description = styled.div`
    grid-area: description;
    max-width: 400px;
    @media (max-width: 990px){
        grid-column: 1/3;
        padding-left: 25px;
    }
`;
export default function() {
    return <UserGridStyled> 
            <MiniUserGrid>
            <Photo><ProfileImage/>
            <Name>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;김곰곰</Name>
            </Photo>
            </MiniUserGrid>
            <Label><strong>4871</strong> followers </Label>

            <Description>'책한켠'테스트 프로필 자기소개. '책한켠'은 독서 후 감상평 작성을 도와주는 어플리케이션입니다.</Description>
         </UserGridStyled>;
}