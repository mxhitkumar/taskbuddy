# Postman Collection Setup Guide

## 📥 Import the Collection

### Method 1: Direct Import (Recommended)

1. **Copy the JSON content** from `Service Marketplace - Postman Collection` artifact
2. **Open Postman**
3. Click **Import** button (top left)
4. Select **Raw text** tab
5. **Paste** the entire JSON content
6. Click **Import**

### Method 2: Import from File

1. **Save the JSON** as `service-marketplace-api.postman_collection.json`
2. **Open Postman**
3. Click **Import** button
4. **Drag and drop** the file or click **Choose Files**
5. Click **Import**

---

## 🔧 Setup Environment Variables

### Create Environment

1. Click on **Environments** (left sidebar)
2. Click **+** to create new environment
3. Name it: `Service Marketplace - Local`
4. Add these variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `access_token` | ` ` | ` ` |
| `refresh_token` | ` ` | ` ` |
| `user_id` | ` ` | `