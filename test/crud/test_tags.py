"""
Integration tests for Tag CRUD endpoints
"""
import pytest


class TestTagEndpoints:
    """Test suite for /tags endpoints"""

    def test_get_tags_list_returns_correct_count(self, client, sample_tags):
        """Test GET /tags returns all tags from fixtures"""
        # Given: 5 tags exist in the database

        # When: Requesting all tags
        response = client.get("/tags")

        # Then: Should return 200 and all 5 tags
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert isinstance(data, list)

    def test_get_tags_with_custom_limit(self, client, sample_tags):
        """Test GET /tags with custom limit parameter"""
        # Given: 5 tags exist in the database

        # When: Requesting tags with limit=3
        response = client.get("/tags?limit=3")

        # Then: Should return only 3 tags
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_tag_by_id_returns_correct_tag(self, client, sample_tags):
        """Test GET /tags/{tag_id} returns specific tag"""
        # Given: Multiple tags exist, get the first one's ID
        tag_id = sample_tags[0].id

        # When: Requesting tag by ID
        response = client.get(f"/tags/{tag_id}")

        # Then: Should return 200 and the correct tag
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tag_id
        assert data["user_id"] == 1
        assert data["movie_id"] == 1
        assert data["tag"] == "mind-bending"
        assert data["timestamp"] == 1609459200

    def test_get_tag_by_nonexistent_id_returns_404(self, client, sample_tags):
        """Test GET /tags/{tag_id} with non-existent ID returns 404"""
        # Given: Tag with ID 99999 does not exist

        # When: Requesting non-existent tag
        response = client.get("/tags/99999")

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Tag not found"

    def test_create_tag_adds_to_database(self, client, sample_movies, db_session):
        """Test POST /tags creates new tag in database"""
        # Given: New tag data
        new_tag = {
            "user_id": 5,
            "movie_id": 1,
            "tag": "awesome",
            "timestamp": 1609460000
        }

        # When: Creating a new tag
        response = client.post("/tags", json=new_tag)

        # Then: Should return 201 Created
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == 5
        assert data["movie_id"] == 1
        assert data["tag"] == "awesome"
        assert data["timestamp"] == 1609460000
        assert "id" in data

        # Verify tag was actually added to database
        tag_id = data["id"]
        verify_response = client.get(f"/tags/{tag_id}")
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["tag"] == "awesome"

    def test_create_tag_with_spaces(self, client, sample_movies):
        """Test POST /tags with tag containing spaces"""
        # Given: Tag data with spaces
        new_tag = {
            "user_id": 6,
            "movie_id": 1,
            "tag": "must watch",
            "timestamp": 1609460100
        }

        # When: Creating the tag
        response = client.post("/tags", json=new_tag)

        # Then: Should return 201 Created
        assert response.status_code == 201
        data = response.json()
        assert data["tag"] == "must watch"

    def test_create_multiple_tags_for_same_movie(self, client, sample_movies):
        """Test creating multiple tags for the same movie by same user"""
        # Given: A movie exists

        # When: User creates multiple tags for same movie
        tag1 = client.post("/tags", json={
            "user_id": 10,
            "movie_id": 1,
            "tag": "exciting",
            "timestamp": 1609460000
        })
        tag2 = client.post("/tags", json={
            "user_id": 10,
            "movie_id": 1,
            "tag": "thrilling",
            "timestamp": 1609460100
        })

        # Then: Both tags should be created successfully
        assert tag1.status_code == 201
        assert tag2.status_code == 201
        assert tag1.json()["id"] != tag2.json()["id"]
        assert tag1.json()["tag"] == "exciting"
        assert tag2.json()["tag"] == "thrilling"

    def test_update_tag_modifies_database(self, client, single_tag):
        """Test PUT /tags/{tag_id} updates tag in database"""
        # Given: Tag exists
        tag_id = single_tag.id

        # When: Updating the tag
        update_data = {
            "tag": "updated-tag",
            "timestamp": 1609470000
        }
        response = client.put(f"/tags/{tag_id}", json=update_data)

        # Then: Should return 200 and updated data
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tag_id
        assert data["tag"] == "updated-tag"
        assert data["timestamp"] == 1609470000

        # Verify update persisted in database
        verify_response = client.get(f"/tags/{tag_id}")
        verify_data = verify_response.json()
        assert verify_data["tag"] == "updated-tag"
        assert verify_data["timestamp"] == 1609470000

    def test_update_tag_partial_update(self, client, single_tag):
        """Test PUT /tags/{tag_id} with partial data"""
        # Given: Tag exists
        tag_id = single_tag.id
        original_timestamp = single_tag.timestamp

        # When: Updating only the tag text
        update_data = {"tag": "partially-updated"}
        response = client.put(f"/tags/{tag_id}", json=update_data)

        # Then: Should update tag but keep original timestamp
        assert response.status_code == 200
        data = response.json()
        assert data["tag"] == "partially-updated"
        assert data["timestamp"] == original_timestamp

    def test_update_nonexistent_tag_returns_404(self, client):
        """Test PUT /tags/{tag_id} with non-existent ID returns 404"""
        # Given: Tag with ID 99999 does not exist

        # When: Attempting to update non-existent tag
        update_data = {"tag": "new-tag"}
        response = client.put("/tags/99999", json=update_data)

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Tag not found"

    def test_delete_tag_removes_from_database(self, client, single_tag):
        """Test DELETE /tags/{tag_id} removes tag from database"""
        # Given: Tag exists
        tag_id = single_tag.id

        # Verify tag exists
        verify_before = client.get(f"/tags/{tag_id}")
        assert verify_before.status_code == 200

        # When: Deleting the tag
        response = client.delete(f"/tags/{tag_id}")

        # Then: Should return 204 No Content
        assert response.status_code == 204

        # Verify tag no longer exists in database
        verify_after = client.get(f"/tags/{tag_id}")
        assert verify_after.status_code == 404

    def test_delete_nonexistent_tag_returns_404(self, client):
        """Test DELETE /tags/{tag_id} with non-existent ID returns 404"""
        # Given: Tag with ID 99999 does not exist

        # When: Attempting to delete non-existent tag
        response = client.delete("/tags/99999")

        # Then: Should return 404 Not Found
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Tag not found"

    def test_get_empty_tags_list(self, client):
        """Test GET /tags returns empty list when no tags exist"""
        # Given: No tags in database

        # When: Requesting all tags
        response = client.get("/tags")

        # Then: Should return 200 with empty list
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert isinstance(data, list)

    def test_different_users_can_tag_same_movie(self, client, sample_movies):
        """Test that different users can tag the same movie"""
        # Given: A movie exists

        # When: Different users tag the same movie
        tag1 = client.post("/tags", json={
            "user_id": 20,
            "movie_id": 1,
            "tag": "user20-tag",
            "timestamp": 1609460000
        })
        tag2 = client.post("/tags", json={
            "user_id": 21,
            "movie_id": 1,
            "tag": "user21-tag",
            "timestamp": 1609460100
        })

        # Then: Both tags should be created successfully
        assert tag1.status_code == 201
        assert tag2.status_code == 201
        assert tag1.json()["user_id"] == 20
        assert tag2.json()["user_id"] == 21

    def test_tag_text_preserves_case(self, client, sample_movies):
        """Test that tag text case is preserved"""
        # Given: Tag with mixed case
        new_tag = {
            "user_id": 30,
            "movie_id": 1,
            "tag": "Must-Watch-Movie",
            "timestamp": 1609460000
        }

        # When: Creating the tag
        response = client.post("/tags", json=new_tag)

        # Then: Case should be preserved
        assert response.status_code == 201
        data = response.json()
        assert data["tag"] == "Must-Watch-Movie"
