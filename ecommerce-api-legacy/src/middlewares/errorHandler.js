function errorHandler(err, req, res, next) {
    console.error('[ERROR]', err.message);
    res.status(500).json({ error: 'Erro interno do servidor' });
}

module.exports = errorHandler;
