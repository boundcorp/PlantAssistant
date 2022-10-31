import uvicorn
if __name__ == '__main__':
    uvicorn.run('plantassistant.app_setup:app', host="0.0.0.0", port=9234, reload=True)