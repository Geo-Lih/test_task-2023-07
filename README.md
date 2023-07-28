Test_task

This is a FastAPI project that serves as a JSON API for managing credits and payment plans. The project uses MySQL as the database, SQLAlchemy as the ORM for database operations, and Alembic for managing database migrations. Uvicorn is used as the ASGI server to run the FastAPI application. During the development of this app, the primary focus was aimed at leveraging SQLAlchemy and its advanced querying capabilities to interact with the database efficiently.




Entity Relationship Diagram (ERD)
        ![drawSQL-test-task-export-2023-07-27](https://github.com/Geo-Lih/test_task-2023-07/assets/72580162/e369b39e-d554-4e17-a649-0c9a99af86f4)




Uploading Instructions:

1. Clone the Repository:

        git clone https://github.com/Geo-Lih/test_task-2023-07.git


2. Set Up Virtual Environment:

        python3 -m venv venv

3. Activate the virtual environment:

        source venv/bin/activate


4. Install Dependencies:

        pip install -r requirements.txt


5. Set Up Environment Variables:

You need to create a `.env` file in the root of the project with the following structure:

        DB_HOST=localhost
        
        DB_PORT=3306
        
        DB_NAME=test_task
        
        DB_USER=your_database_user
        
        DB_PASS=your_database_password


6. Run Alembic Migrations:

First, make sure your database connection details are correctly set in the `.env` file.

        alembic upgrade ecaa46fea308

This will apply all pending migrations and update the database schema.


7. Run the FastAPI Application:

        uvicorn main:app --reload
