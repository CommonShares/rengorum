import json

from flask_restful import (
    Resource,
    abort,
    reqparse,
)
from mongoengine.errors import DoesNotExist

# Molekuls Imports
from mongodb.models import forums


parser = reqparse.RequestParser()
parser.add_argument("forum_id", type=str)
parser.add_argument("name", type=str)
parser.add_argument("description", type=str)
parser.add_argument("slug", type=str, default=None)


class ForumResource(Resource):

    def _get_forum_if_exists(self, forum_id: str):
        try:
            forum = forums.Forum.objects.get(id=forum_id)
            return forum
        except DoesNotExist:
            abort(404, message="Forum not found")

    def get(self, forum_id: str):
        return json.loads(self._get_forum_if_exists(forum_id).to_json())

    def delete(self, forum_id: str):
        forum = self._get_forum_if_exists(forum_id)
        forum.delete()
        return f"{forum_id} deleted", 204

    def put(self, forum_id: str):
        args = parser.parse_args()
        forum = self._get_forum_if_exists(forum_id)
        forum.name = args["name"]
        forum.description = args["description"]
        if args["slug"]:
            forum.slug = args["slug"]
        forum.save()
        return forum.to_mongo().to_dict(), 201


class ForumListResource(Resource):

    def get(self):
        forums_list = []
        for forum in forums.Forum.objects():
            forums_list.append(json.loads(forum.to_json()))
        return forums_list

    def post(self):
        args = parser.parse_args()
        forum = forums.Forum(
            name=args["name"],
            description=args["description"],
            slug=args["slug"],
        )
        forum.save()
        return forum.to_json(), 201
