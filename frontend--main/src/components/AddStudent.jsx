import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/addStudent.css";

const AddStudent = () => {
  const [name, setName] = useState("");
  const [admissionNumber, setAdmissionNumber] = useState("");
  const [grade, setGrade] = useState("");
  const [useBus, setUseBus] = useState(false);
  const [isBoarding, setIsBoarding] = useState(false);
  const [boardingFee, setBoardingFee] = useState(0);
  const [grades, setGrades] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchGrades = async () => {
      try {
        const response = await axios.get("/api/grades"); // Adjust endpoint
        setGrades(response.data);
      } catch (error) {
        console.error("Error fetching grades:", error);
      }
    };

    fetchGrades();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const studentData = {
      name,
      admission_number: admissionNumber,
      grade,
      use_bus: useBus,
      boarding_fee: boardingFee,
    };

    try {
      const response = await axios.post("/api/students", studentData);
      setMessage(response.data.message);
      setName("");
      setAdmissionNumber("");
      setGrade("");
      setUseBus(false);
      setBoardingFee(0);
    } catch (error) {
      console.error("Error adding student:", error);
      setMessage("Error adding student. Please try again.");
    }
  };

  const handleGradeChange = (e) => {
    const selectedGrade = e.target.value;
    setGrade(selectedGrade);

    if (["5", "6", "7", "8", "9", "10"].includes(selectedGrade)) {
      setIsBoarding(true);
      setBoardingFee(3500);
    } else {
      setIsBoarding(false);
      setBoardingFee(0);
    }
  };

  return (
    <div className="add-student">
      <div className="form-container">
        <h2>Add Student</h2>
        {message && <p className="message">{message}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name:</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Admission Number:</label>
            <input
              type="text"
              value={admissionNumber}
              onChange={(e) => setAdmissionNumber(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Grade:</label>
            <select value={grade} onChange={handleGradeChange} required>
              <option value="" disabled>
                Select grade
              </option>
              {grades.map((g) => (
                <option key={g.id} value={g.grade}>
                  {g.grade}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={useBus}
                onChange={() => setUseBus(!useBus)}
              />
              Will use bus
            </label>
          </div>
          {!isBoarding && (
            <div className="form-group">
              <label>Boarding Fee:</label>
              <input
                type="number"
                value={boardingFee}
                onChange={(e) => setBoardingFee(e.target.value)}
                disabled={isBoarding}
              />
            </div>
          )}
          <button type="submit" className="submit-btn">
            Add Student
          </button>
        </form>
      </div>
    </div>
  );
};

export default AddStudent;
                     
