import { Col, Container, Row } from "react-bootstrap";
import { Footer } from "../components/footer";
import { NavBar } from "../components/navbar";

import homeStyles from "../styles/Home.module.css";

export default function Home() {
  return (
    <Container>
      <NavBar />

      <main>
        <Row>
          <Col className="d-flex align-items-center" sm={7}>
            <p>
              Anatomical fiducials (AFIDs) is an open framework for evaluating
              correspondence in brain images and teaching neuroanatomy using
              anatomical fiducial placement. Here you will find a web
              application that allows you to upload a fiducial markup file
              (.fcsv or .json) generated using the AFIDs protocol, and validate
              that it conforms to the protocol.
            </p>
          </Col>
          <Col className="d-flex align-items-center" sm={5}>
            <video
              src="/afids-human_HD.mp4"
              className={homeStyles.afidsVideo}
              controls
            />
          </Col>
        </Row>
      </main>

      <Footer />
    </Container>
  );
}
