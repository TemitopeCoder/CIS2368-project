const express = require('express');
const path = require('path');
const axios = require('axios');

const app = express();
const backendUrl = "http://localhost:7000";

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.get('/', (req, res) => {
    res.render('home', { title: 'Library Home' });
});

app.get('/books', async (req, res) => {
    try {
        const response = await axios.get(`${backendUrl}/api/books/inventory`);
        const books = Array.isArray(response?.data) ? response.data : [];
        res.render('books', { 
            books,
            title: 'Book Management'
        });
    } catch (error) {
        console.error('Books Error:', error.message);
        res.render('books', { 
            books: [],
            title: 'Book Management'
        });
    }
});

app.get('/customers', async (req, res) => {
    try {
        const response = await axios.get(`${backendUrl}/api/customer/all`);
        const customers = Array.isArray(response?.data) ? response.data : [];
        res.render('customers', { 
            customers,
            title: 'Customer Management' 
        });
    } catch (error) {
        console.error('Customers Error:', error.message);
        res.render('customers', { 
            customers: [],
            title: 'Customer Management'
        });
    }
});

app.get('/borrowings', async (req, res) => {
    try {
        const [borrowingsRes, booksRes, customersRes] = await Promise.all([
            axios.get(`${backendUrl}/api/borrowing/all`),
            axios.get(`${backendUrl}/api/books/inventory`),
            axios.get(`${backendUrl}/api/customer/all`)
        ]);

        const processData = () => {
            const borrowings = Array.isArray(borrowingsRes?.data) ? borrowingsRes.data : [];
            const allBooks = Array.isArray(booksRes?.data) ? booksRes.data : [];
            const allCustomers = Array.isArray(customersRes?.data) ? customersRes.data : [];

            return {
                borrowings: borrowings.filter(b => !b.returndate),
                availableBooks: allBooks.filter(b => b.status === 'Available'),
                eligibleCustomers: allCustomers.filter(c => 
                    !borrowings.some(b => !b.returndate && b.customerid === c.customerid)
                ),
                borrowingHistory: borrowings.filter(b => b.returndate)
            };
        };

        const { borrowings, availableBooks, eligibleCustomers, borrowingHistory } = processData();
        
        res.render('borrowings', {
            borrowings,
            availableBooks,
            eligibleCustomers,
            borrowingHistory,
            title: 'Borrowing Management'
        });
    } catch (error) {
        console.error('Borrowings Error:', error.message);
        res.render('borrowings', {
            borrowings: [],
            availableBooks: [],
            eligibleCustomers: [],
            borrowingHistory: [],
            title: 'Borrowing Management'
        });
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Frontend server running at http://localhost:${PORT}`);
});