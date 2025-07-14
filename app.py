from flask import Flask, render_template, request, send_file
import io
import xlsxwriter
from enhancing import Subject, assign_teachers, TimetableBuilder

app = Flask(__name__)

latest_timetable = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    class_name = request.form['class_name']
    num_sections = int(request.form['num_sections'])

    subject_names = request.form.getlist('subject_name[]')
    subject_priorities = request.form.getlist('subject_priority[]')
    subject_types = request.form.getlist('subject_type[]')

    fixed_names = request.form.getlist('fixed_name[]')
    fixed_periods = request.form.getlist('fixed_periods[]')

    # Prepare subject list
    subjects = [
        Subject(name.strip(), int(priority), s_type.strip())
        for name, priority, s_type in zip(subject_names, subject_priorities, subject_types)
        if name.strip()
    ]

    # Prepare fixed subject dictionary
    fixed_subjects = {
        name.strip(): int(periods)
        for name, periods in zip(fixed_names, fixed_periods)
        if name.strip() and periods.isdigit()
    }

    sections = [f"{class_name}-{chr(65 + i)}" for i in range(num_sections)]
    
    teacher_map, teacher_pool = assign_teachers(subjects, num_sections, fixed_subjects)
    builder = TimetableBuilder(sections, subjects, teacher_map, teacher_pool, fixed_subjects)
    timetable = builder.generate()

    global latest_timetable
    latest_timetable = timetable

    return render_template('result.html', timetable=timetable)


@app.route('/download', methods=['GET'])
def download():
    global latest_timetable

    if not latest_timetable:
        return "No timetable available. Please generate one first."

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    for sec, days in latest_timetable.items():
        worksheet = workbook.add_worksheet(sec)
        worksheet.write(0, 0, "Day/Period")
        for i in range(7):
            worksheet.write(0, i + 1, f"Period {i+1}")
        for day_index, periods in enumerate(days):
            worksheet.write(day_index + 1, 0, f"Day {day_index + 1}")
            for p_index, period in enumerate(periods):
                worksheet.write(day_index + 1, p_index + 1, period if period else "")

    workbook.close()
    output.seek(0)
    return send_file(output, download_name='timetable.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
