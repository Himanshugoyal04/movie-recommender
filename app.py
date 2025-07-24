import pickle
import streamlit as st
import time
import random
import requests



def fetch_movie_details(movie_id, retries=3):
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    api_key = "c62b507ff0a0cec827df7e06c7f6f634"

    for i in range(retries):
        try:
            response = requests.get(f"{base_url}?api_key={api_key}", timeout=5)
            response.raise_for_status()
            data = response.json()

            poster_path = data.get('poster_path')
            overview = data.get('overview', 'No overview available.')
            genres = [genre['name'] for genre in data.get('genres', [])]
            rating = data.get('vote_average', 'N/A')
            poster_url = "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Poster"

            # Get trailer link
            trailer_url = get_trailer_link(movie_id, api_key)

            return poster_url, overview, genres, rating, trailer_url
        except requests.exceptions.RequestException as e:
            wait = (2 ** i) + random.random()
            print(f"[RETRY {i + 1}] Failed to fetch movie_id={movie_id}: {e}. Retrying in {wait:.2f}s...")
            time.sleep(wait)

    return "https://via.placeholder.com/500x750?text=Error", "Overview fetch error", [], "N/A", None



def get_trailer_link(movie_id, api_key):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}")
        data = response.json()
        for video in data.get('results', []):
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                return f"https://www.youtube.com/watch?v={video['key']}"
    except:
        pass
    return None



def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_posters = []
    recommended_overviews = []
    recommended_genres = []
    recommended_ratings = []
    recommended_trailers = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        time.sleep(1)
        poster, overview, genres, rating, trailer = fetch_movie_details(movie_id)

        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_posters.append(poster)
        recommended_overviews.append(overview)
        recommended_genres.append(genres)
        recommended_ratings.append(rating)
        recommended_trailers.append(trailer)

    return recommended_movie_names, recommended_posters, recommended_overviews, recommended_genres, recommended_ratings, recommended_trailers


# --- Streamlit UI ---
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Type or select a movie from the dropdown", movie_list)

if st.button('🔍 Show Recommendation'):
    names, posters, overviews, genres_list, ratings, trailers = recommend(selected_movie)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i])
            st.subheader(names[i])
            st.markdown(f"⭐ **Rating:** {ratings[i]}/10")
            st.markdown("**Genres:** " + ", ".join(genres_list[i]) if genres_list[i] else "_No genre info_")
            st.caption(overviews[i])
            if trailers[i]:
                st.markdown(f"[▶ Watch Trailer](https://www.youtube.com/watch?v={trailers[i].split('=')[-1]})",
                            unsafe_allow_html=True)
