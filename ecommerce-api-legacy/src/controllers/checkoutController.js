const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditModel = require('../models/auditModel');
const { hashPassword } = require('../config/crypto');
const { paymentGatewayKey } = require('../config/settings');

function processPayment(cardNumber) {
    // In production this would call a real payment gateway
    const status = cardNumber.startsWith('4') ? 'PAID' : 'DENIED';
    return status;
}

async function checkout(name, email, password, courseId, cardNumber) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) {
        return { error: 'Curso não encontrado' };
    }

    let user = await userModel.findByEmail(email);
    if (!user) {
        const passHash = hashPassword(password || '123456');
        const created = await userModel.create(name, email, passHash);
        user = { id: created.id };
    }

    const paymentStatus = processPayment(cardNumber);
    if (paymentStatus === 'DENIED') {
        return { error: 'Pagamento recusado' };
    }

    const enrollment = await enrollmentModel.create(user.id, course.id);
    await paymentModel.create(enrollment.id, course.price, paymentStatus);
    await auditModel.log(`Checkout curso ${course.id} por usuário ${user.id}`);

    return { msg: 'Sucesso', enrollment_id: enrollment.id };
}

module.exports = { checkout };
