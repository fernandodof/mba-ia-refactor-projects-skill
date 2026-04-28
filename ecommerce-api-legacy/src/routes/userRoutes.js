const express = require('express');
const userController = require('../controllers/userController');

const router = express.Router();

router.delete('/users/:id', async (req, res, next) => {
    try {
        const result = await userController.deleteUser(req.params.id);
        if (result.error) {
            return res.status(404).json(result);
        }
        res.json(result);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
