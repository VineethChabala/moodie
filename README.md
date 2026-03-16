# Moodie AI 🍿

Moodie is a context-aware movie recommendation app built with Streamlit and the TMDB (The Movie Database) API. It goes beyond simple genre filtering by understanding your current mood, energy level, who you're watching with, and your era preferences to suggest the perfect movie.

## Features ✨
- **Smart Mapping**: Converts human feelings (Happy/Light, Sad/Emotional, etc.) into precise TMDB API queries.
- **Context-Aware**: Adapts recommendations based on whether you're alone, on a date night, or with family/kids.
- **State Management**: Remembers your discarded movies so you can easily skip to the next recommendation without restarting your search.
- **Interactive UI**: Clean, responsive Streamlit interface with movie posters, plot summaries, ratings, and quick action buttons.

## Prerequisites 🛠️
- Python 3.7 or higher
- A TMDB API Key. You can get one by creating an account at [The Movie Database](https://www.themoviedb.org/).

## Installation & Setup 🚀

1. **Clone the repository** (or download the files):
   ```bash
   git clone <repository-url>
   cd moodie
   ```

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API Key**:
   Streamlit uses a `secrets.toml` file to manage sensitive information securely.
   - Create a directory named `.streamlit` in the root of your project.
   - Create a file named `secrets.toml` inside the `.streamlit` directory and add your TMDB API key:
     ```toml
     TMDB_API_KEY = "your_tmdb_api_key_here"
     ```

## Running the App 🏃‍♂️

Start the Streamlit development server:
```bash
streamlit run app.py
```

The app should automatically open in your default web browser at `http://localhost:8501`.

## Usage 💡
1. Open the sidebar and adjust your **Diagnostic Inputs**:
   - **How are you feeling?**: Happy/Light, Sad/Emotional, Tense/Angry, Curious/Bored.
   - **Energy Level**: Low (Chill), Medium (Engaging), High (Adrenaline).
   - **Who's watching?**: Just Me, Date Night, Family/Kids.
   - **Era Preference**: Any, Modern (2010+), Classic (Pre-2000).
2. Click **Find Movies** to generate a query tailored to your current context.
3. Review the recommended movie poster, plot, rating, and popularity.
4. Click **I'll Watch This!** to confirm your choice, or **Seen it / Skip** to immediately view the next best recommendation without needing to reload the page.
