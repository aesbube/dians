import React from "react";
import { Suspense, lazy } from "react";
// import Background from "../components/background";
import Spinner from "../components/spinner";


const LazyColumnContainer = lazy(
  () => import("../components/column_container")
);

const App: React.FC = () => {
  return (
    <>
      {/* <Background /> */}
      
            <h1>DIANS</h1>
            <p>
              DIANS is a web application that allows users to create, read, update, and delete notes.
            </p>   
         
    </>
  );
};

export default App;