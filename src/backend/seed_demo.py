from database import get_connection, init_db


DEMO_USERS = [
    {
        "email": "alex@example.com",
        "password_hash": "demo-not-for-login",
        "pets": [
            {"name": "Milo", "species": "Dog", "breed": "Corgi", "age_years": 3, "gender": "male"},
            {"name": "Luna", "species": "Cat", "breed": "Siamese", "age_years": 2, "gender": "female"},
        ],
    },
    {
        "email": "sam@example.com",
        "password_hash": "demo-not-for-login",
        "pets": [
            {"name": "Rocky", "species": "Dog", "breed": "Labrador", "age_years": 4, "gender": "male"},
            {"name": "Bella", "species": "Cat", "breed": "Tabby", "age_years": 1, "gender": "female"},
        ],
    },
]


def get_or_create_user(email: str, password_hash: str) -> int:
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (email,),
        ).fetchone()
        if existing:
            return int(existing["id"])

        cursor = conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (email, password_hash),
        )
        return int(cursor.lastrowid)


def ensure_pet(owner_id: int, pet: dict) -> None:
    with get_connection() as conn:
        existing = conn.execute(
            """
            SELECT id
            FROM pets
            WHERE owner_id = ? AND name = ? AND species = ?
            """,
            (owner_id, pet["name"], pet["species"]),
        ).fetchone()
        if existing:
            return

        conn.execute(
            """
            INSERT INTO pets (owner_id, name, species, breed, age_years, gender)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                owner_id,
                pet["name"],
                pet["species"],
                pet.get("breed"),
                pet.get("age_years"),
                pet.get("gender"),
            ),
        )


def seed_demo_data() -> None:
    init_db()
    for user in DEMO_USERS:
        owner_id = get_or_create_user(user["email"], user["password_hash"])
        for pet in user["pets"]:
            ensure_pet(owner_id, pet)


if __name__ == "__main__":
    seed_demo_data()
    print("Demo users and pets seeded successfully.")
