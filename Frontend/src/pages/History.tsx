import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import Graph from "../components/Graph";

const History = () => {
  const { data, setData } = useAuth();
  console.log(data);
  const navigate = useNavigate();
  const handleremove = () => {
    setData(null);
    navigate("/");
  };
  return (
    <>
      <div className="w-[80%] p-10 flex flex-col mx-auto items-center justify-center">
        <Graph plotData={data} remove={handleremove} />
      </div>
    </>
  );
};

export default History;
