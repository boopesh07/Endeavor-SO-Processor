import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, ListGroup, Button, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { getAllSalesOrders } from '../services/api';
import FileUpload from '../components/FileUpload';

const HomePage = ({ onExtracted }) => {
    const [salesOrders, setSalesOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchSalesOrders();
    }, []);

    const fetchSalesOrders = async () => {
        setLoading(true);
        try {
            const orders = await getAllSalesOrders();
            setSalesOrders(orders);
        } catch (err) {
            console.error('Error fetching sales orders:', err);
            setError('Failed to load sales orders');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString();
    };

    return (
        <Container className="py-4">
            <Row className="mb-4">
                <Col>
                    <h1>Sales Order Processor</h1>
                    <p className="lead">
                        Upload a sales order PDF to extract and match items with your product catalog.
                    </p>
                </Col>
            </Row>

            <Row>
                <Col md={6}>
                    <Card className="mb-4">
                        <Card.Header as="h5">Upload Sales Order</Card.Header>
                        <Card.Body>
                            <FileUpload onExtracted={onExtracted} />
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={6}>
                    <Card>
                        <Card.Header as="h5">
                            <div className="d-flex justify-content-between align-items-center">
                                Recent Sales Orders
                                <Button
                                    variant="outline-primary"
                                    size="sm"
                                    onClick={fetchSalesOrders}
                                >
                                    Refresh
                                </Button>
                            </div>
                        </Card.Header>
                        <Card.Body>
                            {loading ? (
                                <div className="text-center p-4">
                                    <Spinner animation="border" />
                                    <p className="mt-2">Loading sales orders...</p>
                                </div>
                            ) : error ? (
                                <div className="text-center text-danger p-3">
                                    <p>{error}</p>
                                    <Button variant="primary" onClick={fetchSalesOrders}>
                                        Try Again
                                    </Button>
                                </div>
                            ) : salesOrders.length === 0 ? (
                                <p className="text-center text-muted p-3">
                                    No sales orders found. Upload your first order to get started!
                                </p>
                            ) : (
                                <ListGroup variant="flush">
                                    {salesOrders.map((order) => (
                                        <ListGroup.Item key={order._id} className="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h6 className="mb-1">
                                                    {order.order_number || order.file_name}
                                                </h6>
                                                <small className="text-muted">
                                                    {order.line_items.length} items • Created: {formatDate(order.created_at)}
                                                </small>
                                            </div>
                                            <Link to={`/sales-order/${order._id}`}>
                                                <Button variant="primary" size="sm">
                                                    View
                                                </Button>
                                            </Link>
                                        </ListGroup.Item>
                                    )).slice(0, 5)}
                                    {salesOrders.length > 5 && (
                                        <ListGroup.Item className="text-center">
                                            <Link to="/sales-orders">View all sales orders</Link>
                                        </ListGroup.Item>
                                    )}
                                </ListGroup>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default HomePage; 