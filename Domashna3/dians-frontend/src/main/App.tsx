import { Suspense, lazy } from "react";
import Spinner from "../components/spinner";
import NavBar from "../content/navbar";
import { Route, Routes, BrowserRouter as Router } from "react-router-dom";
import BackgroundContainer from "../components/background.";
import HomePage from "../pages/home";
import GraphPage from "../pages/graph";
import TechnicalAnalysis from "../pages/technical";
import FundamentalAnalysis from "../pages/fundamental";
import Prediction from "../pages/lstm";

// Lazy load the components
const LazyRowContainer = lazy(() => import("../components/row_container"));
// const Graph = lazy(() => import("../components/line_graph"));
// const FundamentalAnalysis = lazy(() => import("../components/fundamental_analysis"));
// const LstmPredict = lazy(() => import("../components/lstm_predict"));

const App: React.FC = () => {
  return (
    <Router>
      <BackgroundContainer />
      <Suspense fallback={<Spinner />}>
        <NavBar />
        {/* Add Routes inside the ColumnContainer */}
        <LazyRowContainer>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="/technical_analysis" element={<TechnicalAnalysis />} />
               <Route path="/fundamental_analysis" element={<FundamentalAnalysis />} />
              <Route path="/lstm_predict" element={<Prediction />} />  
          </Routes>
        </LazyRowContainer>
      </Suspense>
    </Router>
  );
};

export default App;
