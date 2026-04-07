import streamlit as st
import requests
import random
import pandas as pd
from vibe_checker import VibeChecker
from sematic_recommender import SemanticRecommender

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

def search_movie_tmdb(title, year):
    # Remove anything after and including '(' to improve TMDB search accuracy
    clean_title = title.split('(')[0].strip()
    
    params = {
        "api_key": API_KEY,
        "query": clean_title,
        "language": "en-US",
        "page": 1
    }
    if year:
        # Sometimes 'nan' can be passed
        if str(year).lower() != 'nan':
            params["primary_release_year"] = str(year)
            
    try:
        response = requests.get(f"{BASE_URL}/search/movie", params=params)
        data = response.json()
        results = data.get('results', [])
        if results:
            return results[0]
    except:
        pass
    return None

# --- STATE MANAGEMENT ---
# This makes the app "Smart" by remembering where you are
if 'movies' not in st.session_state:
    st.session_state.movies = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# 1. Initialize session state to track where the user is
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'

# Helper function to change pages
def navigate(view_name):
    st.session_state.current_view = view_name
    st.rerun() # Forces the app to instantly reload with the new view

@st.cache_resource
def get_vibe_checker():
    return VibeChecker()

@st.cache_resource
def get_semantic_recommender():
    return SemanticRecommender()

vibe_checker = get_vibe_checker()
semantic_recommender = get_semantic_recommender()

# --- VIEW 1: THE LANDING PAGE ---
def render_home():
    st.title("🍿 Moodie: What are we watching?")
    st.write("Choose how you want to find your next movie:")
    
    # Use columns to put the buttons side-by-side
    col1, col2 = st.columns(2)
    
    with col1:
        # use_container_width makes the buttons nice and large
        if st.button("🎛️ Set Mood via Knobs", use_container_width=True):
            navigate('knobs')
            
    with col2:
        if st.button("✍️ Type a Prompt", use_container_width=True):
            navigate('prompt')


# --- VIEW 2: THE KNOBS SCREEN ---
def render_knobs_screen():
    # Back button to return to home
    if st.button("⬅️ Back to Home"):
        navigate('home')
        
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

                # # --- NEW: THE SOCIAL VIBE CHECKER ---
                # st.write("### 🗣️ Audience Vibe Check")
                # if st.button("Deep Scan Reviews (AI)", key=f"scan_{movie['id']}"):
                #     with st.spinner(f"Scraping Letterboxd and running Gemini Analysis for '{movie['title']}'..."):
                        
                #         vibe_report = vibe_checker.check_vibe(movie['title'])
                        
                #         if "error" in vibe_report:
                #             st.error(vibe_report["error"])
                #         else:
                #             st.success(f"**Primary Emotion:** {vibe_report.get('primary_emotion', 'N/A')}")
                #             st.warning(f"**Warning:** {vibe_report.get('warning', 'None')}")
                #             st.info(f"**Consensus:** {vibe_report.get('consensus', 'N/A')}")
                
                # st.markdown("---")
                
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


# --- VIEW 3: THE PROMPT SCREEN ---
def render_prompt_screen():
    if st.button("⬅️ Back to Home"):
        navigate('home')
        
    st.header("✍️ Describe your Mood")
    
    user_prompt = st.text_area("How are you feeling? What kind of movie are you looking for?")
    
    if st.button("Get Recommendations", type="primary"):
        if user_prompt:
            with st.spinner("Finding the perfect movies..."):
                try:
                    recommendations = semantic_recommender.get_recommendations(user_prompt)
                    st.success("Here are your movies!")
                    
                    for index, row in recommendations.iterrows():
                        year = str(int(row['year'])) if pd.notna(row['year']) else ""
                        tmdb_movie = search_movie_tmdb(row['title'], year)
                        
                        if tmdb_movie:
                            # Layout: 2 Columns (Poster | Details)
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                poster_url = f"https://image.tmdb.org/t/p/w500{tmdb_movie['poster_path']}" if tmdb_movie.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster"
                                st.image(poster_url, use_column_width=True)
                                
                            with col2:
                                st.subheader(f"{tmdb_movie['title']} ({tmdb_movie.get('release_date', '')[:4]})")
                                st.caption(f"⭐ Rating: {tmdb_movie.get('vote_average', 0)}/10  |  ❤️ Popularity: {int(tmdb_movie.get('popularity', 0))}")
                                
                                # Smart Tagging
                                if tmdb_movie.get('vote_average', 0) > 8.0:
                                    st.markdown("`🔥 Masterpiece`")
                                elif tmdb_movie.get('popularity', 0) > 1000:
                                    st.markdown("`🌍 Global Hit`")
                                    
                                st.write("### Plot Summary")
                                st.write(tmdb_movie.get('overview', row.get('plot', 'No plot available.')))
                                
                                st.markdown("---")
                        else:
                            # Fallback if TMDB API doesn't find it
                            st.write(f"**{row.get('title', 'Unknown Title')}** ({year})")
                            st.write(row.get('plot', 'No plot available.'))
                            st.write("---")
                except Exception as e:
                    st.error(f"Error getting recommendations: {e}")
        else:
            st.warning("Please type a prompt first.")

# --- THE ROUTER ---
# This looks at the session state and decides which function to run
if st.session_state.current_view == 'home':
    render_home()
elif st.session_state.current_view == 'knobs':
    render_knobs_screen()
elif st.session_state.current_view == 'prompt':
    render_prompt_screen()