#!/bin/bash
cd /workspace/project/recruiter-in-a-box/backend
source .env.test
export PATH="$HOME/.local/bin:$PATH"
/home/openhands/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
