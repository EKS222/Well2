import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StudentList from './StudentList';
import StudentDetails from './StudentDetails';
import '../styles/dashboard.css';

const AdminDashboard = () => {
  const [selectedStudent, setSelectedStudent] = useState(null);
  const navigate = useNavigate();

  return (
    <div className="dashboard-container">
      {/* Header Section */}
      <div className="dashboard-header">
        <h2>Admin Dashboard</h2>
        <button 
          className="add-student-btn" 
          onClick={() => navigate('/admin/add-student')}
        >
          Add New Student
        </button>
      </div>

      {/* Main Content Section */}
      <div className="dashboard-main">
        <div className="dashboard-section student-list">
          <h3>Student List</h3>
          <StudentList onSelectStudent={setSelectedStudent} />
        </div>

        <div className="dashboard-section student-details">
          <h3>Student Details</h3>
          {selectedStudent ? (
            <StudentDetails student={selectedStudent} showAddPayment={false} />
          ) : (
            <p>Select a student to view details</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

