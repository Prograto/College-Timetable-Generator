import random
from collections import defaultdict

class Subject:
    def __init__(self, name, priority, sub_type='theory'):
        self.name = name
        self.priority = priority
        self.type = sub_type

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
            "Training Exam": 2,
            "Sports": 2,
            "Counseling": 1,
            "Library": 1,
            "skills": 1
        }

    def assign_fixed_subjects(self):
        return sum(self.fixed_subjects.values())

    def assign_lab_periods(self, lab_count):
        return lab_count * 6  # 2 sessions × 3 periods

    def distribute_subject_periods(self, theory_subjects, lab_count):
        fixed = self.assign_fixed_subjects()
        labs = self.assign_lab_periods(lab_count)
        remaining = self.total_periods - fixed - labs
        per_subject = remaining // len(theory_subjects)
        remainder = remaining % len(theory_subjects)
        return per_subject, remainder

    def generate_for_class(self, subject_list):
        lab_subjects = [s for s in subject_list if s.type == 'lab']
        theory_subjects = [s for s in subject_list if s.type == 'theory']
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

    # Also add dummy teacher for fixed subjects
    for fs in TimeTableGenerator().fixed_subjects:
        teacher_map[fs] = [f"{fs}_T" for _ in range(num_sections)]

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
        self.teacher_slots = {t.name: [[False]*self.periods_per_day for _ in range(self.days)] for t in teacher_pool}
        self.allocation = TimeTableGenerator().generate_for_class(subjects)

    def is_slot_free(self, section, day, period):
        return self.timetable[section][day][period] is None

    def spread_subject_days(self, total, max_per_day=2):
        slots = []
        for d in range(self.days):
            slots.extend([d] * max_per_day)
        random.shuffle(slots)
        return slots[:total]

    def place_fixed_subjects(self, section_index, section):
        fixed_subjects = [s for s in self.allocation if s in TimeTableGenerator().fixed_subjects]
        fixed_plan = []

        for subj in fixed_subjects:
            session_count = self.allocation[subj] // 2
            days_plan = self.spread_subject_days(session_count, max_per_day=1)
            for d in days_plan:
                fixed_plan.append((d, subj))

        for day, subj in fixed_plan:
            teacher_name = self.teacher_map[subj][section_index]
            for period in range(self.periods_per_day - 1):  # need 2 slots
                if (self.is_slot_free(section, day, period) and
                    self.is_slot_free(section, day, period + 1)):
                    self.timetable[section][day][period] = f"{subj} ({teacher_name})"
                    self.timetable[section][day][period + 1] = f"{subj} ({teacher_name})"
                    break


    def place_subjects(self):
        for section_index, section in enumerate(self.sections):
            self.place_fixed_subjects(section_index, section)
            subject_slots = defaultdict(list)
            daily_lab_tracker = {d: 0 for d in range(self.days)}

            for subject in self.subjects:
                if subject.name in TimeTableGenerator().fixed_subjects:
                    continue
                periods = self.allocation[subject.name]
                days_plan = self.spread_subject_days(periods)
                for d in days_plan:
                    subject_slots[d].append(subject)

            for day in range(self.days):
                random.shuffle(subject_slots[day])
                for subject in subject_slots[day]:
                    teacher_name = self.teacher_map[subject.name][section_index]
                    if subject.type == 'lab':
                        if daily_lab_tracker[day] >= 1:
                            continue
                        placed = self.place_lab(section, day, subject, teacher_name)
                        if placed:
                            daily_lab_tracker[day] += 1
                    else:
                        self.place_theory(section, day, subject, teacher_name)

            # Fill remaining empty slots with any available theory subject
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    if self.timetable[section][day][period] is None:
                        for subject in self.subjects:
                            if subject.type == 'theory' and subject.name not in TimeTableGenerator().fixed_subjects:
                                teacher_name = self.teacher_map[subject.name][section_index]
                                if not self.teacher_slots[teacher_name][day][period]:
                                    self.timetable[section][day][period] = f"{subject.name} ({teacher_name})"
                                    self.teacher_slots[teacher_name][day][period] = True
                                    break

    def place_theory(self, section, day, subject, teacher_name):
        # Ensure no more than 2 of same subject per day in a section
        subject_count_today = sum(
            subject.name in (self.timetable[section][day][p] or '') for p in range(self.periods_per_day)
        )
        if subject_count_today >= 2:
            return False

        for period in range(self.periods_per_day):
            if self.is_slot_free(section, day, period) and not self.teacher_slots[teacher_name][day][period]:
                prev = period > 0 and teacher_name in str(self.timetable[section][day][period - 1])
                next = period < self.periods_per_day - 1 and teacher_name in str(self.timetable[section][day][period + 1])
                if prev and next:
                    continue
                self.timetable[section][day][period] = f"{subject.name} ({teacher_name})"
                self.teacher_slots[teacher_name][day][period] = True
                return True
        return False


    def place_lab(self, section, day, subject, teacher_name):
        valid_starts = [0, 1, 4]  # allowed start periods (0-based indexing)

        for period in valid_starts:
            if period + 2 >= self.periods_per_day:
                continue
            if all(self.is_slot_free(section, day, period + i) and not self.teacher_slots[teacher_name][day][period + i] for i in range(3)):
                for i in range(3):
                    self.timetable[section][day][period + i] = f"{subject.name} ({teacher_name})"
                    self.teacher_slots[teacher_name][day][period + i] = True
                return True
        return False


    def generate(self):
        self.place_subjects()
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
                print(f"  Period {period_idx + 1}: {period}")
