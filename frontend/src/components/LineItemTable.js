import React, { useState } from 'react';
import { Table, Form, Button, InputGroup } from 'react-bootstrap';
import { getMatchesForItem } from '../services/api';

const LineItemTable = ({ items, salesOrderId, onItemUpdate, readOnly }) => {
    const [loadingItems, setLoadingItems] = useState({});
    const [matchOptions, setMatchOptions] = useState({});
    const [editingItem, setEditingItem] = useState(null);
    const [editingRequestItem, setEditingRequestItem] = useState(null);
    const [editedRequestText, setEditedRequestText] = useState('');

    const handleMatchChange = async (itemIndex, item) => {
        if (loadingItems[itemIndex]) return;

        setLoadingItems(prev => ({ ...prev, [itemIndex]: true }));

        try {
            const matches = await getMatchesForItem(salesOrderId, item['Request Item']);
            setMatchOptions(prev => ({ ...prev, [itemIndex]: matches }));
            setEditingItem(itemIndex);
        } catch (error) {
            console.error('Error fetching matches:', error);
        } finally {
            setLoadingItems(prev => ({ ...prev, [itemIndex]: false }));
        }
    };

    const handleSelectMatch = async (itemIndex, matchedItem, score) => {
        if (onItemUpdate) {
            onItemUpdate(itemIndex, {
                matched_item: matchedItem,
                match_score: score
            });
        }

        setEditingItem(null);
    };

    const handleEditRequestItem = (index, currentText) => {
        setEditingRequestItem(index);
        setEditedRequestText(currentText);
    };

    const handleSaveRequestItem = (index) => {
        if (editedRequestText.trim() !== '') {
            if (onItemUpdate) {
                onItemUpdate(index, {
                    'Request Item': editedRequestText
                });
            }
        }
        setEditingRequestItem(null);
    };

    const formatScore = (score) => {
        if (score === null || score === undefined) return '';
        return score.toFixed(1);
    };

    // Helper function to safely format currency values
    const formatCurrency = (value) => {
        if (value === null || value === undefined) return '-';
        try {
            return `$${parseFloat(value).toFixed(2)}`;
        } catch (error) {
            return value.toString();
        }
    };

    // Helper function to get quantity value (handles both Quantity, Amount, and Qty fields)
    const getQuantity = (item) => {
        // Check different possible field names
        if (item['Quantity'] !== undefined) return item['Quantity'];
        if (item['Qty'] !== undefined) return item['Qty'];
        if (item['Amount'] !== undefined) return item['Amount'];
        return '-';
    };

    // Helper function to get unit price (handles both Unit Price and Price fields)
    const getUnitPrice = (item) => {
        // Check different possible field names
        if (item['Unit Price'] !== undefined) return formatCurrency(item['Unit Price']);
        if (item['Price'] !== undefined) return formatCurrency(item['Price']);
        return '-';
    };

    return (
        <Table striped bordered hover responsive>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Request Item</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                    <th>Matched Product</th>
                </tr>
            </thead>
            <tbody>
                {items.map((item, index) => (
                    <tr key={index}>
                        <td>{index + 1}</td>
                        <td>
                            {editingRequestItem === index ? (
                                <InputGroup>
                                    <Form.Control
                                        type="text"
                                        value={editedRequestText}
                                        onChange={(e) => setEditedRequestText(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter') handleSaveRequestItem(index);
                                        }}
                                    />
                                    <Button
                                        variant="outline-success"
                                        onClick={() => handleSaveRequestItem(index)}
                                    >
                                        Save
                                    </Button>
                                </InputGroup>
                            ) : (
                                <div
                                    className="editable-field"
                                    onClick={() => !readOnly && handleEditRequestItem(index, item['Request Item'])}
                                    style={{ cursor: readOnly ? 'default' : 'pointer' }}
                                >
                                    {item['Request Item']}
                                    {!readOnly && <i className="ms-2 bi bi-pencil-fill small"></i>}
                                </div>
                            )}
                        </td>
                        <td>{getQuantity(item)}</td>
                        <td>{getUnitPrice(item)}</td>
                        <td>{item['Total'] !== null && item['Total'] !== undefined ? formatCurrency(item['Total']) : '-'}</td>
                        <td>
                            {editingItem === index ? (
                                <Form.Select
                                    onChange={(e) => {
                                        const selectedOption = matchOptions[index].find(
                                            option => option.match === e.target.value
                                        );
                                        handleSelectMatch(index, e.target.value, selectedOption?.score);
                                    }}
                                    value={item.matched_item || ''}
                                >
                                    <option value="">Select a match...</option>
                                    {matchOptions[index]?.map((option, i) => (
                                        <option key={i} value={option.match}>
                                            {option.match} (Score: {formatScore(option.score)})
                                        </option>
                                    ))}
                                </Form.Select>
                            ) : (
                                <div
                                    className="editable-field"
                                    onClick={() => !readOnly && handleMatchChange(index, item)}
                                    style={{ cursor: readOnly ? 'default' : 'pointer' }}
                                >
                                    {item.matched_item || 'Click to match product'}
                                    {!readOnly && !item.matched_item && <i className="ms-2 bi bi-search"></i>}
                                    {!readOnly && item.matched_item && <i className="ms-2 bi bi-pencil-fill small"></i>}
                                </div>
                            )}
                        </td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );
};

export default LineItemTable; 