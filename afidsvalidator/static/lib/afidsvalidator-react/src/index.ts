import renderFooter from "./components/footer";
import renderNavbar from "./components/navbar";

globalThis.renderNavbar = renderNavbar();
globalThis.renderFooter = renderFooter();

export default {
  renderNavbar,
  renderFooter,
};
