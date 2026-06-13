import uvicorn

if __name__ == '__main__':
    # python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug --reload
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
