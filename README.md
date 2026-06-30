# Moodie AI 🍿

Moodie AI is a highly interactive, context-aware movie recommendation dashboard built with **Streamlit**, powered by **TMDB (The Movie Database)**, and supercharged with **Hugging Face Sentence Transformers** and **Google Gemini AI**. 

Unlike standard genre search tools, Moodie AI deciphers your immediate feelings, social context, and energy levels to recommend the perfect movie, or performs semantic search over hundreds of thousands of movie plots.

---

## 🏗️ Project Architecture & File Directory

The project is structured as follows:

* **[`app.py`](app.py)**: The main Streamlit entry point. Contains the state router, navigation views (Landing page, Knobs screen, and Semantic Prompt screen), query builders, and integration endpoints.
* **[`sematic_recommender.py`](sematic_recommender.py)**: Implements semantic search using `SentenceTransformer('all-MiniLM-L6-v2')`. Dynamically fetches large CSV datasets and embedding vectors from Google Drive if they are not cached locally.
* **[`vibe_checker.py`](vibe_checker.py)**: The audience vibe validator. Uses `gemini-2.5-flash` to read scraped user reviews and extract structured JSON (primary emotion, content warnings, and emotional consensus).
* **[`lb_scrapper.py`](lb_scrapper.py)**: A BeautifulSoup-based Letterboxd reviews parser designed to bypass common bot checks using `cloudscraper`.
* **[`driveids.id`](driveids.id)**: Tracks ID variants (CSV & NPY versions) on Google Drive for easy download configuration.

---

## ✨ Key Features

### 🎛️ 1. Context-Aware Diagnostic Knobs
Input your context through the sidebar controls:
* **How are you feeling?**: (Happy/Light, Sad/Emotional, Tense/Angry, Curious/Bored).
* **Energy Level**: (Low/Chill, Medium/Engaging, High/Adrenaline). Adjusts target review counts and popularity priority.
* **Who's watching?**: (Just Me, Date Night, Family/Kids). Automatically adjusts age certifications (e.g. PG limits for kids) and pushes romance/comedy weights.
* **Era Preference**: (Any, Modern 2010+, Classic Pre-2000).

### ✍️ 2. Natural Language Semantic Search
Simply type how you feel or describe a plot (e.g. *"dark space exploration with robots"*). Using `all-MiniLM-L6-v2` dense vector matching over our database, Moodie AI will instantly identify and return the top 10 matching films.

### 🗣️ 3. Audience Vibe Check (Gemini AI)
By parsing user reviews directly from Letterboxd, the integrated Film Psychologist (powered by Gemini Flash) reads between the lines to deliver:
* **True Emotional Consensus** (e.g., *"Stressful"*, *"Comforting"*)
* **Content Warnings** (flags potential triggers or unexpected themes)
* **General Vibe Summary** (capsules audience response in 1-2 sentences)

### 💾 4. Smart Session State Management
Never see the same movie twice. Moodie AI remembers your discarded or already-seen recommendations during a session, allowing you to skip to the next choice instantly without reloading.

---

## 🛠️ Prerequisites & API Configurations

Ensure you have the following API keys ready:
1. **TMDB API Key**: Available under API Settings on [The Movie Database](https://www.themoviedb.org/).
2. **Google Gemini API Key**: Obtainable from [Google AI Studio](https://aistudio.google.com/app/apikey).
3. **Hugging Face Token**: Available in settings on [Hugging Face](https://huggingface.co/settings/tokens).

### Streamlit Secrets Configuration

Create a folder named `.streamlit` in the root of the project, and inside it create a `secrets.toml` file containing your credentials:

```toml
TMDB_API_KEY = "your_tmdb_api_key_here"
GEMINI_API_KEY = "your_gemini_api_key_here"
HUGGINGFACE_API_KEY = "your_hf_token_here"
CSV_DRIVE_ID = "your_csv_drive_id_here"
NPY_DRIVE_ID = "your_npy_drive_id_here"
```

> [!TIP]
> You can retrieve the Google Drive File IDs from the **[`driveids.id`](driveids.id)** file, which lists IDs for different database sizes/versions.

---

## 🚀 Installation & Setup

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```

3. **Browse local application**:
   Open `http://localhost:8501` in your browser.
