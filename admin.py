import uvicorn
if __name__ == '__main__':
    uvicorn.run('fastadmin.handler:app', host="0.0.0.0", port=9988, reload=True)