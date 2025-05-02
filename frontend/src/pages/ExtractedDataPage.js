import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert, Spinner, ButtonGroup } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import LineItemTable from '../components/LineItemTable';
import { createSalesOrder, matchBatchItems } from '../services/api';

const ExtractedDataPage = ({ fileName, extractedData, onReset }) => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [matchingLoading, setMatchingLoading] = useState(false);
    const [editableData, setEditableData] = useState(extractedData);
    const [matchingComplete, setMatchingComplete] = useState(false);

    // Check if all items have matched products
    useEffect(() => {
        if (editableData && editableData.length > 0) {
            const allMatched = editableData.every(item => item.matched_item);
            setMatchingComplete(allMatched);
        } else {
            setMatchingComplete(false);
        }
    }, [editableData]);

    const handleItemUpdate = (index, updates) => {
        const updatedItems = [...editableData];
        updatedItems[index] = { ...updatedItems[index], ...updates };
        setEditableData(updatedItems);
    };

    const handleBulkMatch = async () => {
        setMatchingLoading(true);
        setError(null);

        try {
            // Extract all request items for batch matching
            const queries = editableData.map(item => item['Request Item']);

            // Call the batch matching API
            const matchResults = await matchBatchItems(queries);

            // Update each item with its match result
            const updatedItems = editableData.map((item, index) => {
                const requestItem = item['Request Item'];
                const matches = matchResults[requestItem] || [];

                if (matches.length > 0) {
                    // Use the best match (first one) as the default
                    const bestMatch = matches[0];
                    return {
                        ...item,
                        matched_item: bestMatch.match,
                        match_score: bestMatch.score,
                        alternate_matches: matches.slice(1)
                    };
                }
                return item;
            });

            setEditableData(updatedItems);
        } catch (err) {
            console.error('Error matching items:', err);
            setError('Failed to match items. Please try again.');
        } finally {
            setMatchingLoading(false);
        }
    };

    const handleSave = async () => {
        setLoading(true);
        setError(null);

        try {
            const result = await createSalesOrder(fileName, editableData);
            if (result.success) {
                navigate(`/sales-order/${result.sales_order_id}`);
            } else {
                setError('Failed to save the sales order');
            }
        } catch (err) {
            console.error('Error saving sales order:', err);
            setError(err.response?.data?.detail || 'Failed to save the sales order');
        } finally {
            setLoading(false);
        }
    };

    if (!extractedData || extractedData.length === 0) {
        return (
            <Container className="py-4">
                <Alert variant="warning">
                    No data was extracted. Please try uploading another file.
                </Alert>
                <Button variant="primary" onClick={onReset}>
                    Go Back
                </Button>
            </Container>
        );
    }

    return (
        <Container className="py-4">
            <Row className="mb-4">
                <Col>
                    <div className="d-flex justify-content-between align-items-center">
                        <h1>Extracted Data</h1>
                        <Button variant="outline-secondary" onClick={onReset}>
                            Cancel
                        </Button>
                    </div>
                    <p className="lead">Review and edit the extracted line items before saving.</p>
                </Col>
            </Row>

            <Card className="mb-4">
                <Card.Header as="h5">
                    <div className="d-flex justify-content-between align-items-center">
                        <span>File: {fileName}</span>
                        <span>{editableData.length} items extracted</span>
                    </div>
                </Card.Header>
                <Card.Body>
                    <div className="mb-4">
                        <Button
                            variant="success"
                            onClick={handleBulkMatch}
                            disabled={matchingLoading}
                            className="mb-3"
                        >
                            {matchingLoading ? (
                                <>
                                    <Spinner animation="border" size="sm" className="me-2" />
                                    Matching Items...
                                </>
                            ) : (
                                'Bulk Match All Items'
                            )}
                        </Button>
                        <p className="text-muted small mt-1">
                            Click to automatically match all items with products from the catalog.
                        </p>
                    </div>

                    <LineItemTable
                        items={editableData}
                        onItemUpdate={handleItemUpdate}
                        isMatchingAvailable={true}
                    />

                    {error && <Alert variant="danger" className="mt-3">{error}</Alert>}

                    <div className="d-flex justify-content-between align-items-center mt-4">
                        <div>
                            {!matchingComplete && (
                                <Alert variant="warning" className="mb-0 py-2">
                                    Please match all items before saving. Use the "Bulk Match All Items" button.
                                </Alert>
                            )}
                        </div>
                        <Button
                            variant="primary"
                            size="lg"
                            onClick={handleSave}
                            disabled={loading || !matchingComplete}
                        >
                            {loading ? (
                                <>
                                    <Spinner animation="border" size="sm" className="me-2" />
                                    Saving...
                                </>
                            ) : (
                                'Save and Continue'
                            )}
                        </Button>
                    </div>
                </Card.Body>
            </Card>
        </Container>
    );
};

export default ExtractedDataPage; 