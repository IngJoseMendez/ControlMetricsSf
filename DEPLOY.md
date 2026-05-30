# ControlMetrics – Guía de Despliegue

Arquitectura: **FastAPI (Render.com free)** + **Next.js (Vercel free)**

---

## 1. Subir el código a GitHub

```bash
git add .
git commit -m "ControlMetrics web app – FastAPI + Next.js"
git remote add origin https://github.com/TU_USUARIO/controlmetrics.git
git push -u origin master
```

---

## 2. Desplegar el Backend en Render.com

### 2.1 Crear cuenta y nuevo servicio

1. Ir a [render.com](https://render.com) → **New → Web Service**
2. Conectar tu repositorio de GitHub
3. Configurar:
   - **Name**: `controlmetrics-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

4. Click **Create Web Service**

### 2.2 URL resultante

Render asignará una URL del tipo:
```
https://controlmetrics-api.onrender.com
```

> **Nota**: El plan gratuito de Render "duerme" el servicio tras 15 min de inactividad.
> La primera petición tarda ~30s en despertar. Las siguientes son instantáneas.

---

## 3. Desplegar el Frontend en Vercel

### 3.1 Importar proyecto

1. Ir a [vercel.com](https://vercel.com) → **New Project**
2. Importar el repositorio de GitHub
3. Configurar:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (detectado automáticamente)

### 3.2 Variable de entorno (IMPORTANTE)

En la sección **Environment Variables** de Vercel, agregar:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://controlmetrics-api.onrender.com` |

> Reemplaza la URL con la que te asignó Render en el paso 2.2.

4. Click **Deploy**

---

## 4. Desarrollo local

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API disponible en: http://localhost:8000
Docs interactivas: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App disponible en: http://localhost:3000

El archivo `frontend/.env.local` apunta al backend local (http://localhost:8000).

---

## 5. Estructura del proyecto

```
ControlMetrics/
├── backend/
│   ├── main.py              # FastAPI app + CORS
│   ├── config.py            # Constantes SPC, datos demo
│   ├── requirements.txt
│   ├── routers/
│   │   ├── normalidad.py    # POST /api/normalidad
│   │   ├── cartas_xr.py     # POST /api/cartas-xr
│   │   ├── cartas_pnpu.py   # POST /api/cartas-pnpu
│   │   ├── carta_c.py       # POST /api/carta-c
│   │   ├── capacidad.py     # POST /api/capacidad
│   │   ├── muestreo.py      # POST /api/muestreo
│   │   └── mejora.py        # POST /api/mejora
│   └── utils/
│       ├── spc_utils.py     # Lógica estadística (original)
│       └── chart_utils.py   # matplotlib → base64 PNG
└── frontend/
    ├── app/
    │   ├── page.tsx         # Landing page
    │   └── spc/
    │       ├── layout.tsx   # Sidebar de navegación
    │       ├── page.tsx     # Dashboard de módulos
    │       ├── normalidad/
    │       ├── cartas-xr/
    │       ├── cartas-pnpu/
    │       ├── carta-c/
    │       ├── capacidad/
    │       ├── muestreo/
    │       └── mejora/
    ├── components/spc/
    │   ├── ModuleShell.tsx  # Layout inputs/resultados
    │   └── ChartCard.tsx    # Tarjeta de gráfica base64
    └── lib/api.ts           # Cliente HTTP tipado
```
