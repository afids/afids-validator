import React from "react";
import { Nav, Navbar, Row } from "react-bootstrap";
import * as ReactDOM from "react-dom";
import afidsBanner from "../../public/afids_banner.png";

interface NavProps {
  name: string;
  url: string;
  target: string;
}

// Default navigation bar
const navData: NavProps[] = [
  {
    name: "About",
    url: "/",
    target: "_self",
  },
  {
    name: "Protocol",
    url: "https://afids.github.io/afids-protocol/",
    target: "_blank",
  },
  {
    name: "Validator",
    url: "/app",
    target: "_self",
  },
  {
    name: "Contact",
    url: "/contact.html",
    target: "_self",
  },
  // TODO: change dependent on if user is logged in or not
  {
    name: "Login",
    url: "/login",
    target: "_self",
  },
];

const NavBar: React.FC = () => {
  return (
    <>
      <Row>
        <img
          className="mx-auto"
          src={afidsBanner}
          id="afids-banner"
          alt="Afids banner"
        ></img>
      </Row>

      <Navbar className="justify-content-center" variant="dark">
        <Nav>
          {navData.map((nav) => (
            <Nav.Link href={nav.url} key={nav.name} target={nav.target}>
              {nav.name}
            </Nav.Link>
          ))}
        </Nav>
      </Navbar>
      <hr className="nav-hr" />
    </>
  );
};

const RenderNavBar = () => {
  ReactDOM.render(<NavBar />, document.getElementById("react-navbar"));
};

export default RenderNavBar;
