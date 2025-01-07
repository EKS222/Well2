import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AddStudent = ({ onClose }) => {
    const [name, setName] = useState('');
    const [admissionNumber, setAdmissionNumber] = useState('');
    const [grade, setGrade] = useState('');
    const [balance, setBalance] = useState(0.0);
    const [arrears, setArrears] = useState(0.0);
    const [termFee, setTermFee] = useState(0.0);
    const [useBus, setUseBus] = useState(false);
    const [busBalance, setBusBalance] = useState(0.0);
    const [password, setPassword] = useState('');
    const [grades, setGrades] = useState([]);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const fetchGrades = async () => {
            try {
                const response = await axios.get('/api/grades');
                setGrades(response.data);
            } catch (error) {
                console.error('Error fetching grades:', error);
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
            balance,
            arrears,
            term_fee: termFee,
            use_bus: useBus,
            bus_balance: busBalance,
            password,
        };

        try {
            await axios.post('/api/students', studentData);
            setMessage('Student added successfully!');
            // Reset form
            setName('');
            setAdmissionNumber('');
            setGrade('');
            setBalance(0.0);
            setArrears(0.0);
            setTermFee(0.0);
            setUseBus(false);
            setBusBalance(0.0);
            setPassword('');
            onClose(); // Close modal after successful submission
        } catch (error) {
            console.error('Error adding student:', error);
            setMessage('Failed to add student. Please try again.');
        }
    };

    return (
        <div>
            <h2>Add Student</h2>
            {message && <p>{message}</p>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Name:</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Admission Number:</label>
                    <input
                        type="text"
                        value={admissionNumber}
                        onChange={(e) => setAdmissionNumber(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Grade:</label>
                    <select value={grade} onChange={(e) => setGrade(e.target.value)} required>
                        <option value="" disabled>Select grade</option>
                        {grades.map((g) => (
                            <option key={g.id} value={g.grade}>
                                {g.grade}
                            </option>
                        ))}
                    </select>
                </div>
                <div>
                    <label>Balance:</label>
                    <input
                        type="number"
                        value={balance}
                        onChange={(e) => setBalance(parseFloat(e.target.value))}
                        required
                    />
                </div>
                <div>
                    <label>Arrears:</label>
                    <input
                        type="number"
                        value={arrears}
                        onChange={(e) => setArrears(parseFloat(e.target.value))}
                    />
                </div>
                <div>
                    <label>Term Fee:</label>
                    <input
                        type="number"
                        value={termFee}
                        onChange={(e) => setTermFee(parseFloat(e.target.value))}
                        required
                    />
                </div>
                <div>
                    <label>
                        <input
                            type="checkbox"
                            checked={useBus}
                            onChange={() => setUseBus(!useBus)}
                        />
                        Will use bus
                    </label>
                </div>
                <div>
                    <label>Bus Balance:</label>
                    <input
                        type="number"
                        value={busBalance}
                        onChange={(e) => setBusBalance(parseFloat(e.target.value))}
                    />
                </div>
                <div>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Add Student</button>
            </form>
        </div>
    );
};

export default AddStudent;

