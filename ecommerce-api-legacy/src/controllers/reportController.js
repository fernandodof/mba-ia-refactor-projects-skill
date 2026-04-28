const enrollmentModel = require('../models/enrollmentModel');

async function financialReport() {
    const rows = await enrollmentModel.getFinancialReport();

    const courseMap = {};
    for (const row of rows) {
        if (!courseMap[row.course_id]) {
            courseMap[row.course_id] = { course: row.title, revenue: 0, students: [] };
        }
        if (row.student_name) {
            courseMap[row.course_id].students.push({
                student: row.student_name,
                paid: row.amount || 0,
            });
            if (row.status === 'PAID') {
                courseMap[row.course_id].revenue += row.amount;
            }
        }
    }

    return Object.values(courseMap);
}

module.exports = { financialReport };
