import React, { useState } from 'react';
import StudentList from './StudentList';
import StudentDetails from './StudentDetails';
import '../styles/dashboard.css';

const AdminDashboard = () => {
  const [selectedStudent, setSelectedStudent] = useState(null);

  return (
    <div className="dashboard-container">
      <div className="dashboard-section">
        <h2>Admin Dashboard</h2>
        <button>Add New Student</button>
        <StudentList role="admin" onSelectStudent={setSelectedStudent} />
      </div>
      <div className="dashboard-section">
        <StudentDetails student={selectedStudent} showAddPayment={false} />
      </div>
    </div>
  );
};

export default AdminDashboard;