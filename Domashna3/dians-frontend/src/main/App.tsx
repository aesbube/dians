import { Suspense, lazy } from "react";
// import Background from "../components/background";
import Spinner from "../components/spinner";
import ColumnContainer from "../components/column_container";
import Column from "../components/column";

const LazyColumnContainer = lazy(
  () => import("../components/column_container")
);

const App: React.FC = () => {
  return (
    <>
      <Suspense fallback={<Spinner />}>
        <LazyColumnContainer>
          {/* <Background /> */}
          <ColumnContainer>
            <Column>
              <h1>DIANS</h1>
            </Column>
            <Column>
              <p>DIANS is a social network for developers.</p>
            </Column>
          </ColumnContainer>
        </LazyColumnContainer>
      </Suspense>
    </>
  );
};

export default App;
