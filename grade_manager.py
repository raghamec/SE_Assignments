
# Get Student details for number of students mentioned by user    
def get_student():
    students = {}

    try:
        n = int(input("Enter number of students: "))

        if n <= 0:
            raise ValueError("Number of students must be greater than zero.")

        for i in range(n):
            print(f"\nEnter details of Student {i + 1}")

            # Validate student name
            while True:
                name = input("Enter student name: ").strip()

                if not name:
                    print("Error: Name cannot be empty.")
                elif not name.replace(" ", "").isalpha():
                    print("Error: Name must contain only alphabets.")
                elif name in students:
                    print("Error: Student name already exists.")
                else:
                    break

            # Validate student marks
            while True:
                try:
                    mark = float(input("Enter student mark: "))

                    if mark < 0 or mark > 100:
                        print("Error: Marks must be between 0 and 100.")
                    else:
                        break

                except ValueError:
                    print("Error: Please enter a valid numeric mark.")

            students[name] = mark

        return students

    except ValueError as e:
        print("Input Error:", e)
        return {}






# Function to calculate grade
def calculate_grade(mark):
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "E"




# Main program
student_data = get_student()

for name, mark in student_data.items():
        grade = calculate_grade(mark)
        student_data[name] = {"Marks": mark, "Grade": grade}

#         print(f"Student Name : {name}")
#         print(f"Marks        : {mark}")
#         print(f"Grade        : {grade}")
#         print("--------------------------------------")

print(student_data)



def show_result(student_data):

    if not student_data:
        print("No student records available!")
        return

    print("\n" + "=" * 65)
    print("                 STUDENT RESULT REPORT")
    print("=" * 65)

    print(f"{'Student Name':<20} {'Marks':>10} {'Grade':>12}")
    print("-" * 65)

    marks_list = []

    for name, details in student_data.items():

        # Access nested dictionary values
        mark = details.get("Marks", 0)
        grade = details.get("Grade", "Not Available")

        marks_list.append(mark)

        print(f"{name:<20} {mark:>10.2f} {grade:>12}")

    print("-" * 65)

    # Calculate statistics
    average = sum(marks_list) / len(marks_list)
    highest = max(marks_list)
    lowest = min(marks_list)

    print("\nSTUDENT PERFORMANCE STATISTICS")
    print("-" * 65)
    print(f"Total Students : {len(student_data)}")
    print(f"Average Marks  : {average:.2f}")
    print(f"Highest Marks  : {highest:.2f}")
    print(f"Lowest Marks   : {lowest:.2f}")
    print("=" * 65)


show_result(student_data)