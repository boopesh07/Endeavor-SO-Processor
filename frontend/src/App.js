import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

import HomePage from './pages/HomePage';
import ExtractedDataPage from './pages/ExtractedDataPage';
import SalesOrderDetailPage from './pages/SalesOrderDetailPage';

function App() {
    const [extractionState, setExtractionState] = useState({
        fileName: null,
        extractedData: null,
    });

    const handleExtracted = (fileName, extractedData) => {
        setExtractionState({
            fileName,
            extractedData,
        });
        // We'll redirect to the extracted data page in the HomePage component
    };

    const handleReset = () => {
        setExtractionState({
            fileName: null,
            extractedData: null,
        });
    };

    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route
                        path="/"
                        element={
                            extractionState.extractedData ? (
                                <Navigate to="/extracted-data" />
                            ) : (
                                <HomePage onExtracted={handleExtracted} />
                            )
                        }
                    />
                    <Route
                        path="/extracted-data"
                        element={
                            extractionState.extractedData ? (
                                <ExtractedDataPage
                                    fileName={extractionState.fileName}
                                    extractedData={extractionState.extractedData}
                                    onReset={handleReset}
                                />
                            ) : (
                                <Navigate to="/" />
                            )
                        }
                    />
                    <Route path="/sales-order/:id" element={<SalesOrderDetailPage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App; 