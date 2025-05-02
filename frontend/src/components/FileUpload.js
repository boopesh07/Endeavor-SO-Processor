import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button, Alert, Spinner } from 'react-bootstrap';
import { extractFromPDF } from '../services/api';

const FileUpload = ({ onExtracted }) => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            const selectedFile = acceptedFiles[0];
            // Check if the file is a PDF
            if (selectedFile.type === 'application/pdf') {
                setFile(selectedFile);
                setError(null);
            } else {
                setError('Please upload a PDF file');
            }
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf']
        },
        maxFiles: 1
    });

    const handleExtract = async () => {
        if (!file) {
            setError('Please upload a file first');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // Call the extraction API
            const extractedData = await extractFromPDF(file);
            onExtracted(file.name, extractedData);
        } catch (err) {
            console.error('Extraction error:', err);
            setError(err.response?.data?.detail || 'Failed to extract data from the PDF');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mb-4">
            <div
                {...getRootProps()}
                className={`drop-area p-4 mb-3 text-center border ${isDragActive ? 'border-primary' : 'border-secondary'
                    } rounded`}
            >
                <input {...getInputProps()} />
                <p className="mb-0">
                    {isDragActive
                        ? 'Drop the PDF file here...'
                        : 'Drag & drop a PDF file here, or click to select one'}
                </p>
                {file && (
                    <p className="mt-2 text-success">
                        Selected file: {file.name} ({Math.round(file.size / 1024)} KB)
                    </p>
                )}
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            <div className="d-grid">
                <Button
                    variant="primary"
                    onClick={handleExtract}
                    disabled={!file || loading}
                >
                    {loading ? (
                        <>
                            <Spinner animation="border" size="sm" className="me-2" />
                            Extracting...
                        </>
                    ) : (
                        'Extract Data'
                    )}
                </Button>
            </div>
        </div>
    );
};

export default FileUpload; 