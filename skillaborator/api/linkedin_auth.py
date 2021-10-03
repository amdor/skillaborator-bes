from skillaborator.db_collections import auth_service, one_time_code_service
from flask.helpers import make_response
from requests import post, get
from flask_restful import Resource, reqparse


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
        auth_service.save_login(email, token)
        return make_response({"email": email, "token": token}, 200)
    
