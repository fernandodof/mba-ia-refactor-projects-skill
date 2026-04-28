const express = require('express');
const checkoutController = require('../controllers/checkoutController');

const router = express.Router();

router.post('/checkout', async (req, res, next) => {
    try {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

        if (!name || !email || !courseId || !cardNumber) {
            return res.status(400).json({ error: 'Campos obrigatórios: usr, eml, c_id, card' });
        }

        const result = await checkoutController.checkout(name, email, password, courseId, cardNumber);

        if (result.error) {
            const status = result.error === 'Curso não encontrado' ? 404 : 400;
            return res.status(status).json(result);
        }

        res.status(200).json(result);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
