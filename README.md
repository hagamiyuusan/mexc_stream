# MEXC WebSocket Dashboard

A real-time cryptocurrency dashboard built with Next.js and Python WebSocket server.

## Prerequisites

- Node.js (v18 or higher)
- PNPM
- Python (v3.8 or higher)
- pip

## Installation

### Frontend Setup

1. Install Node.js

   - Windows: Download and install from [nodejs.org](https://nodejs.org/)
   - Mac: `brew install node`
   - Linux: `sudo apt install nodejs`

2. Install PNPM
   bash
   npm install -g pnpm
3. Install frontend dependencies
   bash
   cd next-shadcn-admin-dashboard
   pnpm install
4. Run the development server
   bash
   pnpm run dev
   The frontend will be available at [http://localhost:3000](http://localhost:3000)

### Backend Setup

1. Create and activate a virtual environment (recommended)
   bash
   python -m venv venv
   source venv/bin/activate
2. Install dependencies
   bash
   pip install -r requirements.txt

3. Configure your MEXC API credentials

   - Open `main.py`
   - Replace `YourApiKey` and `YourSecretKey` with your actual MEXC API credentials

4. Start the backend server
   bash
   python main.py
   The WebSocket server will start on `ws://localhost:8000`

## Project Structure

- `next-shadcn-admin-dashboard/`: Frontend Next.js application
- `main.py`: Backend WebSocket server
- `requirements.txt`: Python dependencies

## Features

- Real-time asset balance updates
- WebSocket communication
- Modern UI with Shadcn components
- Responsive dashboard layout
