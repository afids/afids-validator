import { faGithub, faTwitter } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import * as React from "react";
import { Row } from "react-bootstrap";
import * as ReactDOM from "react-dom";

interface footerProps {
  name: string;
  url: string;
  icon: any;
}

const footerData: footerProps[] = [
  {
    name: "Twitter",
    url: "https://twitter.com/afids_project",
    icon: faTwitter,
  },
  {
    name: "Github",
    url: "https://github.com/afids",
    icon: faGithub,
  },
];

const Footer: React.FC = () => {
  const startYear: number = 2018;
  let curYear: number = new Date().getFullYear();

  return (
    <footer>
      <div className="flex">
        {footerData.map((foot) => (
          <a href={foot.url} key={foot.name} target="_blank">
            <FontAwesomeIcon icon={foot.icon} className="footIcon" />
          </a>
        ))}
      </div>
      <Row>
        {startYear} - {curYear} Anatomical Fiducials Validator
      </Row>
    </footer>
  );
};

const RenderFooter = () => {
  ReactDOM.render(<Footer />, document.getElementById("react-footer"));
};

export default RenderFooter;
