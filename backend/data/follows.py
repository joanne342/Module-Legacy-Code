
from typing import List

from data.connection import db_cursor
from data.users import User

from psycopg2.errors import UniqueViolation


def follow(follower: User, followee: User):
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
            # Already following - treat as idempotent request.
            pass


def unfollow(follower: User, followee: User):
    """Remove the follow relationship between two users."""
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
    """Return the usernames this user follows."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT users.username
            FROM follows
            INNER JOIN users ON follows.followee = users.id
            WHERE follower = %s
            """,
            (follower.id,),
        )
        rows = cur.fetchall()
        return [row[0] for row in rows]


def get_inverse_followed_usernames(followee: User) -> List[str]:
    """Return the usernames of users following this user."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT users.username
            FROM follows
            INNER JOIN users ON follows.follower = users.id
            WHERE followee = %s
            """,
            (followee.id,),
        )
        rows = cur.fetchall()
        return [row[0] for row in rows]
