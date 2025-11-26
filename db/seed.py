"""
Database seeding script for both movie data and initial users.
Run this script to populate the database with sample data.

Usage:
    python -m db.seed              # Seed only if database is empty
    python -m db.seed --force      # Drop and recreate all data
    python -m db.seed --users-only # Only create initial users
"""
from __future__ import annotations
import os
import csv
import sys
from typing import Iterable, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from db import engine, DB_DIR, SessionLocal, Base
from model.movie import Movie
from model.link import Link
from model.rating import Rating
from model.tag import Tag
from dao import UserDAO


def chunked(iterable: Iterable, size: int) -> Iterable[List]:
    """Split an iterable into chunks of specified size."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def create_schema():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def seed_movies(session: Session, csv_path: str, batch_size: int = 5000):
    """Seed movies from CSV file."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = (
            Movie(
                movie_id=int(row['movieId']),
                title=row['title'],
                genres=row['genres'] or "",
            )
            for row in reader
        )
        for batch in chunked(rows, batch_size):
            session.add_all(batch)
            session.commit()


def seed_links(session: Session, csv_path: str, batch_size: int = 5000):
    """Seed links from CSV file."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = (
            Link(
                movie_id=int(row['movieId']),
                imdb_id=row.get('imdbId') or '',
                tmdb_id=(row.get('tmdbId') or None),
            )
            for row in reader
        )
        for batch in chunked(rows, batch_size):
            session.add_all(batch)
            session.commit()


def seed_ratings(session: Session, csv_path: str, batch_size: int = 10000):
    """Seed ratings from CSV file."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = (
            Rating(
                user_id=int(row['userId']),
                movie_id=int(row['movieId']),
                rating=float(row['rating']),
                timestamp=int(row['timestamp']),
            )
            for row in reader
        )
        for batch in chunked(rows, batch_size):
            session.add_all(batch)
            session.commit()


def seed_tags(session: Session, csv_path: str, batch_size: int = 10000):
    """Seed tags from CSV file."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = (
            Tag(
                user_id=int(row['userId']),
                movie_id=int(row['movieId']),
                tag=row['tag'],
                timestamp=int(row['timestamp']),
            )
            for row in reader
        )
        for batch in chunked(rows, batch_size):
            session.add_all(batch)
            session.commit()


def seed_initial_users(session: Session):
    """Create initial admin and regular users."""
    print("Creating initial users...")

    # Create admin user
    existing_admin = UserDAO.get_by_username(session, "admin")
    if not existing_admin:
        UserDAO.create_user(
            db=session,
            username="admin",
            email="admin@example.com",
            password="admin123",
            roles=["ROLE_ADMIN", "ROLE_USER"]
        )
        print("  ✓ Admin user created (username: admin, password: admin123)")
    else:
        print("  - Admin user already exists")

    # Create regular user
    existing_user = UserDAO.get_by_username(session, "user")
    if not existing_user:
        UserDAO.create_user(
            db=session,
            username="user",
            email="user@example.com",
            password="user123",
            roles=["ROLE_USER"]
        )
        print("  ✓ Regular user created (username: user, password: user123)")
    else:
        print("  - Regular user already exists")


def seed_movie_data(session: Session, force: bool = False):
    """Seed all movie-related data from CSV files."""
    # Check if movie data already exists
    existing = session.scalar(select(Movie).limit(1))
    if existing and not force:
        print("Database already has movie data; skipping movie seeding.")
        return False

    movies_csv = os.path.join(DB_DIR, 'movies.csv')
    links_csv = os.path.join(DB_DIR, 'links.csv')
    ratings_csv = os.path.join(DB_DIR, 'ratings.csv')
    tags_csv = os.path.join(DB_DIR, 'tags.csv')

    # Check if CSV files exist
    if not all(os.path.exists(f) for f in [movies_csv, links_csv, ratings_csv, tags_csv]):
        print("Warning: CSV files not found in db/resources/. Skipping movie data seeding.")
        return False

    print("Seeding movie data...")
    print("  Seeding movies...")
    seed_movies(session, movies_csv)
    print("  Seeding links...")
    seed_links(session, links_csv)
    print("  Seeding ratings...")
    seed_ratings(session, ratings_csv)
    print("  Seeding tags...")
    seed_tags(session, tags_csv)
    print("  ✓ Movie data seeded successfully")
    return True


def main(force: bool = False, users_only: bool = False):
    """Main seeding function."""
    print("=" * 50)
    print("Database Seeding")
    print("=" * 50)

    # Create schema
    print("Creating database schema...")
    create_schema()
    print("  ✓ Schema created")

    if force:
        print("\n⚠ Force mode enabled - dropping all existing data!")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        # Seed users
        print()
        seed_initial_users(session)

        # Seed movie data (unless users-only mode)
        if not users_only:
            print()
            seed_movie_data(session, force=force)

    print()
    print("=" * 50)
    print("Seeding completed!")
    print("=" * 50)


if __name__ == "__main__":
    force = "--force" in sys.argv
    users_only = "--users-only" in sys.argv

    try:
        main(force=force, users_only=users_only)
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
