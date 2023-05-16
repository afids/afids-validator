import Image from "next/image";
import { Nav, Navbar, Row } from "react-bootstrap";
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
    url: "/contact",
    target: "_self",
  },
  // TODO: change dependent on if user is logged in or not
  {
    name: "Login",
    url: "/login",
    target: "_self",
  },
];

export const NavBar = () => {
  return (
    <>
      <Row>
        <Image className="mx-auto" src={afidsBanner} alt="Afids banner" />
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
