from app import create_app

app = create_app()  # Your Flask app instance

# Local development (unchanged)
if __name__ == '__main__':
    app.run(debug=True)