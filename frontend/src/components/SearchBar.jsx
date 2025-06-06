import React from 'react';

const SearchBar = () => (
  <section className="ernet-searchbar-outer">
    <div className="ernet-searchbar-inner">
      <select className="ernet-search-lang">
        <option value="en">Select Language</option>
        <option value="hi">Hindi</option>
      </select>
      <input className="ernet-search-input" type="text" placeholder="Search Your Domain Here" />
      <select className="ernet-search-ext">
        <option value="">Extension</option>
        <option value="ac.in">.ac.in</option>
        <option value="edu.in">.edu.in</option>
        <option value="res.in">.res.in</option>
      </select>
      <button className="ernet-search-btn">Search Domain</button>
    </div>
    <img src="/plane.png" alt="Paper Plane" className="ernet-plane-icon" />
  </section>
);

export default SearchBar; 