"""Quiz question bank. Each question has: id, category, difficulty, question, options (4), correct_index."""

QUESTIONS = [
    # ===== PYTHON =====
    {"id": "py-e1", "category": "Python", "difficulty": "Easy", "question": "Which keyword is used to define a function in Python?", "options": ["func", "def", "function", "define"], "correct_index": 1},
    {"id": "py-e2", "category": "Python", "difficulty": "Easy", "question": "What is the output of: print(type([]))", "options": ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'array'>"], "correct_index": 0},
    {"id": "py-e3", "category": "Python", "difficulty": "Easy", "question": "Which of these is NOT a valid Python data type?", "options": ["list", "tuple", "array", "dict"], "correct_index": 2},
    {"id": "py-e4", "category": "Python", "difficulty": "Easy", "question": "How do you write a comment in Python?", "options": ["// comment", "/* comment */", "# comment", "-- comment"], "correct_index": 2},
    {"id": "py-m1", "category": "Python", "difficulty": "Medium", "question": "What does the 'self' keyword refer to in a class method?", "options": ["The class itself", "The current instance", "A global variable", "The parent class"], "correct_index": 1},
    {"id": "py-m2", "category": "Python", "difficulty": "Medium", "question": "What is the output of: print([1,2,3] * 2)", "options": ["[2, 4, 6]", "[1, 2, 3, 1, 2, 3]", "Error", "[1, 2, 3, 2, 4, 6]"], "correct_index": 1},
    {"id": "py-m3", "category": "Python", "difficulty": "Medium", "question": "Which method removes the last item from a list?", "options": ["remove()", "delete()", "pop()", "discard()"], "correct_index": 2},
    {"id": "py-m4", "category": "Python", "difficulty": "Medium", "question": "What does 'is' operator check in Python?", "options": ["Value equality", "Identity (same object)", "Type equality", "String equality"], "correct_index": 1},
    {"id": "py-h1", "category": "Python", "difficulty": "Hard", "question": "What is a metaclass in Python?", "options": ["A class inside a class", "A class of a class", "An abstract class", "A private class"], "correct_index": 1},
    {"id": "py-h2", "category": "Python", "difficulty": "Hard", "question": "Output of: print([x*2 for x in range(3)])", "options": ["[0, 2, 4]", "[2, 4, 6]", "[0, 1, 2]", "Error"], "correct_index": 0},
    {"id": "py-h3", "category": "Python", "difficulty": "Hard", "question": "What does the GIL stand for in CPython?", "options": ["General Interpreter Lock", "Global Interpreter Lock", "Global Instance Lock", "Generic Import Loader"], "correct_index": 1},

    # ===== DBMS =====
    {"id": "db-e1", "category": "DBMS", "difficulty": "Easy", "question": "What does SQL stand for?", "options": ["Structured Query Language", "Simple Query Language", "Standard Query Logic", "Sequential Query Language"], "correct_index": 0},
    {"id": "db-e2", "category": "DBMS", "difficulty": "Easy", "question": "Which SQL command is used to fetch data?", "options": ["GET", "FETCH", "SELECT", "PULL"], "correct_index": 2},
    {"id": "db-e3", "category": "DBMS", "difficulty": "Easy", "question": "A primary key can be:", "options": ["NULL", "Duplicate", "Unique and Not Null", "Any value"], "correct_index": 2},
    {"id": "db-e4", "category": "DBMS", "difficulty": "Easy", "question": "Which of these is a NoSQL database?", "options": ["MySQL", "PostgreSQL", "MongoDB", "Oracle"], "correct_index": 2},
    {"id": "db-m1", "category": "DBMS", "difficulty": "Medium", "question": "What does ACID stand for in DBMS?", "options": ["Atomicity, Consistency, Isolation, Durability", "Accuracy, Consistency, Integrity, Data", "Atomic, Concurrent, Isolated, Distributed", "Access, Control, Integrity, Data"], "correct_index": 0},
    {"id": "db-m2", "category": "DBMS", "difficulty": "Medium", "question": "Which normal form eliminates transitive dependency?", "options": ["1NF", "2NF", "3NF", "BCNF"], "correct_index": 2},
    {"id": "db-m3", "category": "DBMS", "difficulty": "Medium", "question": "Which JOIN returns all records from both tables?", "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"], "correct_index": 3},
    {"id": "db-m4", "category": "DBMS", "difficulty": "Medium", "question": "A foreign key references:", "options": ["Its own table", "A primary key in another table", "An index", "A view"], "correct_index": 1},
    {"id": "db-h1", "category": "DBMS", "difficulty": "Hard", "question": "What is the purpose of database indexing?", "options": ["To reduce storage", "To speed up data retrieval", "To encrypt data", "To back up data"], "correct_index": 1},
    {"id": "db-h2", "category": "DBMS", "difficulty": "Hard", "question": "In BCNF, every determinant must be a:", "options": ["Foreign key", "Candidate key", "Primary key only", "Unique attribute"], "correct_index": 1},
    {"id": "db-h3", "category": "DBMS", "difficulty": "Hard", "question": "Two-phase locking is used to ensure:", "options": ["Atomicity", "Serializability", "Durability", "Isolation via MVCC"], "correct_index": 1},

    # ===== OPERATING SYSTEM =====
    {"id": "os-e1", "category": "OS", "difficulty": "Easy", "question": "Which of these is NOT an operating system?", "options": ["Linux", "Windows", "Oracle", "macOS"], "correct_index": 2},
    {"id": "os-e2", "category": "OS", "difficulty": "Easy", "question": "The 'brain' of the computer is the:", "options": ["RAM", "CPU", "GPU", "SSD"], "correct_index": 1},
    {"id": "os-e3", "category": "OS", "difficulty": "Easy", "question": "Which one is a system call?", "options": ["printf()", "fork()", "sqrt()", "main()"], "correct_index": 1},
    {"id": "os-e4", "category": "OS", "difficulty": "Easy", "question": "Kernel is a part of:", "options": ["Compiler", "Operating System", "Application", "Hardware"], "correct_index": 1},
    {"id": "os-m1", "category": "OS", "difficulty": "Medium", "question": "Which scheduling algorithm can lead to starvation?", "options": ["FCFS", "Round Robin", "Priority Scheduling", "SJF (non-preemptive)"], "correct_index": 2},
    {"id": "os-m2", "category": "OS", "difficulty": "Medium", "question": "A deadlock requires all of these EXCEPT:", "options": ["Mutual exclusion", "Hold and wait", "Preemption", "Circular wait"], "correct_index": 2},
    {"id": "os-m3", "category": "OS", "difficulty": "Medium", "question": "Paging is used to solve:", "options": ["Deadlock", "External fragmentation", "Race conditions", "Starvation"], "correct_index": 1},
    {"id": "os-m4", "category": "OS", "difficulty": "Medium", "question": "Which state is a process in when waiting for CPU?", "options": ["Running", "Ready", "Blocked", "Terminated"], "correct_index": 1},
    {"id": "os-h1", "category": "OS", "difficulty": "Hard", "question": "Banker's algorithm is used for:", "options": ["Deadlock prevention", "Deadlock avoidance", "Deadlock detection", "Deadlock recovery"], "correct_index": 1},
    {"id": "os-h2", "category": "OS", "difficulty": "Hard", "question": "Which page replacement algorithm suffers from Belady's anomaly?", "options": ["LRU", "FIFO", "Optimal", "LFU"], "correct_index": 1},
    {"id": "os-h3", "category": "OS", "difficulty": "Hard", "question": "A semaphore with only values 0 and 1 is called:", "options": ["Counting semaphore", "Binary semaphore", "Mutex only", "Spinlock"], "correct_index": 1},

    # ===== APTITUDE =====
    {"id": "ap-e1", "category": "Aptitude", "difficulty": "Easy", "question": "What is 15% of 200?", "options": ["25", "30", "35", "20"], "correct_index": 1},
    {"id": "ap-e2", "category": "Aptitude", "difficulty": "Easy", "question": "If a = 5 and b = 3, what is a² - b²?", "options": ["8", "16", "25", "34"], "correct_index": 1},
    {"id": "ap-e3", "category": "Aptitude", "difficulty": "Easy", "question": "The next number in: 2, 4, 8, 16, ?", "options": ["24", "30", "32", "20"], "correct_index": 2},
    {"id": "ap-e4", "category": "Aptitude", "difficulty": "Easy", "question": "How many minutes are in 3.5 hours?", "options": ["180", "200", "210", "240"], "correct_index": 2},
    {"id": "ap-m1", "category": "Aptitude", "difficulty": "Medium", "question": "A train covers 240 km in 4 hours. Its speed is:", "options": ["50 km/h", "60 km/h", "70 km/h", "80 km/h"], "correct_index": 1},
    {"id": "ap-m2", "category": "Aptitude", "difficulty": "Medium", "question": "The average of 10, 20, 30, 40, 50 is:", "options": ["20", "25", "30", "35"], "correct_index": 2},
    {"id": "ap-m3", "category": "Aptitude", "difficulty": "Medium", "question": "If x + y = 10 and x - y = 4, then x =", "options": ["3", "5", "7", "8"], "correct_index": 2},
    {"id": "ap-m4", "category": "Aptitude", "difficulty": "Medium", "question": "A shop offers 20% discount on a $50 item. Sale price?", "options": ["$30", "$35", "$40", "$45"], "correct_index": 2},
    {"id": "ap-h1", "category": "Aptitude", "difficulty": "Hard", "question": "Compound interest on 1000 at 10% for 2 years is:", "options": ["200", "210", "220", "231"], "correct_index": 1},
    {"id": "ap-h2", "category": "Aptitude", "difficulty": "Hard", "question": "A can do work in 10 days, B in 15. Together:", "options": ["5 days", "6 days", "8 days", "12 days"], "correct_index": 1},
    {"id": "ap-h3", "category": "Aptitude", "difficulty": "Hard", "question": "Probability of getting a sum of 7 with two dice:", "options": ["1/6", "1/8", "1/12", "1/9"], "correct_index": 0},

    # ===== PYTHON (extra 9) =====
    {"id": "py-e5", "category": "Python", "difficulty": "Easy", "question": "Which symbol is used for exponentiation in Python?", "options": ["^", "**", "//", "exp"], "correct_index": 1},
    {"id": "py-e6", "category": "Python", "difficulty": "Easy", "question": "What does len('hello') return?", "options": ["4", "5", "6", "Error"], "correct_index": 1},
    {"id": "py-e7", "category": "Python", "difficulty": "Easy", "question": "Which function converts a string to an integer?", "options": ["str()", "int()", "float()", "eval()"], "correct_index": 1},
    {"id": "py-m5", "category": "Python", "difficulty": "Medium", "question": "Which of these creates a set?", "options": ["{}", "set()", "[]", "()"], "correct_index": 1},
    {"id": "py-m6", "category": "Python", "difficulty": "Medium", "question": "What is *args used for?", "options": ["Keyword args", "Variable positional args", "Default values", "Type hints"], "correct_index": 1},
    {"id": "py-m7", "category": "Python", "difficulty": "Medium", "question": "Output of: bool([])", "options": ["True", "False", "None", "Error"], "correct_index": 1},
    {"id": "py-h4", "category": "Python", "difficulty": "Hard", "question": "Which is NOT thread-safe by default in CPython due to the GIL?", "options": ["list.append", "dict.setdefault", "Compound += on int", "None of these are safe"], "correct_index": 2},
    {"id": "py-h5", "category": "Python", "difficulty": "Hard", "question": "What does __slots__ do?", "options": ["Speeds up imports", "Restricts attributes & saves memory", "Enables slots for threading", "Creates a singleton"], "correct_index": 1},
    {"id": "py-h6", "category": "Python", "difficulty": "Hard", "question": "Result of: (lambda x: x*x)(5)", "options": ["10", "25", "5", "Error"], "correct_index": 1},

    # ===== DBMS (extra 9) =====
    {"id": "db-e5", "category": "DBMS", "difficulty": "Easy", "question": "DDL stands for:", "options": ["Data Definition Language", "Data Design Language", "Direct Data Language", "Database Def Language"], "correct_index": 0},
    {"id": "db-e6", "category": "DBMS", "difficulty": "Easy", "question": "Which SQL clause filters rows?", "options": ["ORDER BY", "GROUP BY", "WHERE", "HAVING"], "correct_index": 2},
    {"id": "db-e7", "category": "DBMS", "difficulty": "Easy", "question": "Which is used to remove a table entirely?", "options": ["DELETE", "TRUNCATE", "DROP", "REMOVE"], "correct_index": 2},
    {"id": "db-m5", "category": "DBMS", "difficulty": "Medium", "question": "HAVING is used with:", "options": ["ORDER BY", "GROUP BY", "JOIN", "UNION"], "correct_index": 1},
    {"id": "db-m6", "category": "DBMS", "difficulty": "Medium", "question": "A view is:", "options": ["A stored table", "A virtual table from a query", "An index", "A backup"], "correct_index": 1},
    {"id": "db-m7", "category": "DBMS", "difficulty": "Medium", "question": "A tuple in relational DB means:", "options": ["A column", "A row/record", "A table", "A constraint"], "correct_index": 1},
    {"id": "db-h4", "category": "DBMS", "difficulty": "Hard", "question": "Isolation level that prevents phantom reads:", "options": ["Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable"], "correct_index": 3},
    {"id": "db-h5", "category": "DBMS", "difficulty": "Hard", "question": "Which is a hash-based index structure?", "options": ["B-tree", "B+-tree", "Extendible hashing", "Bitmap"], "correct_index": 2},
    {"id": "db-h6", "category": "DBMS", "difficulty": "Hard", "question": "CAP theorem states you can pick:", "options": ["All three", "Any two", "Only one", "Consistency always"], "correct_index": 1},

    # ===== OS (extra 9) =====
    {"id": "os-e5", "category": "OS", "difficulty": "Easy", "question": "Which is a mobile OS?", "options": ["Ubuntu", "Android", "Debian", "Fedora"], "correct_index": 1},
    {"id": "os-e6", "category": "OS", "difficulty": "Easy", "question": "RAM is:", "options": ["Non-volatile", "Volatile", "Read-only", "Optical"], "correct_index": 1},
    {"id": "os-e7", "category": "OS", "difficulty": "Easy", "question": "Which command lists files on Linux?", "options": ["dir", "ls", "list", "show"], "correct_index": 1},
    {"id": "os-m5", "category": "OS", "difficulty": "Medium", "question": "Thrashing refers to:", "options": ["Excessive paging with low throughput", "Fast context switch", "Cache hits", "Deadlock"], "correct_index": 0},
    {"id": "os-m6", "category": "OS", "difficulty": "Medium", "question": "A zombie process is one that:", "options": ["Runs forever", "Has terminated but not reaped", "Is starving", "Was killed forcibly"], "correct_index": 1},
    {"id": "os-m7", "category": "OS", "difficulty": "Medium", "question": "fork() returns to child:", "options": ["Child PID", "0", "-1", "Parent PID"], "correct_index": 1},
    {"id": "os-h4", "category": "OS", "difficulty": "Hard", "question": "Peterson's algorithm solves:", "options": ["Deadlock", "Mutual exclusion (2 processes)", "Starvation", "Paging"], "correct_index": 1},
    {"id": "os-h5", "category": "OS", "difficulty": "Hard", "question": "Which is TRUE about a microkernel?", "options": ["More services in kernel space", "Fewer services in kernel, more in userspace", "Faster than monolithic always", "No IPC needed"], "correct_index": 1},
    {"id": "os-h6", "category": "OS", "difficulty": "Hard", "question": "In demand paging, a page fault causes:", "options": ["Kernel panic", "Trap to OS, load page", "Process termination", "Cache flush only"], "correct_index": 1},

    # ===== APTITUDE (extra 9) =====
    {"id": "ap-e5", "category": "Aptitude", "difficulty": "Easy", "question": "What is 25% of 80?", "options": ["15", "20", "25", "30"], "correct_index": 1},
    {"id": "ap-e6", "category": "Aptitude", "difficulty": "Easy", "question": "The LCM of 4 and 6 is:", "options": ["10", "12", "18", "24"], "correct_index": 1},
    {"id": "ap-e7", "category": "Aptitude", "difficulty": "Easy", "question": "If 3x = 21, then x = ?", "options": ["3", "5", "7", "9"], "correct_index": 2},
    {"id": "ap-m5", "category": "Aptitude", "difficulty": "Medium", "question": "Ratio of 45 minutes to 2 hours:", "options": ["3:8", "1:2", "2:5", "9:16"], "correct_index": 0},
    {"id": "ap-m6", "category": "Aptitude", "difficulty": "Medium", "question": "Simple interest on 5000 at 8% for 3 years:", "options": ["800", "1000", "1200", "1500"], "correct_index": 2},
    {"id": "ap-m7", "category": "Aptitude", "difficulty": "Medium", "question": "Odd one out: 4, 9, 16, 20, 25", "options": ["4", "16", "20", "25"], "correct_index": 2},
    {"id": "ap-h4", "category": "Aptitude", "difficulty": "Hard", "question": "A shopkeeper marks up 40% and gives 10% discount. Profit %?", "options": ["24%", "26%", "28%", "30%"], "correct_index": 1},
    {"id": "ap-h5", "category": "Aptitude", "difficulty": "Hard", "question": "In how many ways can 5 people sit in a row?", "options": ["25", "60", "120", "125"], "correct_index": 2},
    {"id": "ap-h6", "category": "Aptitude", "difficulty": "Hard", "question": "The average of first 10 natural numbers:", "options": ["5", "5.5", "6", "10"], "correct_index": 1},
]

CATEGORIES = ["Python", "DBMS", "OS", "Aptitude"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]

QUESTIONS_BY_ID = {q["id"]: q for q in QUESTIONS}
