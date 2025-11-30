"""
Integration tests for Link CRUD endpoints
"""
import pytest


class TestLinkEndpoints:
    """Test suite for /links endpoints"""

    def test_get_links_list_returns_correct_count(self, client, sample_links):
        """Test GET /links returns all links from fixtures"""
        # Given: 3 links exist in the database

        # When: Requesting all links
        response = client.get("/links")

        # Then: Should return 200 and all 3 links
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert isinstance(data, list)

        # Verify link structure
        movie_ids = [link["movie_id"] for link in data]
        assert 1 in movie_ids
        assert 2 in movie_ids
        assert 3 in movie_ids

    def test_get_links_with_limit(self, client, sample_links):
        """Test GET /links with limit parameter"""
        # Given: 3 links exist in the database

        # When: Requesting links with limit=2
        response = client.get("/links?limit=2")

        # Then: Should return only 2 links
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_link_by_movie_id_returns_correct_link(self, client, sample_links):
        """Test GET /links/{movie_id} returns specific link"""
        # Given: Link for movie_id 1 exists

        # When: Requesting link by movie ID
        response = client.get("/links/1")

        # Then: Should return 200 and the correct link
        assert response.status_code == 200
        data = response.json()
        assert data["movie_id"] == 1
        assert data["imdb_id"] == "tt0133093"
        assert data["tmdb_id"] == "603"

    def test_get_link_by_nonexistent_movie_id_returns_404(self, client, sample_links):
        """Test GET /links/{movie_id} with non-existent ID returns 404"""
        # Given: Link for movie_id 9999 does not exist

        # When: Requesting non-existent link
        response = client.get("/links/9999")

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Link not found"

    def test_create_link_adds_to_database(self, client, sample_movies, db_session):
        """Test POST /links creates new link in database"""
        # Given: New link data for existing movie
        new_link = {
            "movie_id": 1,
            "imdb_id": "tt1234567",
            "tmdb_id": "12345"
        }

        # When: Creating a new link
        response = client.post("/links", json=new_link)

        # Then: Should return 201 Created
        assert response.status_code == 201
        data = response.json()
        assert data["movie_id"] == 1
        assert data["imdb_id"] == "tt1234567"
        assert data["tmdb_id"] == "12345"

        # Verify link was actually added to database
        verify_response = client.get("/links/1")
        assert verify_response.status_code == 200

    def test_create_link_without_tmdb_id(self, client, sample_movies):
        """Test POST /links with optional tmdb_id"""
        # Given: New link data without tmdb_id
        new_link = {
            "movie_id": 2,
            "imdb_id": "tt9876543"
        }

        # When: Creating a new link
        response = client.post("/links", json=new_link)

        # Then: Should return 201 Created
        assert response.status_code == 201
        data = response.json()
        assert data["movie_id"] == 2
        assert data["imdb_id"] == "tt9876543"
        assert data["tmdb_id"] is None

    def test_create_link_with_duplicate_movie_id_returns_400(self, client, sample_links):
        """Test POST /links with duplicate movie_id returns 400"""
        # Given: Link for movie_id 1 already exists

        # When: Attempting to create another link for same movie
        duplicate_link = {
            "movie_id": 1,
            "imdb_id": "tt9999999",
            "tmdb_id": "99999"
        }
        response = client.post("/links", json=duplicate_link)

        # Then: Should return 400 Bad Request
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    def test_update_link_modifies_database(self, client, single_link):
        """Test PUT /links/{movie_id} updates link in database"""
        # Given: Link for movie_id 100 exists
        movie_id = single_link.movie_id

        # When: Updating the link
        update_data = {
            "imdb_id": "tt1111111",
            "tmdb_id": "11111"
        }
        response = client.put(f"/links/{movie_id}", json=update_data)

        # Then: Should return 200 and updated data
        assert response.status_code == 200
        data = response.json()
        assert data["movie_id"] == movie_id
        assert data["imdb_id"] == "tt1111111"
        assert data["tmdb_id"] == "11111"

        # Verify update persisted in database
        verify_response = client.get(f"/links/{movie_id}")
        verify_data = verify_response.json()
        assert verify_data["imdb_id"] == "tt1111111"
        assert verify_data["tmdb_id"] == "11111"

    def test_update_link_partial_update(self, client, single_link):
        """Test PUT /links/{movie_id} with partial data"""
        # Given: Link for movie_id 100 exists
        movie_id = single_link.movie_id
        original_tmdb = single_link.tmdb_id

        # When: Updating only the imdb_id
        update_data = {"imdb_id": "tt2222222"}
        response = client.put(f"/links/{movie_id}", json=update_data)

        # Then: Should update imdb_id but keep original tmdb_id
        assert response.status_code == 200
        data = response.json()
        assert data["imdb_id"] == "tt2222222"
        assert data["tmdb_id"] == original_tmdb

    def test_update_nonexistent_link_returns_404(self, client):
        """Test PUT /links/{movie_id} with non-existent ID returns 404"""
        # Given: Link for movie_id 9999 does not exist

        # When: Attempting to update non-existent link
        update_data = {"imdb_id": "tt9999999"}
        response = client.put("/links/9999", json=update_data)

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Link not found"

    def test_delete_link_removes_from_database(self, client, single_link):
        """Test DELETE /links/{movie_id} removes link from database"""
        # Given: Link for movie_id 100 exists
        movie_id = single_link.movie_id

        # Verify link exists
        verify_before = client.get(f"/links/{movie_id}")
        assert verify_before.status_code == 200

        # When: Deleting the link
        response = client.delete(f"/links/{movie_id}")

        # Then: Should return 204 No Content
        assert response.status_code == 204

        # Verify link no longer exists in database
        verify_after = client.get(f"/links/{movie_id}")
        assert verify_after.status_code == 404

    def test_delete_nonexistent_link_returns_404(self, client):
        """Test DELETE /links/{movie_id} with non-existent ID returns 404"""
        # Given: Link for movie_id 9999 does not exist

        # When: Attempting to delete non-existent link
        response = client.delete("/links/9999")

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Link not found"

    def test_get_empty_links_list(self, client):
        """Test GET /links returns empty list when no links exist"""
        # Given: No links in database

        # When: Requesting all links
        response = client.get("/links")

        # Then: Should return 200 with empty list
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert isinstance(data, list)
