import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container,
    Row,
    Col,
    Card,
    Button,
    Alert,
    Spinner,
    Badge,
    ListGroup
} from 'react-bootstrap';
import LineItemTable from '../components/LineItemTable';
import {
    getSalesOrder,
    downloadSalesOrderCsv
} from '../services/api';

const SalesOrderDetailPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [salesOrder, setSalesOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [csvLoading, setCsvLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchSalesOrder();
    }, [id]);

    const fetchSalesOrder = async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await getSalesOrder(id);
            setSalesOrder(data);
        } catch (err) {
            console.error('Error fetching sales order:', err);
            setError(err.response?.data?.detail || 'Failed to load sales order');
        } finally {
            setLoading(false);
        }
    };

    const handleItemUpdate = (itemIndex, updates) => {
        if (!salesOrder) return;

        // Create a deep copy of the sales order
        const updatedOrder = {
            ...salesOrder,
            line_items: [...salesOrder.line_items]
        };

        // Update the specific line item
        updatedOrder.line_items[itemIndex] = {
            ...updatedOrder.line_items[itemIndex],
            ...updates
        };

        setSalesOrder(updatedOrder);
    };

    const handleDownloadCsv = async () => {
        if (csvLoading) return;

        setCsvLoading(true);
        try {
            await downloadSalesOrderCsv(id);
        } catch (err) {
            console.error('Error downloading CSV:', err);
            setError('Failed to download CSV. Please try again later.');
        } finally {
            setCsvLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    };

    const hasMatches = salesOrder?.line_items.some(item => item.matched_item);

    if (loading) {
        return (
            <Container className="py-5 text-center">
                <Spinner animation="border" />
                <p className="mt-3">Loading sales order...</p>
            </Container>
        );
    }

    if (error) {
        return (
            <Container className="py-5">
                <Alert variant="danger">{error}</Alert>
                <Button variant="primary" onClick={() => navigate('/')}>
                    Back to Home
                </Button>
            </Container>
        );
    }

    if (!salesOrder) {
        return (
            <Container className="py-5">
                <Alert variant="warning">Sales order not found.</Alert>
                <Button variant="primary" onClick={() => navigate('/')}>
                    Back to Home
                </Button>
            </Container>
        );
    }

    return (
        <Container className="py-4">
            <Row className="mb-4">
                <Col>
                    <div className="d-flex justify-content-between align-items-center mb-2">
                        <h1>Sales Order Details</h1>
                        <Button variant="outline-secondary" onClick={() => navigate('/')}>
                            Back to Home
                        </Button>
                    </div>
                    <p className="lead">Review and export the sales order items.</p>
                </Col>
            </Row>

            <Row className="mb-4">
                <Col md={8}>
                    <Card>
                        <Card.Header as="h5">
                            <div className="d-flex justify-content-between align-items-center">
                                <span>Order Information</span>
                                {salesOrder.order_number && <Badge bg="primary">{salesOrder.order_number}</Badge>}
                            </div>
                        </Card.Header>
                        <ListGroup variant="flush">
                            <ListGroup.Item>
                                <strong>File Name:</strong> {salesOrder.file_name}
                            </ListGroup.Item>
                            {salesOrder.customer_name && (
                                <ListGroup.Item>
                                    <strong>Customer:</strong> {salesOrder.customer_name}
                                </ListGroup.Item>
                            )}
                            {salesOrder.order_date && (
                                <ListGroup.Item>
                                    <strong>Order Date:</strong> {formatDate(salesOrder.order_date)}
                                </ListGroup.Item>
                            )}
                            <ListGroup.Item>
                                <strong>Created:</strong> {formatDate(salesOrder.created_at)}
                            </ListGroup.Item>
                            <ListGroup.Item>
                                <strong>Last Updated:</strong> {formatDate(salesOrder.updated_at)}
                            </ListGroup.Item>
                        </ListGroup>
                    </Card>
                </Col>
                <Col md={4}>
                    <Card>
                        <Card.Header as="h5">Actions</Card.Header>
                        <Card.Body>
                            <div className="d-grid gap-2">
                                <Button
                                    variant="success"
                                    onClick={handleDownloadCsv}
                                    disabled={csvLoading}
                                >
                                    {csvLoading ? (
                                        <>
                                            <Spinner animation="border" size="sm" className="me-2" />
                                            Downloading...
                                        </>
                                    ) : (
                                        'Download as CSV'
                                    )}
                                </Button>
                            </div>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <Card>
                <Card.Header as="h5">
                    <div className="d-flex justify-content-between align-items-center">
                        <span>Line Items</span>
                        <span>{salesOrder.line_items.length} items</span>
                    </div>
                </Card.Header>
                <Card.Body>
                    <LineItemTable
                        items={salesOrder.line_items}
                        salesOrderId={id}
                        onItemUpdate={handleItemUpdate}
                        readOnly={true}
                    />
                </Card.Body>
            </Card>
        </Container>
    );
};

export default SalesOrderDetailPage; 