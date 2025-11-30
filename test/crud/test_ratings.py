"""
Integration tests for Rating CRUD endpoints
"""
import pytest


class TestRatingEndpoints:
    """Test suite for /ratings endpoints"""

    def test_get_ratings_list_returns_correct_count(self, client, sample_ratings):
        """Test GET /ratings returns all ratings from fixtures"""
        # Given: 4 ratings exist in the database

        # When: Requesting all ratings
        response = client.get("/ratings")

        # Then: Should return 200 and all 4 ratings
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert isinstance(data, list)

    def test_get_ratings_with_custom_limit(self, client, sample_ratings):
        """Test GET /ratings with custom limit parameter"""
        # Given: 4 ratings exist in the database

        # When: Requesting ratings with limit=2
        response = client.get("/ratings?limit=2")

        # Then: Should return only 2 ratings
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_rating_by_id_returns_correct_rating(self, client, sample_ratings):
        """Test GET /ratings/{rating_id} returns specific rating"""
        # Given: Multiple ratings exist, get the first one's ID
        rating_id = sample_ratings[0].id

        # When: Requesting rating by ID
        response = client.get(f"/ratings/{rating_id}")

        # Then: Should return 200 and the correct rating
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == rating_id
        assert data["user_id"] == 1
        assert data["movie_id"] == 1
        assert data["rating"] == 5.0
        assert data["timestamp"] == 1609459200

    def test_get_rating_by_nonexistent_id_returns_404(self, client, sample_ratings):
        """Test GET /ratings/{rating_id} with non-existent ID returns 404"""
        # Given: Rating with ID 99999 does not exist

        # When: Requesting non-existent rating
        response = client.get("/ratings/99999")

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Rating not found"

    def test_create_rating_adds_to_database(self, client, sample_movies, db_session):
        """Test POST /ratings creates new rating in database"""
        # Given: New rating data
        new_rating = {
            "user_id": 5,
            "movie_id": 1,
            "rating": 4.5,
            "timestamp": 1609460000
        }

        # When: Creating a new rating
        response = client.post("/ratings", json=new_rating)

        # Then: Should return 201 Created
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == 5
        assert data["movie_id"] == 1
        assert data["rating"] == 4.5
        assert data["timestamp"] == 1609460000
        assert "id" in data

        # Verify rating was actually added to database
        rating_id = data["id"]
        verify_response = client.get(f"/ratings/{rating_id}")
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["rating"] == 4.5

    def test_create_rating_with_minimum_value(self, client, sample_movies):
        """Test POST /ratings with minimum rating value (0.5)"""
        # Given: Rating data with minimum value
        new_rating = {
            "user_id": 6,
            "movie_id": 1,
            "rating": 0.5,
            "timestamp": 1609460100
        }

        # When: Creating the rating
        response = client.post("/ratings", json=new_rating)

        # Then: Should return 201 Created
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 0.5

    def test_create_rating_with_maximum_value(self, client, sample_movies):
        """Test POST /ratings with maximum rating value (5.0)"""
        # Given: Rating data with maximum value
        new_rating = {
            "user_id": 7,
            "movie_id": 1,
            "rating": 5.0,
            "timestamp": 1609460200
        }

        # When: Creating the rating
        response = client.post("/ratings", json=new_rating)

        # Then: Should return 201 Created
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5.0

    def test_update_rating_modifies_database(self, client, single_rating):
        """Test PUT /ratings/{rating_id} updates rating in database"""
        # Given: Rating exists
        rating_id = single_rating.id

        # When: Updating the rating
        update_data = {
            "rating": 4.0,
            "timestamp": 1609470000
        }
        response = client.put(f"/ratings/{rating_id}", json=update_data)

        # Then: Should return 200 and updated data
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == rating_id
        assert data["rating"] == 4.0
        assert data["timestamp"] == 1609470000

        # Verify update persisted in database
        verify_response = client.get(f"/ratings/{rating_id}")
        verify_data = verify_response.json()
        assert verify_data["rating"] == 4.0
        assert verify_data["timestamp"] == 1609470000

    def test_update_rating_partial_update(self, client, single_rating):
        """Test PUT /ratings/{rating_id} with partial data"""
        # Given: Rating exists
        rating_id = single_rating.id
        original_timestamp = single_rating.timestamp

        # When: Updating only the rating value
        update_data = {"rating": 5.0}
        response = client.put(f"/ratings/{rating_id}", json=update_data)

        # Then: Should update rating but keep original timestamp
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5.0
        assert data["timestamp"] == original_timestamp

    def test_update_nonexistent_rating_returns_404(self, client):
        """Test PUT /ratings/{rating_id} with non-existent ID returns 404"""
        # Given: Rating with ID 99999 does not exist

        # When: Attempting to update non-existent rating
        update_data = {"rating": 3.0}
        response = client.put("/ratings/99999", json=update_data)

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Rating not found"

    def test_delete_rating_removes_from_database(self, client, single_rating):
        """Test DELETE /ratings/{rating_id} removes rating from database"""
        # Given: Rating exists
        rating_id = single_rating.id

        # Verify rating exists
        verify_before = client.get(f"/ratings/{rating_id}")
        assert verify_before.status_code == 200

        # When: Deleting the rating
        response = client.delete(f"/ratings/{rating_id}")

        # Then: Should return 204 No Content
        assert response.status_code == 204

        # Verify rating no longer exists in database
        verify_after = client.get(f"/ratings/{rating_id}")
        assert verify_after.status_code == 404

    def test_delete_nonexistent_rating_returns_404(self, client):
        """Test DELETE /ratings/{rating_id} with non-existent ID returns 404"""
        # Given: Rating with ID 99999 does not exist

        # When: Attempting to delete non-existent rating
        response = client.delete("/ratings/99999")

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Rating not found"

    def test_get_empty_ratings_list(self, client):
        """Test GET /ratings returns empty list when no ratings exist"""
        # Given: No ratings in database

        # When: Requesting all ratings
        response = client.get("/ratings")

        # Then: Should return 200 with empty list
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert isinstance(data, list)

    def test_multiple_users_can_rate_same_movie(self, client, sample_movies):
        """Test that multiple users can rate the same movie"""
        # Given: A movie exists

        # When: Multiple users rate the same movie
        rating1 = client.post("/ratings", json={
            "user_id": 10,
            "movie_id": 1,
            "rating": 4.5,
            "timestamp": 1609460000
        })
        rating2 = client.post("/ratings", json={
            "user_id": 11,
            "movie_id": 1,
            "rating": 3.5,
            "timestamp": 1609460100
        })

        # Then: Both ratings should be created successfully
        assert rating1.status_code == 201
        assert rating2.status_code == 201
        assert rating1.json()["id"] != rating2.json()["id"]
