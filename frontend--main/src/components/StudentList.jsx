import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/studentList.css";
import Header from './Header';
const StudentList = ({ role, onSelectStudent }) => {
  const [students, setStudents] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        let url = "https://backend1-nbbb.onrender.com/students"; // Default for Admin & Bursar

        if (role === "teacher") {
          const staffId = localStorage.getItem("staffId"); // Assuming staffId is stored after login
          url = `https://backend1-nbbb.onrender.com/staff/${staffId}/students`;
        }

        const response = await axios.get(url);
        setStudents(response.data);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch students. Please try again.");
      }
    };
    fetchStudents();
  }, [role]);

  return (
    <div className="student-list-container">
      <Header />
      <h2>Student List</h2>
      {error && <p className="error-message">{error}</p>}

      <div className="student-list">
        {students.map((student) => (
          <div
            key={student.id}
            className="student-card"
            onClick={() => onSelectStudent(student)}
          >
            <h3>{student.name}</h3>
            <p>
              <strong>Grade:</strong> {student.grade}
            </p>
            <p>
              <strong>Balance:</strong> {student.balance}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StudentList;
