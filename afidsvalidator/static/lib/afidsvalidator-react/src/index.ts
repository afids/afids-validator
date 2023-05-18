import RenderFooter from "./components/Footer";
import RenderNavBar from "./components/NavBar";

globalThis.RenderNavBar = RenderNavBar();
globalThis.RenderFooter = RenderFooter();

export default {
  RenderNavBar,
  RenderFooter,
};
