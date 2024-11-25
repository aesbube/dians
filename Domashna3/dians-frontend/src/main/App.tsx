import { Suspense, lazy } from "react";
import Spinner from "../components/spinner";
import ColumnContainer from "../components/column_container";
import NavBar from "../content/navbar";
import { Route, Routes, BrowserRouter as Router } from "react-router-dom";
import BackgroundContainer from "../components/background.";
import HomePage from "../pages/home";

// Lazy load the components
const LazyColumnContainer = lazy(
  () => import("../components/column_container")
);
// const Graph = lazy(() => import("../components/graph"));
// const TechnicalAnalysis = lazy(() => import("../components/technical_analysis"));
// const FundamentalAnalysis = lazy(() => import("../components/fundamental_analysis"));
// const LstmPredict = lazy(() => import("../components/lstm_predict"));

const App: React.FC = () => {
  return (
    <Router>
      <BackgroundContainer />
      <Suspense fallback={<Spinner />}>
        <LazyColumnContainer>
          <NavBar />
          <ColumnContainer>
            {/* Add Routes inside the ColumnContainer */}
            <Routes>
              <Route path="/" element={<HomePage />} />
              {/* <Route path="/graph" element={<Graph />} />
              <Route path="/technical" element={<TechnicalAnalysis />} />
              <Route path="/fundamental" element={<FundamentalAnalysis />} />
              <Route path="/lstm" element={<LstmPredict />} /> */}
            </Routes>
          </ColumnContainer>
        </LazyColumnContainer>
      </Suspense>
    </Router>
  );
};

export default App;
