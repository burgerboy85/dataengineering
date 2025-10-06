import csv
import random
import string
import os

# Configuration
OUTPUT_FILE = "/Users/rahulchakraborty/Documents/Study/Data_Engineering/my_project/data/hollywood_movies_latest.csv"
TARGET_SIZE = 1 * 1024 * 1024   # 1 GB in bytes
FIELDNAMES = [
    "movie_id", "title", "genre", "director", "actors",
    "release_year", "duration_minutes", "rating", "box_office_millions", "production_company"
]

GENRES = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Adventure", "Animation"]
DIRECTORS = ["Steven Spielberg", "Christopher Nolan", "Quentin Tarantino", "James Cameron", "Martin Scorsese"]
ACTORS = ["Tom Hanks", "Scarlett Johansson", "Leonardo DiCaprio", "Denzel Washington", "Jennifer Lawrence"]
PRODUCTION_COMPANIES = ["Warner Bros", "Universal", "20th Century Studios", "Paramount", "Netflix Originals"]

def random_title() -> str:
    """
    Generate a random movie title.

    Returns:
        str: A pseudo-random movie title.
    """
    return "The " + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=random.randint(5, 15)))

def random_actors() -> str:
    """
    Generate a random selection of actors.

    Returns:
        str: A comma-separated string of 2 to 3 actor names.
    """
    return ", ".join(random.sample(ACTORS, k=random.randint(2, 3)))

def generate_row(movie_id: int) -> dict:
    """
    Generate a dictionary representing a row of movie data.

    Args:
        movie_id (int): The unique ID of the movie.

    Returns:
        dict: A dictionary with fields matching FIELDNAMES.
    """
    return {
        "movie_id": movie_id,
        "title": random_title(),
        "genre": random.choice(GENRES),
        "director": random.choice(DIRECTORS),
        "actors": random_actors(),
        "release_year": random.randint(1980, 2024),
        "duration_minutes": random.randint(80, 180),
        "rating": round(random.uniform(1.0, 10.0), 1),
        "box_office_millions": round(random.uniform(10, 1000), 2),
        "production_company": random.choice(PRODUCTION_COMPANIES)
    }

def write_large_csv(file_path: str, target_size_bytes: int) -> None:
    """
    Write a CSV file with synthetic movie data until the file size reaches the specified target.

    Args:
        file_path (str): Path to the output CSV file.
        target_size_bytes (int): Target size of the CSV file in bytes.

    Returns:
        None
    """
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        bytes_written = f.tell()
        movie_id = 1

        while bytes_written < target_size_bytes:
            row = generate_row(movie_id)
            writer.writerow(row)
            movie_id += 1
            bytes_written = f.tell()
            if movie_id % 10000 == 0:
                print(f"{bytes_written / (1024*1024):.2f} MB written...")

    print(f"Done. {movie_id - 1} rows written. Final size: {os.path.getsize(file_path) / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    """
    Entry point of the script. Generates a 1 GB CSV file with Hollywood movie data.
    """
    write_large_csv(OUTPUT_FILE, TARGET_SIZE)
