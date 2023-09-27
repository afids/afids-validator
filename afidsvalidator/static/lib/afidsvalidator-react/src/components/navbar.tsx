import * as React from "react";
import { Nav, Navbar, Row } from "react-bootstrap";
import * as ReactDOM from "react-dom";
import afidsBanner from "../../public/afids_banner.png";

interface NavBarProps {
  isLoggedIn: boolean;
}

interface NavProps {
  name: string;
  url: string;
  target: string;
}

function NavBar({ isLoggedIn }: NavBarProps) {
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
      url: "/app.html",
      target: "_self",
    },
    {
      name: "Contact",
      url: "/contact.html",
      target: "_self",
    },
    isLoggedIn
      ? { name: "Logout", url: "/logout.html", target: "_self" }
      : { name: "Login", url: "/login.html", target: "_self" },
  ];

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
}

// Need to pass currentUser from backend
function renderNavbar(isLoggedIn: boolean) {
  ReactDOM.render(
    React.createElement(NavBar, { isLoggedIn: isLoggedIn }),
    document.getElementById("react-navbar")
  );
}

export default renderNavbar;
