import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AddStudent = () => {
    const [name, setName] = useState('');
    const [admissionNumber, setAdmissionNumber] = useState('');
    const [grade, setGrade] = useState('');
    const [useBus, setUseBus] = useState(false);
    const [isBoarding, setIsBoarding] = useState(false);
    const [boardingFee, setBoardingFee] = useState(0);
    const [grades, setGrades] = useState([]);
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Fetch grades from your API or hardcode them
        const fetchGrades = async () => {
            const response = await axios.get('/api/grades'); // Adjust the endpoint as needed
            setGrades(response.data);
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
            boarding_fee: boardingFee
        };

        try {
            const response = await axios.post('/api/students', studentData);
            setMessage(response.data.message);
            // Reset form
            setName('');
            setAdmissionNumber('');
            setGrade('');
            setUseBus(false);
            setBoardingFee(0);
        } catch (error) {
            console.error('Error adding student:', error);
            setMessage('Error adding student. Please try again.');
        }
    };

    const handleGradeChange = (e) => {
        const selectedGrade = e.target.value;
        setGrade(selectedGrade);

        // Check if the selected grade is for boarding
        if (['5', '6', '7', '8', '9', '10'].includes(selectedGrade)) { // Adjust according to your boarding grades
            setIsBoarding(true);
            setBoardingFee(3500); // Set the boarding fee for grades above 5
        } else {
            setIsBoarding(false);
            setBoardingFee(0); // Reset boarding fee for grades below 5
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
                    <select value={grade} onChange={handleGradeChange} required>
                        <option value="" disabled>Select grade</option>
                        {grades.map((g) => (
                            <option key={g.id} value={g.grade}>
                                {g.grade}
                            </option>
                        ))}
                    </select>
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
                {!isBoarding && (
                    <div>
                        <label>Boarding Fee:</label>
                        <input
                            type="number"
                            value={boardingFee}
                            onChange={(e) => setBoardingFee(e.target.value)}
                            disabled={isBoarding}
                        />
                    </div>
                )}
                <button type="submit">Add Student</button>
            </form>
        </div>
    );
};

export default AddStudent;
