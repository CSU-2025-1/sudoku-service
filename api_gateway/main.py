import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from handlers import app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    print("Server started at :8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == '__main__':
    main()