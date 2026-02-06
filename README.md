# 🧠 Axon - AI-Inspired Thought Organizer

A lightweight, simple Python application that helps you turn messy, unstructured thoughts into clear, organized structure. Built as a learning project using Streamlit and basic Python logic—no paid AI APIs required!

## 🎯 What Axon Does

Axon takes your free-form brain dumps and transforms them into:
- ✅ Organized bullet points
- ✅ Clear sentence separation
- ✅ Identified key topics/keywords
- ✅ Thoughts grouped by topic
- ✅ Quick summaries

Perfect for organizing ideas, plans, worries, or any messy thoughts bouncing around in your head.

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project:**
   ```bash
   cd axon
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   This installs Streamlit, the only external dependency we need.

3. **Run the app:**
   ```bash
   streamlit run axon_app.py
   ```

4. **Open in your browser:**
   Streamlit will automatically open the app at `http://localhost:8501`

## 📚 How It Works

### Core Components

#### 1. **Sentence Splitter** (`split_into_sentences`)
- Uses regex to break text into sentences at `.`, `!`, and `?`
- Keeps punctuation and removes extra whitespace
- Handles multiple spaces between sentences

#### 2. **Keyword Extractor** (`identify_keywords`)
- Extracts all words and filters out common "stop words"
- Counts word frequency to find important topics
- Returns top 10 most common keywords (appearing 2+ times)

#### 3. **Topic Grouper** (`group_by_keywords`)
- Matches sentences to keywords they contain
- Groups related sentences under their topics
- Collects ungrouped thoughts under "Other thoughts"

#### 4. **Summary Generator** (`create_summary`)
- Extracts first 2 sentences as a quick overview
- Truncates if too long (150 characters max)
- Gives users an at-a-glance understanding

### Example

**Input (Messy Brain Dump):**
```
Need to finish the project by Friday. Also need to buy groceries. 
The project is complex and needs testing. Don't forget to call Mom. 
Groceries: milk, eggs, bread. Project deadline is critical.
```

**Output:**
- **Summary:** "Need to finish the project by Friday. Also need to buy groceries."
- **Keywords:** project, groceries, need, finish, buy, testing, deadline...
- **Grouped Thoughts:**
  - Project (4 thoughts)
  - Groceries (2 thoughts)
  - Other thoughts (1 thought)

## 🎓 Learning Value

This project teaches:
1. **Text processing** - Regex, string manipulation, tokenization
2. **Data structures** - Dictionaries, lists, counter objects
3. **Algorithm design** - Keyword extraction, grouping logic
4. **UI/UX building** - Streamlit for interactive apps
5. **Software design** - Modular functions, clean code practices

## 🛣️ Future Roadmap

### Phase 2: Enhanced Logic
- Sentiment analysis (detect worried vs excited thoughts)
- Priority detection (identify urgent tasks)
- Better keyword weighting (noun emphasis)
- Duplicate detection and merging

### Phase 3: Real AI Integration
- Replace logic with API calls to Claude, GPT-4, or local LLMs
- Fine-tuned models for thought organization
- Entity recognition (names, dates, locations)
- Smart categorization

### Phase 4: Advanced Features
- Save/load organized thoughts
- Export to formats (JSON, Markdown, PDF)
- Multi-language support
- Voice input
- Dark mode

## 📁 Project Structure

```
axon/
├── axon_app.py           # Main application file
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 💡 Code Overview

### Main Function Flow

```python
User Input (text_area)
    ↓
organize_thoughts()
    ├─→ split_into_sentences()
    ├─→ identify_keywords()
    ├─→ group_by_keywords()
    └─→ create_summary()
    ↓
Display Results
    ├─ Summary
    ├─ Key Topics
    ├─ Grouped Thoughts (expandable)
    └─ Bullet List
```

### Key Features

- **Simple Logic Only** - No machine learning, no APIs
- **Beginner-Friendly** - Well-commented code, clear variable names
- **Interactive UI** - Clean Streamlit interface with nice styling
- **Instant Feedback** - Results update as you type (or on button click)
- **No Account Needed** - Runs entirely locally

## 🐛 Limitations & Known Behaviors

- Works best with 3+ sentences (needs enough text for keyword extraction)
- Stop word list is English-only
- Doesn't understand context (keyword matching is surface-level)
- Requires clear sentence punctuation
- May over-group if keywords appear in many sentences

## 🤝 Contributing

Have ideas for improvement? Some ways to extend this:
- Add sentiment analysis
- Implement better NLP using NLTK
- Create visualization dashboards
- Add database persistence
- Build priority/urgency detection

## 📝 License

This is a learning project. Feel free to use, modify, and build upon it!

## 🙋 Questions?

This project is designed to be readable and understandable for beginners. If anything is unclear:
1. Check the comments in `axon_app.py`
2. Experiment by modifying the stop words or keyword limits
3. Trace through a function with a simple input

---

**Built with ❤️ as a learning project**
*Exploring how AI-style systems organize information, one thought at a time.*