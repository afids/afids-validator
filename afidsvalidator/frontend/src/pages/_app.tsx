import "bootstrap/dist/css/bootstrap.css";
import type { AppProps } from "next/app";
import { useEffect } from "react";
import "../styles/globals.css";

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    import("bootstrap/dist/js/bootstrap");
  }, []);

  return <Component {...pageProps} />;
}
