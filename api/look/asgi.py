from app import create_app
import uvicorn
app = create_app()

def main():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
    
if __name__ == "__main__":
    main()
