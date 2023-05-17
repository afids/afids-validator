import "bootstrap/dist/css/bootstrap.css";
import type { AppProps } from "next/app";
import Head from "next/head";
import { useEffect } from "react";
import "../styles/globals.css";

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // @ts-ignore
    import("bootstrap/dist/js/bootstrap");
  }, []);

  return (
    <>
      <Head>
        <title>AFIDs-Validator</title>
        <meta name="description" content="Anatomical Fiducials Validator" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta
          name="author"
          content="Patrick Park, Geetika Gupta, Jak Lee-Spacek, 
          Tristan Kuehn, Olivia Stanley, Jason Kai"
        />
        <link rel="icon" href="/afids.png" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}
