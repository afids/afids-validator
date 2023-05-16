import Image from "next/image";
import { Nav, Navbar, Row } from "react-bootstrap";
import afidsBanner from "../../public/afids_banner.png";

interface NavProps {
  name: string;
  url: string;
}

// Default navigation bar
const navData: NavProps[] = [
  {
    name: "About",
    url: "/",
  },
  {
    name: "Protocol",
    url: "https://afids.github.io/afids-protocol/",
  },
  {
    name: "Validator",
    url: "/app",
  },
  {
    name: "Contact",
    url: "/contact",
  },
  // TODO: change dependent on if user is logged in or not
  {
    name: "Login",
    url: "/login",
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
            <Nav.Link href={nav.url} key={nav.name}>
              {nav.name}
            </Nav.Link>
          ))}
        </Nav>
      </Navbar>
      <hr className="nav-hr" />
    </>
  );
};
