import sqlite3
from backend.src.Data.Database import IDatabase


class SQLDatabase(IDatabase):
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()
            print(f"Connected to database: {self.db_file}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")


        
    def save_job(self, job, user_id):
        self.connect()
        self.cursor.execute(
        """
        INSERT INTO jobs (
            id, case_number, branch, description, status, created_at, completed_at, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (job.get("id"), job.get( "case_number"), job.get("branch"), job.get("description"), job.get("status"), job.get("created_at"), job.get("completed_at"), user_id)
        )
        self.close()


    def save_file_paths(self, permanent_filenames, permanent_filepaths, job_id, user_id):
        self.connect()

        for name, path in zip(permanent_filenames, permanent_filepaths):
            self.cursor.execute(
            """
            INSERT INTO uploads (
                permanent_file_name, file_path, job_id, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, path, job_id, user_id)
            )

        self.close()

    def add_user(self, name, user, password):
        self.connect()

        self.cursor.execute(
            """
            INSERT INTO users (
                name, username, password
            )
            """,
            (name, user, password)
        )

        self.close()


db = SQLDatabase("test.db")
db.connect()
db.cursor.execute(
    """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
)

db.cursor.execute(
    """
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            case_number TEXT NOT NULL,
            branch TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at DATE,
            completed_at DATE,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """
)


db.cursor.execute(
    """
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            permanent_file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            job_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (job_id) REFERENCES job(id)
            FOREIGN KEY (user_id) REFERENCES user(id)

        );
    """
)


db.cursor.execute(
    """
    INSERT INTO users (name, username, password)
    VALUES (?, ?, ?)
    """,
    ("Admin 1", "admin", "password")
)

db.close()