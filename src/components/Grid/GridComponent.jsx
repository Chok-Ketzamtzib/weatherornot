import React from "react";
import ImgGreyBox from "../../images/GreyBox.svg"

export default function GridComponent({ gridItem }) {
  return (
    <div className="col-md-4 col-sm-12">
      <img src={ImgGreyBox} alt="Default Grey Box"/>
      <h3>{gridItem.header}</h3>
      <p id="gridShort">{gridItem.shortDescription}</p>
    </div>
  );
}
