#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Document Chat Service Launcher${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if .env exists in backend
if [ ! -f backend/.env ]; then
    echo -e "${RED}Error: backend/.env not found!${NC}"
    echo "Please copy backend/.env.example to backend/.env and configure your SAP credentials"
    echo "  cd backend && cp .env.example .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d backend/venv ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
fi

# Check if node_modules exists
if [ ! -d frontend/node_modules ]; then
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}\n"
fi

echo -e "${BLUE}Starting services...${NC}\n"

# Start backend
echo -e "${GREEN}Starting backend on http://localhost:8000${NC}"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}Starting frontend on http://localhost:3000${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}   Services Started Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "\n${RED}Press Ctrl+C to stop all services${NC}\n"

# Cleanup function
cleanup() {
    echo -e "\n${BLUE}Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Services stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait
