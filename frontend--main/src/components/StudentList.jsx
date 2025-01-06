import React, { useState, useEffect } from 'react';
import axios from 'axios';

const StudentList = ({ role, onSelectStudent }) => {
  const [students, setStudents] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        let url = 'https://backend1-nbbb.onrender.com/students'; // Default for Admin & Bursar

        if (role === 'teacher') {
          const staffId = localStorage.getItem('staffId'); // Assuming staffId is stored after login
          url = `https://backend1-nbbb.onrender.com/staff/${staffId}/students`;
        }

        const response = await axios.get(url);
        setStudents(response.data);
      } catch (err) {
        console.error(err);
        setError('Failed to fetch students. Please try again.');
      }
    };
    fetchStudents();
  }, [role]);

  return (
    <div>
      <h3>Student List</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <ul>
        {students.map((student) => (
          <li key={student.id} onClick={() => onSelectStudent(student)}>
            {student.name} - Grade: {student.grade} - Balance: {student.balance}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StudentList;

