from app import create_app
from serverless_wsgi import handle_request  # Add this

app = create_app()  # Your Flask app instance

# Add this handler for Vercel
def handler(request, context):
    return handle_request(app, request, context)

# Local development (unchanged)
if __name__ == '__main__':
    app.run(debug=True)