import streamlit as st
import requests
import random
from vibe_checker import VibeChecker

# --- CONFIGURATION ---
try:
    API_KEY = st.secrets["TMDB_API_KEY"]
except FileNotFoundError:
    st.error("API Key not found. Please set it in secrets.")
BASE_URL = "https://api.themoviedb.org/3"

# --- PAGE SETUP ---
st.set_page_config(page_title="Moodie AI", page_icon="🍿", layout="wide")

# Custom CSS for a better look
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
    }
    .movie-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIC ENGINE ---

# 1. Smart Mapping: Converts human feelings to Data Points
GENRES = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35,
    "Crime": 80, "Documentary": 99, "Drama": 18, "Family": 10751,
    "Fantasy": 14, "History": 36, "Horror": 27, "Mystery": 9648,
    "Romance": 10749, "Sci-Fi": 878, "Thriller": 53
}

def build_smart_query(mood, energy, company, era):
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "vote_count.gte": 200,
        "page": 1
    }
    
    genres = []
    
    # MOOD LOGIC
    if mood == "Happy/Light":
        genres.extend([GENRES['Comedy'], GENRES['Adventure'], GENRES['Animation']])
    elif mood == "Sad/Emotional":
        if energy == "Low (Chill)":
            genres.extend([GENRES['Drama'], GENRES['Romance']]) # Cry it out
        else:
            genres.extend([GENRES['Comedy'], GENRES['Family']]) # Cheer up
    elif mood == "Tense/Angry":
        genres.extend([GENRES['Action'], GENRES['Thriller'], GENRES['Crime']])
    elif mood == "Curious/Bored":
        genres.extend([GENRES['Sci-Fi'], GENRES['Mystery'], GENRES['Documentary']])
        
    # COMPANY LOGIC
    if company == "Family/Kids":
        params["certification_country"] = "US"
        params["certification.lte"] = "PG"
        if GENRES['Horror'] in genres: genres.remove(GENRES['Horror'])
        if GENRES['Crime'] in genres: genres.remove(GENRES['Crime'])
    elif company == "Date Night":
        genres.append(GENRES['Romance'])

    # ERA LOGIC
    if era == "Modern (2010+)":
        params["primary_release_date.gte"] = "2010-01-01"
    elif era == "Classic (Pre-2000)":
        params["primary_release_date.lte"] = "2000-01-01"
        
    # ENERGY LOGIC (Adjusts Sorting)
    if energy == "High (Adrenaline)":
        params["sort_by"] = "popularity.desc"
    elif energy == "Medium (Engaging)":
        params["vote_average.gte"] = 7.0 
        
    # Finalize Genres
    if genres:
        params["with_genres"] = "|".join(map(str, genres))
        
    return params

def fetch_movies(params):
    try:
        response = requests.get(f"{BASE_URL}/discover/movie", params=params)
        data = response.json()
        return data.get('results', [])
    except:
        return []

# --- STATE MANAGEMENT ---
# This makes the app "Smart" by remembering where you are
if 'movies' not in st.session_state:
    st.session_state.movies = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

vibe_checker = VibeChecker()
# --- SIDEBAR UI ---
with st.sidebar:
    st.header("🧠 Diagnostic Inputs")
    mood = st.selectbox("How are you feeling?", ["Happy/Light", "Sad/Emotional", "Tense/Angry", "Curious/Bored"])
    energy = st.select_slider("Energy Level", options=["Low (Chill)", "Medium (Engaging)", "High (Adrenaline)"])
    company = st.radio("Who's watching?", ["Just Me", "Date Night", "Family/Kids"])
    era = st.selectbox("Era Preference", ["Any", "Modern (2010+)", "Classic (Pre-2000)"])
    
    if st.button("🔍 Find Movies", type="primary"):
        # Reset State
        st.session_state.current_index = 0
        params = build_smart_query(mood, energy, company, era)
        results = fetch_movies(params)
        
        # Shuffle results to ensure variety, then store in session
        random.shuffle(results)
        st.session_state.movies = results

# --- MAIN UI ---
st.title("🍿 Moodie: Context-Aware Recommendations")

if not st.session_state.movies:
    st.info("👈 Use the sidebar to tell me about your mood, and I'll find the perfect movie.")
    st.write("### Why this is better:")
    st.write("* **It Listens:** Adapts genres based on who you are with.")
    st.write("* **It Remembers:** Rejects movies you've seen without restarting.")
else:
    # Get current movie based on index
    if st.session_state.current_index < len(st.session_state.movies):
        movie = st.session_state.movies[st.session_state.current_index]
        
        # Layout: 2 Columns (Poster | Details)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else "https://via.placeholder.com/500x750?text=No+Poster"
            st.image(poster_url, use_column_width=True)
            
        with col2:
            st.subheader(f"{movie['title']} ({movie['release_date'][:4]})")
            st.caption(f"⭐ Rating: {movie['vote_average']}/10  |  ❤️ Popularity: {int(movie['popularity'])}")
            
            # Smart Tagging
            if movie['vote_average'] > 8.0:
                st.markdown("`🔥 Masterpiece`")
            elif movie['popularity'] > 1000:
                st.markdown("`🌍 Global Hit`")
                
            st.write("### Plot Summary")
            st.write(movie['overview'])
            
            st.markdown("---")

            # --- NEW: THE SOCIAL VIBE CHECKER ---
            st.write("### 🗣️ Audience Vibe Check")
            if st.button("Deep Scan Reviews (AI)", key=f"scan_{movie['id']}"):
                with st.spinner(f"Scraping Letterboxd and running Gemini Analysis for '{movie['title']}'..."):
                    
                    vibe_report = vibe_checker.check_vibe(movie['title'])
                    
                    if "error" in vibe_report:
                        st.error(vibe_report["error"])
                    else:
                        st.success(f"**Primary Emotion:** {vibe_report.get('primary_emotion', 'N/A')}")
                        st.warning(f"**Warning:** {vibe_report.get('warning', 'None')}")
                        st.info(f"**Consensus:** {vibe_report.get('consensus', 'N/A')}")
            
            st.markdown("---")
            
            # ACTION BUTTONS
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ I'll Watch This!"):
                    st.success(f"Great choice! Enjoy **{movie['title']}**.")
                    st.balloons()
            with b2:
                if st.button("❌ Seen it / Skip"):
                    # Increment index to show next movie
                    st.session_state.current_index += 1
                    st.rerun() # Immediate refresh
                    
    else:
        st.warning("We've run out of recommendations for this filter! Try adjusting the sidebar inputs.")