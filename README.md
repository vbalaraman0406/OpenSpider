# OpenSpider 🕷️
Autonomous Multi-Agent System tailored for WhatsApp.

This guide walks you through the step-by-step process of installing, configuring, and testing OpenSpider locally.

## Getting Started

### Step 1: Installation & Global Linking
To use the `openspider` CLI commands globally on your machine, you must link the built package. 

From the root directory of the OpenSpider repository, run:
```bash
npm link
```
This creates a global symlink, allowing you to run `openspider` from anywhere.

### Step 2: Onboarding & Configuration
OpenSpider requires you to configure an LLM provider (like Google Antigravity) and define your agent's persona.

To start the interactive setup wizard, run:
```bash
openspider onboard
```
This wizard will automatically generate an `.env` file in your current directory.

### Step 3: Starting the Gateway Manager Server
The OpenSpider Gateway is the core engine that processes requests, manages agents, and handles WebSocket connections.

To start the gateway server, run:
```bash
openspider gateway
```
You should see a message indicating the server is running on `http://localhost:3000`. Leave this terminal window open.

### Step 4: Accessing the Web Dashboard (Optional)
OpenSpider includes a graphical web dashboard for managing the agent and viewing logs.

1. Open a **new terminal tab/window**.
2. Navigate to the dashboard directory:
   ```bash
   cd dashboard
   ```
3. Install dependencies and start the development server:
   ```bash
   npm i
   npm run dev
   ```
4. Open your browser and navigate to the URL provided (usually `http://localhost:5173`).
