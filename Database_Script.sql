--DATABASE CREATED IN SQL FIRST BEFORE RUNNING FILE!
--Drop Tables for each demo
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS answers CASCADE;
DROP TABLE IF EXISTS results CASCADE;

-- Users Table
CREATE TABLE users (
    userid INTEGER PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role TEXT NOT NULL
);

-- Materials Table
CREATE TABLE materials (
    materialid SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,
    uploaded_by INTEGER REFERENCES users(userid)
);

-- Questions Table
CREATE TABLE questions (
    questionid SERIAL PRIMARY KEY,
    materialid INTEGER REFERENCES materials(materialid),
    text TEXT NOT NULL,
    created_by INTEGER REFERENCES users(userid)
);

-- Answers Table
CREATE TABLE answers (
    answerid SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    question_id INTEGER REFERENCES questions(questionid),
    submitted_by INTEGER REFERENCES users(userid)
);

-- Results Table
CREATE TABLE results (
    resultid SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions(questionid),
    materialid INTEGER REFERENCES materials(materialid),
    answer_id INTEGER REFERENCES answers(answerid),
    feedback TEXT NOT NULL,
    self_certified BOOLEAN DEFAULT FALSE
);

--Creating Users
INSERT INTO users(userid, username, password, role) 
VALUES(1,'teacher1', 'password1', 'teacher');

INSERT INTO users(userid, username, password, role) 
VALUES(2, 'student1', 'password1', 'student');