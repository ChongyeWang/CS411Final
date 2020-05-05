from flask import Flask, Blueprint, render_template, abort, request, session, flash, Response
import db

profile_api = Blueprint('profile_api', __name__)


@profile_api.route('/profile', methods=['GET', 'POST'])
def profile():
    userEmail = session["email"]
    profileEmail = request.args.get("email").lower()

    db.mysql_cursor.execute(
        'SELECT email, first_name, last_name FROM Users.User WHERE email = %s', (profileEmail,))
    user_info = db.mysql_cursor.fetchall()

    if user_info is None:
        abort(404)  # Email is invalid

    db.mysql_cursor.execute(
        'SELECT rating, content, MovieName FROM Users.Review WHERE email = %s', (profileEmail,))
    user_reviews = db.mysql_cursor.fetchall()

    rating_num = len(user_reviews)
    rating_average = 0

    if rating_num > 0:
        rating_average = round(
            sum([i[0] for i in user_reviews]) / rating_num, 1)
    distance = 0  # 0 -> Your profile, infinity -> No friends in common, other -> distance of N friends
    if userEmail != profileEmail:
        shortestPathQuery = """
            MATCH p = shortestPath((u:User {email: $userEmail})-[:FriendsWith]->(v:User  {email: $profileEmail}))
            RETURN length(p) AS distance
        """

        result = db.neo4j_driver.session().run(shortestPathQuery, userEmail=userEmail,
                                               profileEmail=profileEmail).single()
        distance = result["distance"] if result is not None else "infinity"

    return render_template("profile.html", user_info=user_info, user_reviews=user_reviews, rating_num=rating_num, rating_average=rating_average, distance=distance)

# If a FriendsWith relation does not exist, it is added
@profile_api.route('/addFriend', methods=['POST'])
def addFriend():
    userEmail = session["email"]
    profileEmail = request.json["email"]

    query = """
        MATCH (u:User {email: $userEmail}), (v:User {email: $profileEmail})
        MERGE (u)-[:FriendsWith]->(v)
    """

    db.neo4j_driver.session().run(query, userEmail=userEmail, profileEmail=profileEmail)

    return Response()  # Return response 200 OK

# If a FriendsWith relation exists, it is deleted
@profile_api.route('/removeFriend', methods=['POST'])
def removeFriend():
    userEmail = session["email"]
    profileEmail = request.json["email"]

    query = """
        MATCH (u:User {email: $userEmail})-[r:FriendsWith]->(v:User {email: $profileEmail})
        DELETE r
    """

    db.neo4j_driver.session().run(query, userEmail=userEmail, profileEmail=profileEmail)

    return Response()  # Return response 200 OK
