"""
Integration tests for Movie CRUD endpoints
"""
import pytest


class TestMovieEndpoints:
    """Test suite for /movies endpoints"""

    def test_get_movies_list_returns_correct_count(self, client, sample_movies, auth_headers):
        """Test GET /movies returns all movies from fixtures"""
        # Given: 3 movies exist in the database (from sample_movies fixture)

        # When: Requesting all movies with authentication
        response = client.get("/movies", headers=auth_headers)

        # Then: Should return 200 and all 3 movies
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert isinstance(data, list)

        # Verify movie structure
        movie_ids = [movie["movie_id"] for movie in data]
        assert 1 in movie_ids
        assert 2 in movie_ids
        assert 3 in movie_ids

    def test_get_movies_with_limit(self, client, sample_movies, auth_headers):
        """Test GET /movies with limit parameter"""
        # Given: 3 movies exist in the database

        # When: Requesting movies with limit=2
        response = client.get("/movies?limit=2", headers=auth_headers)

        # Then: Should return only 2 movies
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_movie_by_id_returns_correct_movie(self, client, sample_movies, auth_headers):
        """Test GET /movies/{movie_id} returns specific movie"""
        # Given: Movie with ID 1 exists in database

        # When: Requesting movie by ID
        response = client.get("/movies/1", headers=auth_headers)

        # Then: Should return 200 and the correct movie
        assert response.status_code == 200
        data = response.json()
        assert data["movie_id"] == 1
        assert data["title"] == "The Matrix"
        assert data["genres"] == "Action|Sci-Fi"

    def test_get_movie_by_nonexistent_id_returns_404(self, client, sample_movies, auth_headers):
        """Test GET /movies/{movie_id} with non-existent ID returns 404"""
        # Given: Movie with ID 9999 does not exist

        # When: Requesting non-existent movie
        response = client.get("/movies/9999", headers=auth_headers)

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Movie not found"

    def test_get_movies_without_auth_returns_401(self, client, sample_movies):
        """Test GET /movies without authentication returns 401"""
        # Given: Movies exist but no auth token provided

        # When: Requesting movies without authentication
        response = client.get("/movies")

        # Then: Should return 401 Unauthorized
        assert response.status_code == 401

    def test_create_movie_adds_to_database(self, client, db_session, auth_headers):
        """Test POST /movies creates new movie in database"""
        # Given: New movie data
        new_movie = {
            "movie_id": 500,
            "title": "New Test Movie",
            "genres": "Comedy|Romance"
        }

        # When: Creating a new movie
        response = client.post("/movies", json=new_movie, headers=auth_headers)

        # Then: Should return 201 Created
        assert response.status_code == 201
        data = response.json()
        assert data["movie_id"] == 500
        assert data["title"] == "New Test Movie"
        assert data["genres"] == "Comedy|Romance"

        # Verify movie was actually added to database
        verify_response = client.get("/movies/500", headers=auth_headers)
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["movie_id"] == 500

    def test_create_movie_with_duplicate_id_returns_400(self, client, sample_movies, auth_headers):
        """Test POST /movies with duplicate ID returns 400"""
        # Given: Movie with ID 1 already exists

        # When: Attempting to create movie with same ID
        duplicate_movie = {
            "movie_id": 1,
            "title": "Duplicate Movie",
            "genres": "Drama"
        }
        response = client.post("/movies", json=duplicate_movie, headers=auth_headers)

        # Then: Should return 400 Bad Request
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    def test_update_movie_modifies_database(self, client, single_movie, db_session, auth_headers):
        """Test PUT /movies/{movie_id} updates movie in database"""
        # Given: Movie with ID 100 exists
        movie_id = single_movie.movie_id

        # When: Updating the movie
        update_data = {
            "title": "Updated Movie Title",
            "genres": "Action|Adventure"
        }
        response = client.put(f"/movies/{movie_id}", json=update_data, headers=auth_headers)

        # Then: Should return 200 and updated data
        assert response.status_code == 200
        data = response.json()
        assert data["movie_id"] == movie_id
        assert data["title"] == "Updated Movie Title"
        assert data["genres"] == "Action|Adventure"

        # Verify update persisted in database
        verify_response = client.get(f"/movies/{movie_id}", headers=auth_headers)
        verify_data = verify_response.json()
        assert verify_data["title"] == "Updated Movie Title"
        assert verify_data["genres"] == "Action|Adventure"

    def test_update_movie_partial_update(self, client, single_movie, auth_headers):
        """Test PUT /movies/{movie_id} with partial data"""
        # Given: Movie with ID 100 exists
        movie_id = single_movie.movie_id
        original_genres = single_movie.genres

        # When: Updating only the title
        update_data = {"title": "Only Title Updated"}
        response = client.put(f"/movies/{movie_id}", json=update_data, headers=auth_headers)

        # Then: Should update title but keep original genres
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Updated"
        assert data["genres"] == original_genres

    def test_update_nonexistent_movie_returns_404(self, client, auth_headers):
        """Test PUT /movies/{movie_id} with non-existent ID returns 404"""
        # Given: Movie with ID 9999 does not exist

        # When: Attempting to update non-existent movie
        update_data = {"title": "Updated Title"}
        response = client.put("/movies/9999", json=update_data, headers=auth_headers)

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Movie not found"

    def test_delete_movie_removes_from_database(self, client, single_movie, auth_headers):
        """Test DELETE /movies/{movie_id} removes movie from database"""
        # Given: Movie with ID 100 exists
        movie_id = single_movie.movie_id

        # Verify movie exists
        verify_before = client.get(f"/movies/{movie_id}", headers=auth_headers)
        assert verify_before.status_code == 200

        # When: Deleting the movie
        response = client.delete(f"/movies/{movie_id}", headers=auth_headers)

        # Then: Should return 204 No Content
        assert response.status_code == 204

        # Verify movie no longer exists in database
        verify_after = client.get(f"/movies/{movie_id}", headers=auth_headers)
        assert verify_after.status_code == 404

    def test_delete_nonexistent_movie_returns_404(self, client, auth_headers):
        """Test DELETE /movies/{movie_id} with non-existent ID returns 404"""
        # Given: Movie with ID 9999 does not exist

        # When: Attempting to delete non-existent movie
        response = client.delete("/movies/9999", headers=auth_headers)

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Movie not found"

    def test_get_empty_movies_list(self, client, auth_headers):
        """Test GET /movies returns empty list when no movies exist"""
        # Given: No movies in database

        # When: Requesting all movies
        response = client.get("/movies", headers=auth_headers)

        # Then: Should return 200 with empty list
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert isinstance(data, list)
