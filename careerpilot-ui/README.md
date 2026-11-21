# 🚀 CareerPilot AI - Frontend Web Portal

Modern, responsive Web UI dashboard built with **React**, **TypeScript**, **Vite**, and **Tailwind CSS**.
Pre-configured for **Firebase Hosting (`careerpilot-ai-cd651`)** with automatic proxying to the Spring Boot REST backend on Google Cloud Run.

---

## 🛠️ Quick Start (Local Development)

```bash
# 1. Install dependencies
npm install

# 2. Run local dev server (Runs on port 3000, proxies /api calls to localhost:8080)
npm run dev

# 3. Build production bundle
npm run build
```

---

## 🌐 Deploy to Firebase Hosting (`careerpilot-ai-cd651`)

```bash
# Login to Firebase
firebase login

# Deploy directly to live hosting
firebase deploy --only hosting
```

---

## 🔗 Push to a Dedicated GitHub Repository

To host this in its own repository `laxman235/CareerPilot-UI`:

```bash
cd careerpilot-ui
git init
git add .
git commit -m "feat: initial CareerPilot AI React dashboard with Firebase config"
git branch -M main
git remote add origin https://github.com/laxman235/CareerPilot-UI.git
git push -u origin main
```
