const { db } = require('../config/database');

async function create(userId, courseId) {
    return new Promise((resolve, reject) => {
        db.run(
            "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
            [userId, courseId],
            function (err) { err ? reject(err) : resolve({ id: this.lastID }); }
        );
    });
}

async function getFinancialReport() {
    const rows = await db.allAsync(`
        SELECT
            c.id AS course_id,
            c.title,
            u.name AS student_name,
            p.amount,
            p.status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.enrollment_id = e.id
        ORDER BY c.id
    `, []);
    return rows;
}

module.exports = { create, getFinancialReport };
