from skillaborator.db_collections import auth_service_instance
from flask.helpers import make_response
from requests import post, get
from flask_restful import Resource, abort, reqparse
from flask import Response


class LinkedInAuth(Resource):
    @staticmethod
    def __parse_post_args():
        # TODO: reusable parser?
        parser = reqparse.RequestParser()

        parser.add_argument('client_id', type=str, required=True, location="form")
        parser.add_argument('code', type=str, required=True, location="form")
        parser.add_argument('grant_type', type=str, required=True, location="form")
        parser.add_argument('client_secret', type=str, required=True, location="form")
        parser.add_argument('redirect_uri', type=str, required=True, location="form")
        return parser.parse_args(strict=True)

    @staticmethod
    def __parse_get_args() -> dict:
        parser = reqparse.RequestParser()

        parser.add_argument('token', type=str, required=True, help="User access token")

        return parser.parse_args(strict=True)

    @staticmethod
    def post():
        """
        Get access token
        """
        args = LinkedInAuth.__parse_post_args()
        args['redirect_uri'] = "http://localhost:4200"
        resp = post(url="https://www.linkedin.com/oauth/v2/accessToken", params=args, headers={"Content-Type": "x-www-form-urlencoded"})
        token = resp.json()['access_token']
        get_resp = get("https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))", headers={"Authorization": f"Bearer {token}"})
        email = get_resp.json()["elements"][0]["handle~"]["emailAddress"]
        next_skillaboration_start = auth_service_instance.save_login(email, token)
        return make_response({"email": email, "token": token, "nextSkillaborationStart": next_skillaboration_start}, 200)

    @staticmethod
    def get():
        """
            Get next skillaboration start
        """
        args = LinkedInAuth.__parse_get_args()
        token = args.get("token")
        next_skillaboration_start = auth_service_instance.get_next_skillaboration_start(token)
        if not next_skillaboration_start:
            abort(Response('No start time found', status=400))

        return make_response({"nextSkillaborationStart": next_skillaboration_start}, 200)




    
