# ================================
#       TIMETABLE MAKER
# ================================

class Subject:
    def __init__(self, name, priority, sub_type='theory'):
        self.name = name
        self.priority = priority  # 1 = important, 2 = low
        self.type = sub_type      # 'theory' or 'lab'


class Teacher:
    def __init__(self, name, subject, max_sections):
        self.name = name
        self.subject = subject
        self.max_sections = max_sections
        self.assigned_sections = []


class TimeTableGenerator:
    def __init__(self, periods_per_day=7, days_per_week=6):
        self.days = days_per_week
        self.periods_per_day = periods_per_day
        self.total_periods = self.days * self.periods_per_day
        self.fixed_subjects = {
            "Training": 2,
            "Sports": 2,
            "Counseling": 1,
            "Library": 1
        }

    def assign_fixed_subjects(self):
        return sum(self.fixed_subjects.values())

    def assign_lab_periods(self, lab_count):
        return lab_count * 6

    def distribute_subject_periods(self, theory_subjects, lab_count):
        fixed = self.assign_fixed_subjects()
        labs = self.assign_lab_periods(lab_count)
        remaining = self.total_periods - fixed - labs
        per_subject = remaining // len(theory_subjects)
        remainder = remaining % len(theory_subjects)
        return per_subject, remainder

    def generate_for_class(self, subject_list):
        lab_subjects = [sub for sub in subject_list if sub.type == 'lab']
        theory_subjects = [sub for sub in subject_list if sub.type == 'theory']
        per_subject, remainder = self.distribute_subject_periods(theory_subjects, len(lab_subjects))

        allocation = {}
        for sub in lab_subjects:
            allocation[sub.name] = 6

        for sub in theory_subjects:
            allocation[sub.name] = per_subject + (1 if remainder > 0 and sub.priority == 1 else 0)
            if remainder > 0 and sub.priority == 1:
                remainder -= 1

        allocation.update(self.fixed_subjects)
        return allocation


def assign_teachers(subjects, num_sections):
    teacher_map = {}
    teacher_pool = []
    teacher_id = 1

    for sub in subjects:
        max_sections = 3 if sub.priority == 1 or sub.type == 'lab' else 4
        num_teachers_needed = (num_sections + max_sections - 1) // max_sections
        assigned_teachers = []

        for _ in range(num_teachers_needed):
            teacher_name = f"Teacher{teacher_id}"
            teacher_id += 1
            t = Teacher(teacher_name, sub.name, max_sections)
            teacher_pool.append(t)
            assigned_teachers.append(t.name)

        section_teachers = []
        section_index = 0
        for t_name in assigned_teachers:
            for _ in range(max_sections):
                if section_index >= num_sections:
                    break
                section_teachers.append(t_name)
                section_index += 1

        teacher_map[sub.name] = section_teachers

    return teacher_map, teacher_pool


class TimetableBuilder:
    def __init__(self, sections, subjects, teacher_map, teacher_pool):
        self.sections = sections
        self.subjects = subjects
        self.teacher_map = teacher_map
        self.teacher_pool = teacher_pool
        self.days = 6
        self.periods_per_day = 7
        self.timetable = {s: [[None for _ in range(self.periods_per_day)] for _ in range(self.days)] for s in sections}
        self.teacher_slots = {t.name: [[False for _ in range(self.periods_per_day)] for _ in range(self.days)] for t in teacher_pool}
        self.allocation = TimeTableGenerator().generate_for_class(subjects)

    def place_subject(self, section, subject, teacher_name):
        periods_needed = self.allocation[subject.name]
        placed = 0

        for day in range(self.days):
            for period in range(self.periods_per_day - (2 if subject.type == 'lab' else 0)):
                if placed >= periods_needed:
                    return

                if subject.type == 'lab':
                    if period + 2 >= self.periods_per_day:
                        continue
                    if all(self.timetable[section][day][period + i] is None and not self.teacher_slots[teacher_name][day][period + i] for i in range(3)):
                        for i in range(3):
                            self.timetable[section][day][period + i] = f"{subject.name} ({teacher_name})"
                            self.teacher_slots[teacher_name][day][period + i] = True
                        placed += 3
                else:
                    if self.timetable[section][day][period] is None and not self.teacher_slots[teacher_name][day][period]:
                        prev = period - 1 >= 0 and self.timetable[section][day][period - 1] and teacher_name in self.timetable[section][day][period - 1]
                        next = period + 1 < self.periods_per_day and self.timetable[section][day][period + 1] and teacher_name in self.timetable[section][day][period + 1]
                        if prev and next:
                            continue
                        self.timetable[section][day][period] = f"{subject.name} ({teacher_name})"
                        self.teacher_slots[teacher_name][day][period] = True
                        placed += 1

    def generate(self):
        for section_index, section in enumerate(self.sections):
            for subject in self.subjects:
                teacher = self.teacher_map[subject.name][section_index]
                self.place_subject(section, subject, teacher)
        return self.timetable


# ========== RUNNING EXAMPLE ==========
if __name__ == "__main__":
    sections = [f"CSE-{chr(65+i)}" for i in range(6)]

    subjects = [
        Subject("DSA", 1),
        Subject("NLP", 1),
        Subject("ML", 1),
        Subject("CN", 2),
        Subject("UHV", 2),
        Subject("PLC", 2),
        Subject("IGPS", 2),
        Subject("AI Lab", 1, 'lab'),
        Subject("ML Lab", 2, 'lab')
    ]

    teacher_map, teacher_pool = assign_teachers(subjects, len(sections))
    builder = TimetableBuilder(sections, subjects, teacher_map, teacher_pool)
    timetable = builder.generate()

    for sec in sections:
        print(f"\nTimetable for {sec}")
        for day_idx, day in enumerate(timetable[sec]):
            print(f"Day {day_idx + 1}:")
            for period_idx, period in enumerate(day):
                print(f"  Period {period_idx + 1}: {period or 'Free'}")
