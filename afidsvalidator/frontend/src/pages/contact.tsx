import Link from "next/link";
import { Container, Row } from "react-bootstrap";
import { Footer } from "../components/footer";
import { NavBar } from "../components/navbar";

export default function Contact() {
  return (
    <Container>
      <NavBar />

      <main>
        <Row>
          <p>
            Please reach out if you would like to contribute to this open source
            project, encounter any bugs with the validator, or have any
            questions!
          </p>

          <p>
            For any issues related to the anatomical fiducials validator, please
            create a new issue on our{" "}
            <Link
              href="https://github.com/afids/afids-validator/issues"
              target="_blank"
            >
              Github repository
            </Link>
            . For all other inquiries, please out to us via{" "}
            <Link
              href="https://mattermost.brainhack.org/brainhack/channels/afids"
              target="_blank"
            >
              Mattermost
            </Link>{" "}
            or{" "}
            <Link href="https://twitter.com/afids_project" target="_blank">
              Twitter
            </Link>
            .
          </p>

          <p>
            We will do our best to response to any messages within a reasonable
            time!
          </p>
        </Row>
      </main>

      <Footer />
    </Container>
  );
}
