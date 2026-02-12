# ⚡ 5-Minute Quick Start

## You Need:
- Python 3.8+ installed
- The 4 files (models.py, storage.py, logic.py, app_saas.py)

## Run in 5 Steps:

### 1️⃣ Install Streamlit (1 min)
```bash
pip install streamlit
```

### 2️⃣ Create folder (1 min)
```bash
mkdir axon-app
cd axon-app
```

### 3️⃣ Copy files (1 min)
Copy these 4 files into your `axon-app` folder:
- `models.py`
- `storage.py`
- `logic.py`
- `app_saas.py`

### 4️⃣ Run app (1 min)
```bash
streamlit run app_saas.py
```

### 5️⃣ Open browser (1 min)
Browser opens automatically to `http://localhost:8501`

---

## Done! 🎉

You now have a production-ready thought management app.

### What to do next:
1. Click "➕ New Thought"
2. Add your first thought
3. Try filtering and searching
4. Check analytics

---

## File Structure (What You Need)

```
axon-app/
├── models.py
├── storage.py
├── logic.py
├── app_saas.py
└── axon_thoughts.json (auto-created)
```

That's it! No other files needed.

---

## Key Features Ready to Use

✅ Add/Edit/Delete thoughts
✅ Categorize (Task/Idea/Worry)
✅ Prioritize (Low/Medium/High)
✅ Search by keyword
✅ Filter by category & priority
✅ Analytics & statistics
✅ CSV export
✅ All data saved locally

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | `pip install streamlit` |
| Port in use | `streamlit run app_saas.py --server.port 8502` |
| Nothing happens | Wait 10 seconds, refresh browser |
| Lost data | Check `axon_thoughts.json` file exists |

---

That's all you need to get started! 🚀