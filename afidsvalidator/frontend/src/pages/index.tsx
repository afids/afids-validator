import { Container } from "react-bootstrap";
import { Footer } from "../components/footer";
import { NavBar } from "../components/navbar";

export default function Home() {
  return (
    <Container>
      <NavBar />

      <Footer />
    </Container>
  );
}
