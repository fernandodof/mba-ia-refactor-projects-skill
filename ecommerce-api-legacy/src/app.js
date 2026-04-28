const express = require('express');
const { initDb } = require('./config/database');
const { port } = require('./config/settings');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

app.use('/api', checkoutRoutes);
app.use('/api', reportRoutes);
app.use('/api', userRoutes);

app.use(errorHandler);

initDb().then(() => {
    app.listen(port, () => {
        console.log(`Frankenstein LMS rodando na porta ${port}...`);
    });
}).catch(err => {
    console.error('Falha ao inicializar o banco:', err);
    process.exit(1);
});
