-- Step 1: Create Database
CREATE DATABASE soft_project;
USE soft_project;
-- Step 2: Create Users Table (Student Registry)
CREATE TABLE student_information (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(255) NOT NULL,
email VARCHAR(255) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL, -- Store hashed passwords
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- Step 3: Create Subjects Table (List of Available Subjects)
CREATE TABLE available_subjects (
id INT AUTO_INCREMENT PRIMARY KEY,
subject_name VARCHAR(255) UNIQUE NOT NULL
);
-- Step 4: Create Student-Subjects Table (Many-to-Many Relationship)
CREATE TABLE student_subjects (
student_id INT,
subject_id INT,
PRIMARY KEY (student_id, subject_id),
FOREIGN KEY (student_id) REFERENCES student_information(id) ON DELETE CASCADE,
FOREIGN KEY (subject_id) REFERENCES available_subjects(id) ON DELETE CASCADE
);
-- Step 5: Create Availability Table (Stores Student Available Times)
Alter TABLE student_availability (
id INT AUTO_INCREMENT PRIMARY KEY,
student_id INT NOT NULL,
day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT
NULL,
start_time TIME,
end_time TIME,
timezone VARCHAR(50) DEFAULT 'UTC',
FOREIGN KEY (student_id) REFERENCES student_information(id) ON DELETE CASCADE
);
-- Step 6: Insert Sample Data (Optional)
INSERT INTO student_information (name, email, password_hash)
VALUES
('Alice Johnson', 'alice@example.com', 'hashedpassword1'),
('Bob Smith', 'bob@example.com', 'hashedpassword2');
INSERT INTO available_subjects (subject_name)
VALUES
('Mathematics'),
('Physics'),
('Computer Science');
INSERT INTO student_subjects (student_id, subject_id)
VALUES
(1, 1), -- Alice studies Mathematics
(1, 2), -- Alice studies Physics
(2, 3); -- Bob studies Computer Science
INSERT INTO student_availability (student_id, day_of_week, start_time, end_time, timezone)
VALUES
(1, 'Monday', '14:00:00', '16:00:00', 'UTC'), -- Alice available Monday 2-4 PM
(2, 'Wednesday', '10:00:00', '12:00:00', 'UTC'); -- Bob available Wednesday 10AM-12PM
-- Step 7: Add study group tables
CREATE TABLE study_groups (
group_id INT AUTO_INCREMENT,
group_name varchar(255) not null,
subject_id int,
level_of_study VARCHAR(255),
group_owner_id INT not null,
primary key (group_id),
FOREIGN KEY (group_owner_id) REFERENCES student_information(id) ON DELETE CASCADE,
FOREIGN KEY (subject_id) REFERENCES available_subjects(id) ON DELETE cascade
);

INSERT INTO available_subjects (subject_name)
values
('Biology'),
('Chinese');

create table group_members (
group_id int,
student_id int,
primary key (group_id, student_id),
foreign key (group_id) references study_groups(group_id) on delete cascade,
foreign key (student_id) references student_information(id) on delete cascade
);

INSERT INTO study_groups (group_name, subject_id, level_of_study, group_owner_id )
VALUES
('Meadownet Chinese',5, 'Highschool', 4),
('GSU Biology1002', 4, 'Undergrad', 1);

insert into group_members (group_id, student_id)
values
(1,4),
(1,3),
(2,1);