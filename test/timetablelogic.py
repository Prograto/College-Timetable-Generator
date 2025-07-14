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
        return 3 * 2 + 3 * 1

    def assign_lab_periods(self, lab_count):
        return lab_count * 6

    def distribute_subject_periods(self, theory_subjects, lab_count):
        fixed = self.assign_fixed_subjects()
        labs = self.assign_lab_periods(lab_count)
        remaining = self.total_periods - fixed - labs
        sorted_theory = sorted(theory_subjects, key=lambda s: s.priority)
        per_subject = remaining // len(theory_subjects)
        remainder = remaining % len(theory_subjects)
        return per_subject, remainder, sorted_theory

    def generate_for_class(self, subject_list):
        lab_subjects = [s for s in subject_list if s.type == 'lab']
        theory_subjects = [s for s in subject_list if s.type == 'theory']

        fixed_periods = self.assign_fixed_subjects()
        lab_periods = self.assign_lab_periods(len(lab_subjects))
        remaining_periods = self.total_periods - fixed_periods - lab_periods

        allocation = {}

        for lab in lab_subjects:
            allocation[lab.name] = 6

        for fs, p in self.fixed_subjects.items():
            allocation[fs] = p

        for subject in theory_subjects:
            if subject.priority == 1:
                allocation[subject.name] = 5
            else:
                allocation[subject.name] = 4

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

    for fs in TimeTableGenerator().fixed_subjects:
        teacher_names = [f"{fs}_T" for _ in range(num_sections)]
        teacher_map[fs] = teacher_names
        for name in teacher_names:
            teacher_pool.append(Teacher(name, fs, 1))

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
        self.allocations = {
            section: TimeTableGenerator().generate_for_class(subjects)
            for section in sections
        }
        self.daily_subject_counts = {s: [defaultdict(int) for _ in range(self.days)] for s in sections}
        self.weekly_subject_counts = {s: defaultdict(int) for s in sections}
        self.lab_last_day = {}

    def is_slot_free(self, section, day, period):
        return self.timetable[section][day][period] is None

    def spread_subject_days(self, total, max_per_day=2):
        slots = []
        for d in range(self.days):
            slots.extend([d] * max_per_day)
        random.shuffle(slots)
        return slots[:total]

    def place_fixed_subjects(self, section_index, section):
        double_period_subjects = {"Training", "Training Exam"}
        single_period_subjects = {"Counseling", "skills"}
        end_period_subjects = {"Sports", "Library"}
        used_days = set()

        for subj in double_period_subjects:
            teacher_name = self.teacher_map[subj][section_index]
            day_choices = [d for d in range(self.days) if d not in used_days]
            random.shuffle(day_choices)
            for day in day_choices:
                for period in range(self.periods_per_day - 1):
                    if self.is_slot_free(section, day, period) and self.is_slot_free(section, day, period + 1):
                        self.timetable[section][day][period] = f"{subj} ({teacher_name})"
                        self.timetable[section][day][period + 1] = f"{subj} ({teacher_name})"
                        self.teacher_slots[teacher_name][day][period] = True
                        self.teacher_slots[teacher_name][day][period + 1] = True
                        self.daily_subject_counts[section][day][subj] += 2
                        self.weekly_subject_counts[section][subj] += 2
                        used_days.add(day)
                        break
                else:
                    continue
                break

        for subj in end_period_subjects:
            teacher_name = self.teacher_map[subj][section_index]
            available_days = list(set(range(self.days)) - used_days)
            random.shuffle(available_days)
            for day in available_days:
                period = self.periods_per_day - (2 if subj == "Sports" else 1)
                span = 2 if subj == "Sports" else 1
                if all(self.is_slot_free(section, day, period + i) for i in range(span)):
                    for i in range(span):
                        self.timetable[section][day][period + i] = f"{subj} ({teacher_name})"
                        self.daily_subject_counts[section][day][subj] += 1
                        self.weekly_subject_counts[section][subj] += 1
                    used_days.add(day)
                    break

        for subj in single_period_subjects:
            teacher_name = self.teacher_map[subj][section_index]
            day_choices = [d for d in range(self.days) if d not in used_days]
            random.shuffle(day_choices)
            for day in day_choices:
                for period in range(self.periods_per_day):
                    if self.is_slot_free(section, day, period) and not self.teacher_slots[teacher_name][day][period]:
                        self.timetable[section][day][period] = f"{subj} ({teacher_name})"
                        self.teacher_slots[teacher_name][day][period] = True
                        self.daily_subject_counts[section][day][subj] += 1
                        self.weekly_subject_counts[section][subj] += 1
                        used_days.add(day)
                        break
                else:
                    continue
                break

    def place_subjects(self):
        for section_index, section in enumerate(self.sections):
            self.place_fixed_subjects(section_index, section)
            subject_slots = defaultdict(list)
            daily_lab_tracker = {d: 0 for d in range(self.days)}

            for subject in self.subjects:
                if subject.name in TimeTableGenerator().fixed_subjects:
                    continue
                periods = self.allocations[section][subject.name]
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
                        if self.place_lab(section, day, subject, teacher_name):
                            daily_lab_tracker[day] += 1
                    else:
                        self.place_theory(section, day, subject, teacher_name)

            for day in range(self.days):
                for period in range(self.periods_per_day):
                    if self.timetable[section][day][period] is None:
                        sorted_subjects = sorted(
                            [s for s in self.subjects if s.type == 'theory' and s.name not in TimeTableGenerator().fixed_subjects],
                            key=lambda s: s.priority
                        )
                        for subject in sorted_subjects:
                            if (self.daily_subject_counts[section][day][subject.name] < 2 and
                                self.weekly_subject_counts[section][subject.name] < self.allocations[section][subject.name]):
                                teacher_name = self.teacher_map[subject.name][section_index]
                                if not self.teacher_slots[teacher_name][day][period]:
                                    self.timetable[section][day][period] = f"{subject.name} ({teacher_name})"
                                    self.teacher_slots[teacher_name][day][period] = True
                                    self.daily_subject_counts[section][day][subject.name] += 1
                                    self.weekly_subject_counts[section][subject.name] += 1
                                    break

    def place_theory(self, section, day, subject, teacher_name):
        if (self.daily_subject_counts[section][day][subject.name] >= 2 or
            self.weekly_subject_counts[section][subject.name] >= self.allocations[section][subject.name]):
            return False
        for period in range(self.periods_per_day):
            if self.is_slot_free(section, day, period) and not self.teacher_slots[teacher_name][day][period]:
                self.timetable[section][day][period] = f"{subject.name} ({teacher_name})"
                self.teacher_slots[teacher_name][day][period] = True
                self.daily_subject_counts[section][day][subject.name] += 1
                self.weekly_subject_counts[section][subject.name] += 1
                return True
        return False

    def place_lab(self, section, day, subject, teacher_name):
        valid_starts = [0, 1, 4]
        key = (section, subject.name)
        if key in self.lab_last_day and abs(day - self.lab_last_day[key]) == 1:
            return False
        for period in valid_starts:
            if period + 2 >= self.periods_per_day:
                continue
            if all(self.is_slot_free(section, day, period + i) and not self.teacher_slots[teacher_name][day][period + i] for i in range(3)):
                for i in range(3):
                    self.timetable[section][day][period + i] = f"{subject.name} ({teacher_name})"
                    self.teacher_slots[teacher_name][day][period + i] = True
                self.lab_last_day[key] = day
                self.weekly_subject_counts[section][subject.name] += 3
                return True
        return False

    def generate(self):
        self.place_subjects()
        return self.timetable

if __name__ == "__main__":
    sections = [f"CSE-{chr(65+i)}" for i in range(6)]
    subjects = [
        Subject("DSA", 1),
        Subject("NLP", 1),
        Subject("ML", 1),
        Subject("UHV", 2),
        Subject("PLC", 2),
        Subject("IGPS", 2),
        Subject("AI Lab", 1, 'lab'),
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
