import React from 'react';

const StudentDetails = ({ student, showAddPayment, onAddPayment }) => {
  if (!student) return <p>Select a student to view details.</p>;

  return (
    <div>
      <h3>Details for {student.name}</h3>
      <p><strong>Grade:</strong> {student.grade}</p>
      <p><strong>Admission Number:</strong> {student.admission_number}</p>
      <p><strong>Balance:</strong> {student.balance}</p>
      <p><strong>Arrears:</strong> {student.arrears}</p>
      <p><strong>Term Fee:</strong> {student.term_fee}</p>
      <p><strong>Uses Bus Service:</strong> {student.use_bus ? 'Yes' : 'No'}</p>
      <p><strong>Bus Balance:</strong> {student.bus_balance}</p>

      {showAddPayment && (
        <button onClick={onAddPayment}>Add Payment</button>
      )}
    </div>
  );
};

export default StudentDetails;

