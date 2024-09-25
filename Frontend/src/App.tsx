import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";

import Home from "./pages/Home";
import { LoginForm } from "./pages/Login";
import { RegisterForm } from "./pages/Register";

function App() {

  return (
    <div >
        <Router>
          <Routes>
            <Route
              path="/"
              element={<Home/>}
            />
            <Route
              path="/login"
              element={<LoginForm/>}
            />
            <Route
              path="/register"
              element={<RegisterForm/>}
            />
          </Routes>
        </Router>
     
    </div>
  );
}

export default App;