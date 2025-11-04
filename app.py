from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random

app = Flask(__name__)

# Sample movie data
movies_db = {
    '1': {
        'id': '1',
        'title': 'The Shawshank Redemption',
        'year': 1994,
        'genre': 'Drama',
        'poster': 'https://via.placeholder.com/300x450/667eea/ffffff?text=Shawshank',
        'description': 'Two imprisoned men bond over years, finding redemption through acts of common decency.',
        'ratings': [],
        'reviews': []
    },
    '2': {
        'id': '2',
        'title': 'The Godfather',
        'year': 1972,
        'genre': 'Crime',
        'poster': 'https://via.placeholder.com/300x450/764ba2/ffffff?text=Godfather',
        'description': 'The aging patriarch of an organized crime dynasty transfers control to his reluctant son.',
        'ratings': [],
        'reviews': []
    },
    '3': {
        'id': '3',
        'title': 'The Dark Knight',
        'year': 2008,
        'genre': 'Action',
        'poster': 'https://via.placeholder.com/300x450/f093fb/ffffff?text=Dark+Knight',
        'description': 'Batman faces the Joker, a criminal mastermind who wants to plunge Gotham into anarchy.',
        'ratings': [],
        'reviews': []
    },
    '4': {
        'id': '4',
        'title': 'Pulp Fiction',
        'year': 1994,
        'genre': 'Crime',
        'poster': 'https://via.placeholder.com/300x450/4facfe/ffffff?text=Pulp+Fiction',
        'description': 'The lives of two mob hitmen, a boxer, and a pair of diner bandits intertwine.',
        'ratings': [],
        'reviews': []
    },
    '5': {
        'id': '5',
        'title': 'Forrest Gump',
        'year': 1994,
        'genre': 'Drama',
        'poster': 'https://via.placeholder.com/300x450/00f2fe/ffffff?text=Forrest+Gump',
        'description': 'The presidencies of Kennedy and Johnson unfold through the perspective of an Alabama man.',
        'ratings': [],
        'reviews': []
    },
    '6': {
        'id': '6',
        'title': 'Inception',
        'year': 2010,
        'genre': 'Sci-Fi',
        'poster': 'https://via.placeholder.com/300x450/43e97b/ffffff?text=Inception',
        'description': 'A thief who steals corporate secrets through dream-sharing technology.',
        'ratings': [],
        'reviews': []
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Get all movies with calculated average ratings"""
    movies_with_ratings = []
    
    for movie_id, movie in movies_db.items():
        movie_copy = movie.copy()
        
        # Calculate average rating
        if movie['ratings']:
            avg_rating = sum(movie['ratings']) / len(movie['ratings'])
            movie_copy['average_rating'] = round(avg_rating, 1)
            movie_copy['total_ratings'] = len(movie['ratings'])
        else:
            movie_copy['average_rating'] = 0
            movie_copy['total_ratings'] = 0
        
        movie_copy['total_reviews'] = len(movie['reviews'])
        movies_with_ratings.append(movie_copy)
    
    # Sort by average rating (highest first)
    movies_with_ratings.sort(key=lambda x: x['average_rating'], reverse=True)
    
    return jsonify({'movies': movies_with_ratings})

@app.route('/api/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Get single movie details"""
    if movie_id not in movies_db:
        return jsonify({'error': 'Movie not found'}), 404
    
    movie = movies_db[movie_id].copy()
    
    # Calculate average rating
    if movie['ratings']:
        movie['average_rating'] = round(sum(movie['ratings']) / len(movie['ratings']), 1)
        movie['total_ratings'] = len(movie['ratings'])
    else:
        movie['average_rating'] = 0
        movie['total_ratings'] = 0
    
    return jsonify({'movie': movie})

@app.route('/api/movies/<movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    """Add a rating to a movie"""
    if movie_id not in movies_db:
        return jsonify({'error': 'Movie not found'}), 404
    
    data = request.json
    rating = data.get('rating')
    
    if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    movies_db[movie_id]['ratings'].append(rating)
    
    # Calculate new average
    avg_rating = sum(movies_db[movie_id]['ratings']) / len(movies_db[movie_id]['ratings'])
    
    return jsonify({
        'success': True,
        'average_rating': round(avg_rating, 1),
        'total_ratings': len(movies_db[movie_id]['ratings'])
    })

@app.route('/api/movies/<movie_id>/review', methods=['POST'])
def add_review(movie_id):
    """Add a review to a movie"""
    if movie_id not in movies_db:
        return jsonify({'error': 'Movie not found'}), 404
    
    data = request.json
    reviewer_name = data.get('name', 'Anonymous')
    review_text = data.get('review')
    rating = data.get('rating')
    
    if not review_text or len(review_text.strip()) == 0:
        return jsonify({'error': 'Review text is required'}), 400
    
    if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    review = {
        'id': str(random.randint(1000, 9999)),
        'name': reviewer_name,
        'review': review_text,
        'rating': rating,
        'timestamp': datetime.now().isoformat()
    }
    
    movies_db[movie_id]['reviews'].append(review)
    movies_db[movie_id]['ratings'].append(rating)
    
    return jsonify({
        'success': True,
        'review': review,
        'total_reviews': len(movies_db[movie_id]['reviews'])
    })

@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    """Search movies by title"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'movies': []})
    
    results = []
    for movie in movies_db.values():
        if query in movie['title'].lower() or query in movie['genre'].lower():
            movie_copy = movie.copy()
            if movie['ratings']:
                movie_copy['average_rating'] = round(sum(movie['ratings']) / len(movie['ratings']), 1)
            else:
                movie_copy['average_rating'] = 0
            results.append(movie_copy)
    
    return jsonify({'movies': results})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
