
from typing import List

from data.connection import db_cursor
from data.users import User
from psycopg2.errors import UniqueViolation


def follow(follower: User, followee: User):
    """Create a follow relationship between two users."""
    with db_cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO follows (follower, followee)
                VALUES (%(follower_id)s, %(followee_id)s)
                """,
                {
                    "follower_id": follower.id,
                    "followee_id": followee.id,
                },
            )
        except UniqueViolation:
            # Following an already-followed user is idempotent.
            pass


def unfollow(follower: User, followee: User):
    """Remove a follow relationship between two users."""
    with db_cursor() as cur:
        cur.execute(
            """
            DELETE FROM follows
            WHERE follower = %(follower_id)s
              AND followee = %(followee_id)s
            """,
            {
                "follower_id": follower.id,
                "followee_id": followee.id,
            },
        )


def get_followed_usernames(follower: User) -> List[str]:
    """Return the usernames followed by this user."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT users.username
            FROM follows
            INNER JOIN users ON follows.followee = users.id
            WHERE follows.follower = %s
            """,
            (follower.id,),
        )
        return [row[0] for row in cur.fetchall()]


def get_inverse_followed_usernames(followee: User) -> List[str]:
    """Return the usernames of users following this user."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT users.username
            FROM follows
            INNER JOIN users ON follows.follower = users.id
            WHERE follows.followee = %s
            """,
            (followee.id,),
        )
        return [row[0] for row in cur.fetchall()]
