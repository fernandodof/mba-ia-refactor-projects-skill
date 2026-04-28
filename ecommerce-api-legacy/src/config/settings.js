require('dotenv').config();

module.exports = {
    port: process.env.PORT || 3000,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    smtpUser: process.env.SMTP_USER,
    dbPass: process.env.DB_PASS,
    debug: process.env.NODE_ENV !== 'production',
};
